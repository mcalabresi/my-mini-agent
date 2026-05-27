import asyncio
from typing import Union

from rich.console import Console
from rich.markdown import Markdown

from my_mini_agent.agent import Agent, load_agent
from my_mini_agent.utils.helper_functions import getTokenUtilization


async def main() -> None:
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

    # loading a predefined agent
    agent: Union[Agent, None] = await load_agent("Clive")
    # agent: Union[Agent, None] = load_agent("Clive")

    if agent is not None:
        # get the total tokens in context window
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
                response = await agent.chat(user_input)
                # get the total tokens used so far
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
    asyncio.run(main())
