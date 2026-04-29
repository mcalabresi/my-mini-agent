import getpass
from datetime import datetime
from pprint import pprint
from typing import Annotated

from rich.console import Console
from rich.markdown import Markdown

from agent import Agent
from helper_functions import (
    list_dir,
    message_debug,
    read_markdown_file,
    write_markdown_file,
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
        a: Annotated[int | float, "First number"],
        b: Annotated[int | float, "Second number"],
    ) -> dict[str, int | float]:
        """Add two numbers together."""
        return {"result": a + b}

    @agent.tool
    def multiply(
        a: Annotated[int | float, "First number"],
        b: Annotated[int | float, "Second number"],
    ) -> dict[str, int | float]:
        """Multiplies two numbers together."""
        return {"result": a * b}

    @agent.tool
    def secret() -> dict[str, str]:
        """Returns the secret key"""
        return {"result": "fluffy bunnies"}

    @agent.tool
    def concatenate(
        a: Annotated[int | str, "First item"], b: Annotated[int | str, "Second item"]
    ) -> dict[str, str]:
        """Concatenates two items."""
        return {"result": str(a) + str(b)}

    @agent.tool
    def get_orders(input: str | None = None) -> dict[str, str]:
        """
        Get the orders for a customer name. If input is None, get all orders.

        Args:
            input: the customer name
        """
        if isinstance(input, str):
            return {"result": f"{input} has ordered 3 pairs of blue socks"}
        return {
            "result": "Billy has ordered 3 pairs of blue socks, Jean has ordered 5 pairs of red socks"
        }

    # using an imported function as tool
    agent.tool(write_markdown_file)
    agent.tool(read_markdown_file)
    agent.tool(list_dir)

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
        skip_querying = False
        console.print("[green] You:[/green] ", end="")
        user_input = console.input()

        # one of these keywords trigger the end of the loop
        if user_input.strip().lower() in {"quit", "exit", "bye", "ciao", "q"}:
            console.print("[dim]Goodbye![/dim]")
            return
        # debug messages
        if user_input.strip().lower() in {"/dm", "/debug_messages"}:
            message_debug(console, agent.messages)
            skip_querying = True
        # debug tools
        if user_input.strip().lower() in {"/dt", "/debug_tools"}:
            pprint(agent.tools.get_schemas())
            skip_querying = True

        if not skip_querying:
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
