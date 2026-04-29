import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import requests

from tools import Tools


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

    def skill(self, skill_name: str) -> None:
        # Get current working directory
        cwd = os.getcwd()

        # Check if we're already in skills directory
        if cwd != "skills":
            # Change to agent-space directory
            try:
                os.chdir(f"skills/{skill_name}")
            except FileNotFoundError:
                raise RuntimeError(
                    f"Directory 'skills/{skill_name}' does not exist. Please create it first "
                    "or run from the correct location."
                )

        # Construct full filename with .md extension
        file_path = Path.cwd() / "SKILL.md"

        try:
            # Write the content to the file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

                def return_skill() -> str:
                    return content

                return_skill.__name__ = f"{skill_name}-skill"

                self.context(return_skill)
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {str(e)}")
        finally:
            # Always return to the original working directory
            os.chdir(cwd)

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
