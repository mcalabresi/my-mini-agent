# Basically here we are implementing a so-called workflow
# We use two agents. The first is a writer, the second is a critic
# The user inputs some ideas for a children story
# The writer writes a first draft, the critic writes his notes and passes them to the writer
# the writer makes the corrections and then saves the story in the agent-space


from rich.console import Console
from rich.markdown import Markdown

from agent import load_agent
from helper_functions import getTokenUtilization


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

    # loading a predefined agent
    writing_agent = load_agent("Clive")
    critic_agent = load_agent("Eddie")
    # agent: Union[Agent, None] = load_agent("Clive")

    if writing_agent is not None and critic_agent is not None:
        # get the total tokens in context window
        total_context_tokens = writing_agent.total_context_window_tokens

        console.print("[blue] Suggest a topic for a children story [/blue]")
        # user inputs the first message to the Agent
        console.print("[green] You:[/green] ", end="")
        user_input = console.input()

        write_first_draft_template = f"""
        Write a children story according to this input by the user:
        <user-input>{user_input}</user-input>\n
        do not memorize it yet as it will be scrutinized further.
        Respond just with the generated story without adding your notes and thoughts. Use 500 words max
        """

        # showing the spinner while the LLM thinks about what to say
        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            # we send here the message to the Agent
            first_draft = writing_agent.chat(write_first_draft_template)
            # get the total tokens used so far
            total_tokens = writing_agent.tokens_used

        # we show the agent response on the screen and we keep on with the loop
        console.print(f"[blue]{writing_agent.name}:[/blue] ", end="")
        # agent will respond as a Markdown Object (coming from rich console), we put this in a separate line
        markdown_response = Markdown(first_draft)
        console.print(markdown_response)

        critic_first_draft_template = f"""
        Review the following story and note down in a concise way what may be corrected:
        <first-draft>{first_draft}</first-draft>\n
        Be concise, give clear instruction on how to make it better, use bullet points.
        max 200 words.
        """

        # showing the spinner while the LLM thinks about what to say
        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            # we send here the message to the Agent
            critic_review = critic_agent.chat(critic_first_draft_template)
            # get the total tokens used so far
            total_tokens += writing_agent.tokens_used

        # we show the agent response on the screen and we keep on with the loop
        console.print(f"[orange1]{critic_agent.name}:[/orange1] ", end="")
        # agent will respond as a Markdown Object (coming from rich console), we put this in a separate line
        markdown_response = Markdown(critic_review)
        console.print(markdown_response)

        write_second_draft_template = f"""
        Modify your story according to this input by the editor:
        <editor-input>{critic_review}</editor-input>\n
        Respond just with the generated story without adding your notes and thoughts. Use 500 words max.
        When the story is ready memorize it.
        """

        # showing the spinner while the LLM thinks about what to say
        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            # we send here the message to the Agent
            final_draft = writing_agent.chat(write_second_draft_template)
            # get the total tokens used so far
            total_tokens += writing_agent.tokens_used

        # we show the agent response on the screen and we keep on with the loop
        console.print(f"[blue]{writing_agent.name}:[/blue] ", end="")
        # agent will respond as a Markdown Object (coming from rich console), we put this in a separate line
        markdown_response = Markdown(final_draft)
        console.print(markdown_response)

        # show info about token utilization
        console.print(getTokenUtilization(total_tokens, total_context_tokens))


if __name__ == "__main__":
    main()
