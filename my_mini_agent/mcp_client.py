import json
import os
from asyncio.exceptions import CancelledError
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters, Tool
from mcp.client.stdio import stdio_client

from my_mini_agent.mcp_catalog import mcp_servers
from my_mini_agent.utils.helper_functions import prYellow, truncate_long_args


class MCPClient:
    def __init__(self, mcp_server_name):
        # Initialize session and client objects
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.available_tools: list[Tool] | None = None
        self.name: str = mcp_server_name
        self.tool_names_list: list[str] = []
        self.api_key = os.getenv(f"{mcp_server_name.upper()}_API_KEY") or "NO_API_KEY"
        self.mcp_server_params = mcp_servers.get(self.name, None)
        if self.mcp_server_params is not None:
            key = f"{self.name.upper()}_API_KEY"
            self.mcp_server_params["env"] = {key: self.api_key}

    @classmethod
    def schema_for_mcp_tool(cls, mcp_tool: Tool | None) -> dict[str, Any] | None:
        if mcp_tool is not None:
            return {
                "type": "function",
                "function": {
                    "name": mcp_tool.name,
                    "description": mcp_tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": mcp_tool.inputSchema.get("properties"),
                    },
                },
            }
        return None

    async def connect(self) -> MCPClient | None:
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """

        # get the server_params from definition

        # is_python = server_script_path.endswith(".py")
        # is_js = server_script_path.endswith(".js")
        # if not (is_python or is_js):
        #     raise ValueError("Server script must be a .py or .js file")

        # if is_python:
        #     path = Path(server_script_path).resolve()
        #     server_params = StdioServerParameters(
        #         command="uv",
        #         args=["--directory", str(path.parent), "run", path.name],
        #         env=None,
        #     )
        # else:
        #     server_params = StdioServerParameters(
        #         command="node", args=[server_script_path], env=None
        #     )
        #

        print(f"Connecting with MCP server {self.name}")

        mcp_server_params = mcp_servers.get(self.name, None)

        if mcp_server_params is not None:
            try:
                server_params = StdioServerParameters(**mcp_server_params)

                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                self.stdio, self.write = stdio_transport
                self.session = await self.exit_stack.enter_async_context(
                    ClientSession(self.stdio, self.write)
                )

                await self.session.initialize()

                # List available tools
                response = await self.session.list_tools()
                tools = response.tools
                self.available_tools = tools
                self.tool_names_list = [tool.name for tool in tools]
                print(
                    f"\nConnected to server {self.name} with tools:",
                    self.tool_names_list,
                )
                return self
            except Exception as e:
                print(e)
                print(f"Cannot connect with MCP server {self.name}")

        return None

    async def execute(self, tool_call: dict[str, Any]) -> dict[str, Any]:
        """function to run the tool the LLM chose

        :param tool_call: dict[str, Any] - the info about what tool we need to call and with which parameters
        :return: the result of the tool call in a format that LLM can use to give a response
        """
        fn_payload = tool_call.get("function") or {}
        fn_name = fn_payload.get("name")
        # print("\nI am inside Execute\n")
        if fn_name not in self.tool_names_list:
            return {
                "result": f"function {fn_name} is not provided by {self.name} MCP server"
            }

        try:
            args = json.loads(fn_payload.get("arguments") or "{}")
            # check if an argument has been called with 'None'
            for k, v in args.items():
                if v == "None":
                    args[k] = None
            prYellow(
                f">> Invoking MCP function {fn_name} with arguments {truncate_long_args(**args)} <<"
            )
            if self.session is not None:
                result = await self.session.call_tool(fn_name, args)
                # print("\n\n RESULT OF THE CALL \n")
                # print(result)
                return result if isinstance(result, dict) else {"result": str(result)}
                # add a proper logger here
            return {"result": "The MCP session is down, retry later"}
        except KeyboardInterrupt:
            raise
        except Exception as e:
            return {"error": str(e)}

    async def execute_tool(self, tool_name: str, tool_args) -> Any:
        if self.session is not None:
            result = await self.session.call_tool(tool_name, tool_args)
            return result.content
        return None

    async def disconnect(self):
        """Clean up resources"""
        print(f"closing connection with MCP server {self.name}")
        if self.session is not None:
            try:
                await self.exit_stack.aclose()
            except CancelledError as e:
                print(f"CancelledError: {e}")
                print("Something went wrong during disconnection")
            except RuntimeError as rte:
                print(f"RuntimeError: {rte}")
            else:
                print(f"closed correctly the connection with {self.name}")
