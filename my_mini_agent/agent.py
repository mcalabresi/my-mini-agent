import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Union

import aiofiles
import httpx
from dotenv import load_dotenv

from my_mini_agent import context_catalog, tool_catalog
from my_mini_agent.agents_catalog import available_agents
from my_mini_agent.mcp_client import MCPClient
from my_mini_agent.tools import Tools
from my_mini_agent.utils.helper_functions import (
    get_local_model_context_window,
    list_format,
    message_debug,
    prYellow,
)
from my_mini_agent.utils.helper_skills import extract_skills_frontmatters


@dataclass
class Agent:
    # info about connection to the model
    model: str = "qwen3.5"
    base_url: str = "http://127.0.0.1:1234/v1"
    api_key: str = field(default="NO_API_KEY", repr=False)
    tools: Tools = field(default_factory=Tools)
    # info about behaviour of the LLM
    name: str = field(default="my_mini_agent")
    system_prompt: str = "You are a helpful assistant"
    # this syntax below means that we will pass as values "functions" that take no argument and return a string
    dynamic_context_functions: dict[str, Callable[[], str]] = field(
        default_factory=dict
    )
    messages: list[dict[str, Any]] = field(default_factory=list)
    total_context_window_tokens: int = 0
    tokens_used: int = 0
    mcp_clients: list[MCPClient] = field(default_factory=list)
    mcp_tools_schemas: list[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        load_dotenv()
        self.model = os.getenv("MODEL_NAME") or ""
        self.api_key = os.getenv("MODEL_API_KEY") or "NO_API_KEY"
        # make sure there's  no trailing '/' at the end of url
        self.base_url = (os.getenv("MODEL_API_BASE_URL") or self.base_url).rstrip("/")
        if "127.0.0.1" in self.base_url:
            self.total_context_window_tokens = get_local_model_context_window(
                self.model
            )

    def add_tool(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """ "Register a tool
        :param func: Callable - the function we want to register as tool
        :return: Callable - the function that we passed as input
        """
        return self.tools.register(func)

    def add_mcp_tool(self, tool_name, mcp_client: MCPClient):
        if (
            mcp_client is not None
            and mcp_client.available_tools
            and len(mcp_client.available_tools) > 0
            and tool_name in mcp_client.tool_names_list
        ):
            tool = [t for t in mcp_client.available_tools if t.name == tool_name][0]
            schema = MCPClient.schema_for_mcp_tool(tool)
            self.mcp_tools_schemas.append(schema)

    def add_all_mcp_tools(self, mcp_client: MCPClient):
        if (
            mcp_client is not None
            and mcp_client.available_tools
            and len(mcp_client.available_tools) > 0
        ):
            for tool in mcp_client.available_tools:
                schema = MCPClient.schema_for_mcp_tool(tool)
                self.mcp_tools_schemas.append(schema)

    def add_context_function(self, func: Callable[[], str]) -> Callable[[], str]:
        """Register a context function
        :param func: Callable - a function that we want to register, this should return a string
        :return: Callable - the function that we passed in input
        """
        # contexts is a dictionary containing functions, the keys are the function names
        self.dynamic_context_functions[func.__name__] = func
        return func

    async def add_skill(self, skill_name: str) -> None:
        """Add a skill to the context

        :skill_name: str - The name of the skill.

        Note: Skills should be set in skills directory.
        Each skill should have its folder with name skill_name.
        Inside this folder we need a file named SKILL.md
        """
        if not skill_name:
            print("empty skillname")
            return
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

            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()

                def return_skill() -> str:
                    return content

                return_skill.__name__ = f"{skill_name}-skill"

                self.add_context_function(return_skill)
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {str(e)}")
        finally:
            # Always return to the original working directory
            os.chdir(cwd)

    async def define_skillset(self, skillset: list[str]):
        available_skills_text = await extract_skills_frontmatters("skills", skillset)

        def available_skills() -> str:
            instructions = "Here are all the available skills. If you need to use one of them call tool `read_skill` with parameter skill_name set to skill `name` \n\n"
            return instructions + available_skills_text

        self.add_context_function(available_skills)

    def prepare_system_context(self) -> list[dict[str, Any]]:
        """method that prepares a list of context info for the model
        :return: list[dict[str,Any]] - a list with the context info in a format liked by OpenAI api
        """
        # getting the context from the context functions we registered and rendering it in a xml style
        context_content = "<context>\n"
        # adding agent name just for fun
        context_content += f"<agent-name>{self.name}</agent-name>\n"
        for ctx_func_name, ctx_func in self.dynamic_context_functions.items():
            context_content += f"<{ctx_func_name}>{ctx_func()}</{ctx_func_name}>\n"
        context_content += "</context>"

        # structuring our context and our system prompt specified at creation of the Agent
        # we will add it to messages and send all of this
        context_list: list[dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": context_content},
        ]
        return context_list

    async def chat(self, user_message: str) -> str:
        """Chat with the Agent
        :param user_message: str - the input from the user
        :return: str - the response message from the Agent

        Inner working:
            If the user message starts with a slash character it starts a command.
            Otherwise it will perform an API call to the LLM
            We send a lot of info to the LLM, not just the last user message
            but the whole list of messages in our conversation so far.

            We send the system prompt to give more context.
            (We call all the registered context functions and add them here)

            We add also the list of tool schemas so that the LLM can invoke them

            When we receive a valid response we add it to the messages so that,
            in further calls, the model remembers of what it said just before.

            If an LLM invokes a tool we execute it and call again the LLM with the response as message.
            The LLM may call on its own multiple tools one at a time without user intervention.

        """
        # first of all let's consider the case of slash-commands
        # these will not trigger any call to the LLM but are used for debug or modifying the context / tools used
        if user_message.startswith("/"):
            # we execute the slash command and return, no call to the LLM this time
            return self.slash_commands(user_message)

        # take the message from the user and append it to messages,
        # remember we don't just send the user_message but the whole list of messages so far
        self.messages.append({"role": "user", "content": user_message})

        # structuring our context and our system prompt specified at creation of the Agent
        # we will add it to messages and send all of this
        # this should be memoized
        system_context: list[dict[str, Any]] = self.prepare_system_context()

        # IMPORTANT THIS IS THE AGENT LOOP (RE-ACT Reason and act)
        # we introduce this loop to make sure that each time we have a tool call
        # to perform we call back the API of the model .
        # Improvement idea: We can do also a max calls check here to avoid infinite loop
        while True:
            api_kwargs = {
                "model": self.model,
                "messages": system_context + self.messages,
            }

            tool_schemas = self.tools.get_schemas()

            if tool_schemas:
                api_kwargs["tools"] = tool_schemas + self.mcp_tools_schemas

            # open-ai style API endpoint
            url = f"{self.base_url}/chat/completions"
            # as usual you need to pass an API Key and you are going to send json data as post
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            # print(" API KWARGS :", api_kwargs)
            # here we make our post request, note that we send the whole list of messages, not just the last one
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    url,
                    headers=headers,
                    json=api_kwargs,
                    timeout=3000,
                )
                # print(r.text)
                # if there's an error raise it
                r.raise_for_status()
                # get the data ( parse the json response from the LLM )
                data = r.json()
                # print(f"{data=}")
                choices = data.get("choices")
                usage = data.get("usage")
                total_tokens = usage.get("total_tokens")
                # update the token count
                self.tokens_used = total_tokens
                # api should provide choices
                if not choices:
                    raise RuntimeError("Model response missing choices")

                # the response is in the first choice
                message = choices[0].get("message")

                if message is None:
                    # LLM responded nothing, is it an error?
                    raise RuntimeError("Model response missing message")

                # extracting the eventual tool_calls from LLM
                tool_calls = message.get("tool_calls") or []

                # we create a list of dicts to specify the tool calls
                formatted_tool_calls_list = [
                    {
                        "id": tc.get("id"),
                        "type": tc.get("type"),
                        "function": {
                            "name": (tc.get("function") or {}).get("name"),
                            "arguments": (tc.get("function") or {}).get("arguments"),
                        },
                    }
                    for tc in tool_calls
                ]

                # we append it to the messages to keep track
                self.messages.append(
                    {
                        "role": "assistant",
                        "content": message.get("content"),
                        "tool_calls": formatted_tool_calls_list,
                    }
                )

                # finally we extract the agent's response
                agent_response = message.get("content") or ""

                # Case in which there is no tool call, the LLM just responds some text
                if not tool_calls or len(tool_calls) == 0:
                    return agent_response

                # Case in which there is a list of tool calls
                for tool_call in tool_calls:
                    # we execute each tool call and append the result into messages
                    # print("\n I AM INTO TOOL CALL \n")
                    # print(f"{tool_call=}")
                    fn = tool_call.get("function")
                    fn_name = fn.get("name")
                    # is it an MCP call?
                    is_MCP_call = False
                    for mcp_client in self.mcp_clients:
                        if fn_name in mcp_client.tool_names_list:
                            is_MCP_call = True
                            result = await mcp_client.execute(tool_call)
                            self.messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call.get("id"),
                                    "content": json.dumps(result),
                                }
                            )
                    if not is_MCP_call:
                        if fn_name == "read_skill":
                            fn_payload = tool_call.get("function") or {}
                            args = json.loads(fn_payload.get("arguments") or "{}")
                            skill_name = args.get("skill_name", "")
                            prYellow(
                                f">> Invoking function {fn_name} with argument {skill_name} <<"
                            )
                            result = await self.add_skill(skill_name)
                        else:
                            result = self.tools.execute(tool_call)
                        self.messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.get("id"),
                                "content": json.dumps(result),
                            }
                        )
                    # notice we don't return, after all tools are called we will
                    # call again the model with the new message list containing the result
                    # of the tool calls.

    def slash_commands(self, slash_command: str) -> str:
        """manages slash commands

        :param command: str - the slash command we give to the agent
        :return: the output of the slash command in md format (as said by the Agent)"""
        # debug messages
        if slash_command.strip().lower() in {"/dm", "/debug_messages"}:
            return message_debug(self.messages)

        # debug tools
        elif slash_command.strip().lower() in {"/dt", "/debug_tools"}:
            total_schemas = self.tools.get_schemas() + self.mcp_tools_schemas
            return f"These are all my tool schemas: \n\n {list_format(total_schemas)}"

        # debug messages
        elif slash_command.strip().lower() in {"/dc", "/debug_context"}:
            return f"Here is my system context: \n\n{list_format(self.prepare_system_context())}"

        # deletes the previous messages. The context will be recreated in next turn
        elif slash_command.strip().lower() == "/new":
            self.messages = []
            return "Let's start a new topic with fresh memory!"

        elif slash_command.strip().startswith("/terminal"):
            command_list = slash_command.split()[1:]
            print(" ".join(command_list))
            os.system(" ".join(command_list))
            return f"Called terminal command: {' '.join(command_list)}"

        return f"I don't know this command:  {slash_command}"


async def load_agent(agent_name: str) -> Union[Agent, None]:
    found_agents = [a for a in available_agents if a.get("name") == agent_name]
    if len(found_agents) == 0:
        print(f"Agent named {agent_name} not found!")
        return None

    agent_data = found_agents[0]
    new_agent = Agent(
        name=agent_data.get("name", "agent"),
        system_prompt=agent_data.get("system_prompt", "You are a useful assistant"),
    )
    agent_contexts = agent_data.get("context", [])
    for c in agent_contexts:
        context_function = getattr(context_catalog, c)
        new_agent.add_context_function(context_function)

    agent_skills = agent_data.get("skills", [])
    await new_agent.define_skillset(agent_skills)
    # for skill in agent_skills:
    #     new_agent.add_skill(skill)

    agent_tools = agent_data.get("tools", [])
    agent_tools.append("read_skill")
    for tool in agent_tools:
        tool_function = getattr(tool_catalog, tool)
        new_agent.add_tool(tool_function)

    return new_agent


"""
Note to self. it's better that the agent connects and disconnects the mcp servers as there is just one AsyncExitStack

from contextlib import AsyncExitStack

self.exit_stack = AsyncExitStack()
streams = await self.exit_stack.enter_async_context(sse_client())
session = await self.exit_stack.enter_async_context(session_client())

# Later, cleanup
await self.exit_stack.aclose()
"""
