from rich.console import Console
from rich.markdown import Markdown

from agent import Agent
from context_catalog import (
    current_date_time,
    user_context,
)
from helper_functions import getTokenUtilization
from tool_catalog import (
    add_link_to_index,
    edit_note,
    list_notes,
    read_note,
    write_note,
)


def main() -> None:
    """Main for MyMiniAgent"""
    # invoke rich Console, we are going to need it for displaying nice stuff in the terminal
    console = Console()

    # we've got a logo to show just for fun (notice it's a raw string)
    my_mini_agent_logo = r"""
    __  ___     __  ____      _ ___                __
   /  |/  /_ __/  |/  (_)__  (_) _ |___ ____ ___  / /_
  / /|_/ / // / /|_/ / / _ \/ / __ / _ `/ -_) _ \/ __/
 /_/  /_/\_, /_/  /_/_/_//_/_/_/ |_\_, /\__/_//_/\__/
        /___/                     /___/
    """

    console.print(f"[blue]{my_mini_agent_logo}[/blue]")

    ##############################################################
    #                      Agent definition                      #
    ##############################################################

    # invoke the agent
    # model_name = "google/gemma-4-e4b"
    # agent = Agent(model="qwen/qwen3.5-9b")
    agent = Agent(name="Bong")

    total_context_tokens = agent.total_context_window_tokens

    # let's modify the system prompt
    agent.system_prompt = "You are a Bong, a reticent assistant, you answer briefly with as less words as possible. You use simple words and you return only your final output, not your internal thoughts"

    # let's define a context function
    # we can use the decorator that we defined as agent method if we want to define it here
    # @agent.context_function
    # def current_date_time() -> str:
    #     return (
    #         f"Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    #     )

    # or we import the function and add the context like this
    agent.add_context_function(current_date_time)
    agent.add_context_function(user_context)
    # agent.context(my_files)
    agent.add_skill("obsidian-markdown-lite")
    agent.add_skill("long-term-memory")
    # agent.context(obsidian_writer_skill)

    # example of defining a tool and registering on the fly
    # @agent.add_tool
    # def add(
    #     a: Annotated[int | float, "First number"],
    #     b: Annotated[int | float, "Second number"],
    # ) -> dict[str, int | float]:
    #     """Add two numbers together."""
    #     return {"result": a + b}

    # otherwise to import it from external module
    # using an imported function as tool
    agent.add_tool(write_note)
    agent.add_tool(read_note)
    agent.add_tool(list_notes)
    agent.add_tool(add_link_to_index)
    agent.add_tool(edit_note)

    # agent = load_agent("Bong")
    if agent is not None:
        total_context_tokens = agent.total_context_window_tokens
        while True:
            # chat loop
            # user inputs the first message to the Agent
            console.print("[green] You:[/green] ", end="")
            user_input = console.input()

            # one of these keywords trigger the end of the loop
            if user_input.strip().lower() in {"quit", "exit", "bye", "ciao", "q"}:
                console.print("[dim]Goodbye![/dim]")
                return

            # showing the spinner while the LLM thinks about what to say
            with console.status("[dim]Thinking...[/dim]", spinner="dots"):
                # we send here the message to the Agent
                response = agent.chat(user_input)
                total_tokens = agent.tokens_used

            # we show the agent response on the screen and we keep on with the loop
            console.print(f"[blue]{agent.name}:[/blue] ", end="")
            # agent will respond as a Markdown Object (coming from rich console), we put this in a separate line
            if not user_input.startswith("/"):
                markdown_response = Markdown(response)
                console.print(markdown_response)
            else:
                console.print(response)

            # show info about token utilization
            console.print(getTokenUtilization(total_tokens, total_context_tokens))


if __name__ == "__main__":
    main()
