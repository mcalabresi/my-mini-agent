import getpass
import inspect
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated, Any, Callable, Final, Union, get_args, get_origin

import requests
from rich.console import Console
from rich.markdown import Markdown


@dataclass
class Tools:
    """ "This class manages tools for the agent
    One of its duties will be to extract the info of the functions
    we pass and create a schema that the LLM can use
    """

    # tool schema attribute,
    TOOL_SCHEMA_ATTR: Final[str] = "__tool_schema__"
    # here is a dict of functions (tools), this represents the group of tools that the agent is allowed to use
    tools: dict[str, Callable[..., Any]] = field(default_factory=dict)

    @staticmethod
    def _annotation_to_schema(annotation: Any) -> dict[str, Any]:
        """converts annotation to JSON schema fragment
         (by annotation in Python we mean the types involved with the function (arguments and return type))

        :param annotation: Any - the annotation (of the function tool) that we want to convert to schema
        :return: dic[str, Any] - the schema of the annotation
        """
        # Notice that the types we return in the schema look like TypeScript / JavaScript types

        # default schema
        schema: dict[str, Any] = {"type": "string"}
        # description of the tool function
        description: str | None = None

        # gets the origin of the provided annotation
        origin = get_origin(annotation)

        if origin is Annotated:
            # if the origin is Annotated get the base type and call again the method on the base type
            base_type, *meta = get_args(annotation)
            schema = Tools._annotation_to_schema(base_type)
            if meta:
                description = str(meta[0])
        elif annotation in (int, float):
            schema = {"type": "number"}
        elif annotation is bool:
            schema = {"type": "boolean"}
        elif annotation is str:
            schema = {"type": "string"}
        elif annotation is dict:
            schema = {"type": "object"}
        elif annotation is list:
            schema = {"type": "array"}
        # from now on we check the origins
        elif origin is list:
            schema = {
                "type": "array",
                "items": Tools._annotation_to_schema(get_args(annotation)[0]),
            }
        elif origin is dict:
            schema = {"type": "object"}
        # if the origin is a Union get the first type
        elif origin is Union:
            any_of = [
                Tools._annotation_to_schema(arg)
                for arg in get_args(annotation)
                if arg is not type(None)
            ]
            if any_of:
                schema = any_of[0]

        # if there is a description we will add it to the schema
        if description:
            schema["description"] = description

        return schema

    @classmethod
    def schema_for_callable(cls, func: Callable[..., Any]) -> dict[str, Any]:
        """Inspects a function and returns the schema in the format that LLM like for a tool

        :param cls: - the class
        :param func: Callable[..., Any] - a function with an arbitrary number of parameters of any type
        :return: dict[str, Any] - the schema of the provided function tool
        """
        sig = inspect.signature(func)
        annotations = inspect.get_annotations(func)

        parameters: dict[str, Any] = {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

        for name, param in sig.parameters.items():
            annotation = annotations.get(name, inspect.Parameter.empty)

            if annotation is inspect.Parameter.empty:
                # could be an error to be raised
                continue

            parameters["properties"][name] = cls._annotation_to_schema(annotation)

            # if there is no default value associated to this parameter it means that it is required
            if param.default is param.empty:
                parameters["required"].append(name)

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__ or "No description provided",
                "parameters": parameters,
                "strict": True,
            },
        }

    def get_schemas(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for fn in self.tools.values():
            s = getattr(fn, self.TOOL_SCHEMA_ATTR, None)
            if s is not None:
                out.append(s)
        return out

    def register(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """decorator to register a tool

        :param func: Callable[..., Any] - the function we want to become a tool
        :return: the original function
        """
        if getattr(func, self.TOOL_SCHEMA_ATTR, None) is None:
            setattr(func, self.TOOL_SCHEMA_ATTR, self.schema_for_callable(func))
        self.tools[func.__name__] = func
        return func

    def execute(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        """function to run the tool the LLM chose

        :param tool_call: dict[str, Any] - the info about what tool we need to call and with which parameters
        :return: the result of the tool call in a format that LLM can use to give a response
        """
        fn_payload = tool_call.get("function") or {}
        fn_name = fn_payload.get("name")
        fn = self.tools.get(fn_name) if fn_name else None

        if not fn:
            return {"error": f"Tool '{fn_name}' not found"}

        try:
            args = json.loads(fn_payload.get("arguments") or "{}")
            result = fn(**args)
            return result if isinstance(result, dict) else {"result": result}
            # add a proper logger here
        except KeyboardInterrupt:
            raise
        except Exception as e:
            return {"error": str(e)}


@dataclass
class Agent:
    # info about connection to the model
    model: str = "qwen3.5"
    base_url: str = "http://127.0.0.1:1234/v1"
    api_key: str = field(default="NO_API_KEY", repr=False)
    tools: Tools = field(default_factory=Tools)
    # info about behaviour of the LLM
    system_prompt: str = "You are a helpful assistant"
    # this syntax below means that we will pass as values "functions" that take no argument and return a string
    contexts: dict[str, Callable[[], str]] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        # make sure there's  no trailing '/' at the end of url
        self.base_url = self.base_url.rstrip("/")

    def tool(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """ "Decorator to register tools
        :param func: Callable - the function we want to register as tool
        :return: Callable - the function that we passed as input
        """
        return self.tools.register(func)

    def context(self, func: Callable[[], str]) -> Callable[[], str]:
        """Decorator to register context functions
        :param func: Callable - a function that we want to register, this should return a string
        :return: Callable - the function that we passed in input
        """
        # contexts is a dictionary containing functions, the keys are the function names
        self.contexts[func.__name__] = func
        return func

    def prepare_context(self) -> list[dict[str, Any]]:
        """method that prepares a list of context info for the model
        :return: list[dict[str,Any]] - a list with the context info in a format liked by OpenAI api
        """
        # getting the context from the context functions we registered and rendering it in a xml style
        context_content = "<context>\n"
        for ctx_func_name, ctx_func in self.contexts.items():
            context_content += f"<{ctx_func_name}>{ctx_func()}</{ctx_func_name}>\n"
        context_content += "</context>"

        # structuring our context and our system prompt specified at creation of the Agent
        # we will add it to messages and send all of this
        context_list: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": context_content},
        ]
        return context_list

    def chat(self, user_message: str) -> str:
        """This functions allows chatting with the Agent
        :param user_message: str - the input from the user
        :return: str - the response message from the Agent

        Inner working:
           In a nutshell it's an API call to the LLM at this stage but
            We send a lot of info to the model, not just the last user message
            but the whole list of messages in our conversation so far
            We send the system prompt to give more context. (We call all the registered context functions and add them here)
            When we receive a valid response we add it to the messages so that in further calls the model remembers of what it said just before.

        """
        # take the message from the user and append it to messages
        self.messages.append({"role": "user", "content": user_message})

        # structuring our context and our system prompt specified at creation of the Agent
        # we will add it to messages and send all of this
        prefix: list[dict[str, Any]] = self.prepare_context()

        # we introduce this loop to make sure each time we have a tool call
        # to perform we call back the API of the model . We can do also a max calls check here
        # to avoid infinite loop
        while True:
            api_kwargs = {"model": self.model, "messages": prefix + self.messages}

            tool_schemas = self.tools.get_schemas()
            if tool_schemas:
                api_kwargs["tools"] = tool_schemas

            # open-ai style API endpoint
            url = f"{self.base_url}/chat/completions"
            # as usual you need to pass an API Key and you are going to send json data as post
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            # here we make our post request, note that we send the whole list of messages, not just the last one
            r = requests.post(
                url,
                headers=headers,
                json=api_kwargs,
                timeout=300,
            )

            # if there's an error raise it
            r.raise_for_status()
            # get the data ( parse the json response )
            data = r.json()
            # print(f"{data=}")
            choices = data.get("choices")

            # api should provide choices
            if not choices:
                raise RuntimeError("Model response missing choices")

            # the response is in first choice
            message = choices[0].get("message")

            if message is None:
                # LLM responded nothing, is it an error?
                raise RuntimeError("Model response missing message")

            # extracting the eventual tool_calls from LLM
            tool_calls = message.get("tool_calls") or []

            # we append it to the messages
            self.messages.append(
                {
                    "role": "assistant",
                    "content": message.get("content"),
                    "tool_calls": [
                        {
                            "id": tc.get("id"),
                            "type": tc.get("type"),
                            "function": {
                                "name": (tc.get("function") or {}).get("name"),
                                "arguments": (tc.get("function") or {}).get(
                                    "arguments"
                                ),
                            },
                        }
                        for tc in tool_calls
                    ],
                }
            )

            # finally we extract the agent's response
            agent_response = message.get("content") or ""

            if not tool_calls or len(tool_calls) == 0:
                return agent_response

            for tool_call in tool_calls:
                result = self.tools.execute(tool_call)
                self.messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "content": json.dumps(result),
                    }
                )


def main() -> None:
    """Main for MyMiniAgent"""
    # invoke rich Console, we are going to need it for displaying nice stuff in the terminal
    console = Console()

    # invoke the agent
    agent = Agent(model="qwen/qwen3.5-9b")

    # let's define a context function
    # and let's use the decorator that we defined as agent method

    @agent.context
    def current_date_time() -> str:
        return (
            f"Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

    @agent.context
    def user_context() -> str:
        return f"Current user: {getpass.getuser()}\n"

    @agent.tool
    def add(
        a: Annotated[int, "First number"], b: Annotated[int, "Second number"]
    ) -> dict[str, int]:
        """Add two numbers together."""
        print("invoking tool add")
        return {"result": a + b}

    @agent.tool
    def multiply(
        a: Annotated[int, "First number"], b: Annotated[int, "Second number"]
    ) -> dict[str, int]:
        """Multiplies two numbers together."""
        print("invoking tool multiply")
        return {"result": a * b}

    @agent.tool
    def secret() -> dict[str, str]:
        """Returns the secret key"""
        print("invoking tool secret")
        return {"result": "fluffy bunnies"}

    # we've got a logo to show just for fun (notice it's a raw string)
    my_mini_agent_logo = r"""
    __  ___     __  ____      _ ___                __
   /  |/  /_ __/  |/  (_)__  (_) _ |___ ____ ___  / /_
  / /|_/ / // / /|_/ / / _ \/ / __ / _ `/ -_) _ \/ __/
 /_/  /_/\_, /_/  /_/_/_//_/_/_/ |_\_, /\__/_//_/\__/
        /___/                     /___/
    """

    console.print(f"[blue]{my_mini_agent_logo}[/blue]")

    while True:
        # chat loop
        # user inputs the first message to the Agent
        console.print("[green] You:[/green] ", end="")
        user_input = console.input()
        # one of these keywords trigger the end of the loop
        if user_input.strip().lower() in {"quit", "exit", "bye", "ciao"}:
            console.print("[dim]Goodbye![/dim]")
            return

        # showing the spinner while the LLM thinks about what to say
        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            # we send here the message to the Agent
            response = agent.chat(user_input)

        # we've got the response! Probably it's markdown so let's format it correctly
        markdown_response = Markdown(response)

        # we show this on the screen and we keep on with the loop
        console.print("[blue]Agent:[/blue] ", end="")
        console.print(markdown_response)


if __name__ == "__main__":
    main()
