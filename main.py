from pprint import pprint

from rich.console import Console
from rich.markdown import Markdown

from agent import Agent
from context_catalog import (
    current_date_time,
    my_files,
    obsidian_writer_skill,
    user_context,
)
from helper_functions import message_debug
from tool_catalog import list_dir, read_markdown_file, write_markdown_file


def main() -> None:
    """Main for MyMiniAgent"""
    # invoke rich Console, we are going to need it for displaying nice stuff in the terminal
    console = Console()

    # invoke the agent
    agent = Agent(model="qwen/qwen3.5-9b")

    # let's define a context function

    # we can use the decorator that we defined as agent method if we want to define it here
    # @agent.context
    # def current_date_time() -> str:
    #     return (
    #         f"Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    #     )

    # or we import the function and add the context like this
    agent.context(current_date_time)
    agent.context(user_context)
    agent.context(my_files)
    agent.skill("obsidian-markdown-lite")
    # agent.context(obsidian_writer_skill)

    # example of defining a tool and registering on the fly
    # @agent.tool
    # def add(
    #     a: Annotated[int | float, "First number"],
    #     b: Annotated[int | float, "Second number"],
    # ) -> dict[str, int | float]:
    #     """Add two numbers together."""
    #     return {"result": a + b}

    # otherwise to import it from external module
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

        if user_input.strip().lower() in {"/dc", "/debug_context"}:
            pprint(agent.prepare_context())
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
