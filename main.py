import getpass
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

import requests
from rich.console import Console
from rich.markdown import Markdown


@dataclass
class Agent:
    # info about connection to the model
    model: str = "qwen3.5"
    base_url: str = "http://127.0.0.1:1234/v1"
    api_key: str = field(default="NO_API_KEY", repr=False)

    # info about behaviour of the LLM
    system_prompt: str = "You are a helpful assistant"
    # this syntax below means that we will pass as values "functions" that take no argument and return a string
    contexts: dict[str, Callable[[], str]] = field(default_factory=dict)
    messages: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        # make sure there's  no trailing '/' at the end of url
        self.base_url = self.base_url.rstrip("/")

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
        context_list: list[dict[str, Any]] = self.prepare_context()

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
            json={"model": self.model, "messages": context_list + self.messages},
            timeout=300,
        )

        # if there's an error raise it
        r.raise_for_status()
        # get the data ( parse the json response )
        data = r.json()
        print(f"{data=}")
        choices = data.get("choices")

        # api should provide choices
        if not choices:
            raise RuntimeError("Model response missing choices")

        # the response is in first choice
        message = choices[0].get("message")

        if message is None:
            # LLM responded nothing, is it an error?
            raise RuntimeError("Model response missing message")

        # finally we extract the agent's response
        agent_response = message.get("content") or ""
        # we append it to the messages
        self.messages.append({"role": "assistant", "content": agent_response})
        # and we return it as output
        return agent_response


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
