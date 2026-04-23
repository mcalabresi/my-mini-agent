from dataclasses import dataclass, field
from typing import Any

import requests
from rich.console import Console
from rich.markdown import Markdown


@dataclass
class Agent:
    model: str = "qwen3.5"
    base_url: str = "http://127.0.0.1:1234/v1"
    api_key: str = field(default="NO_API_KEY", repr=False)
    messages: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        r = requests.post(
            url,
            headers=headers,
            json={"model": self.model, "messages": self.messages},
            timeout=300,
        )

        r.raise_for_status()
        data = r.json()
        choices = data.get("choices")

        if not choices:
            raise RuntimeError("Model response missing choices")

        message = choices[0].get("message")

        if message is None:
            raise RuntimeError("Model response missing message")

        agent_response = message.get("content") or ""
        self.messages.append({"role": "assistant", "content": agent_response})
        return agent_response


def main() -> None:
    agent = Agent(model="qwen/qwen3.5-9b")
    console = Console()

    my_mini_agent_logo = r"""
    __  ___     __  ____      _ ___                __
   /  |/  /_ __/  |/  (_)__  (_) _ |___ ____ ___  / /_
  / /|_/ / // / /|_/ / / _ \/ / __ / _ `/ -_) _ \/ __/
 /_/  /_/\_, /_/  /_/_/_//_/_/_/ |_\_, /\__/_//_/\__/
        /___/                     /___/
    """

    console.print(f"[blue]{my_mini_agent_logo}[/blue]")
    while True:
        console.print("[green] You:[/green] ", end="")
        user_input = console.input()

        if user_input.strip().lower() in {"quit", "exit", "bye", "ciao"}:
            console.print("[dim]Goodbye![/dim]")
            return

        with console.status("[dim]Thinking...[/dim]", spinner="dots"):
            response = agent.chat(user_input)

        markdown_response = Markdown(response)
        console.print("[blue]Agent:[/blue] ", end="")
        console.print(markdown_response)
        # console.print(f"[blue]Assistant:[/blue] {markdown_response}")


if __name__ == "__main__":
    main()
