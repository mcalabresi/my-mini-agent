"""Module containing helper functions"""

import os
from pathlib import Path
from typing import Annotated, Any

from rich.console import Console


def message_debug(console: Console, messages: list[dict[str, Any]]) -> None:
    """ "Show nicely the list of messages so far
    :param console: Console - rich console
    :param messages: list[dict[str,Any]] - list of messages"""
    for message in messages:
        # print(f"{message=}")
        sender = message.get("role", "user")
        who_sent_text = ""
        if sender == "user":
            txt = "User".ljust(10, "-") + ">"
            who_sent_text = f"[green]{txt}[/green]"
        elif sender == "assistant":
            txt = "Agent".ljust(10, "-") + ">"
            who_sent_text = f"[blue]{txt}[/blue]"
        elif sender == "tool":
            txt = "Tool".ljust(10, "-") + ">"
            who_sent_text = f"[orange1]{txt}[/orange1]"

        console.print(f"| {who_sent_text} ", end="")
        content = message.get("content", "").strip()
        if len(content) > 0:
            console.print(content)
        if (tool_calls := message.get("tool_calls", [])) and len(tool_calls) > 0:
            for tc in tool_calls:
                fn = tc.get("function", {})
                console.print(
                    f"Calling tool function '{fn.get('name')}' with arguments {fn.get('arguments')}"
                )


def write_markdown_file(
    file_name: Annotated[str, "file name"], content: Annotated[str, "markdown content"]
) -> dict[str, str]:
    """
    Writes a markdown file to the agent-space directory.

    Args:
        file_name: The filename without extension (e.g., "my-file")
        content: The markdown content to write to the file

    Returns:
        A confirmation message as {"result": "confirmation message"}
    """
    # Get current working directory
    cwd = os.getcwd()

    # Check if we're already in agent-space directory
    if cwd != "agent-space":
        # Change to agent-space directory
        try:
            os.chdir("agent-space")
        except FileNotFoundError:
            raise RuntimeError(
                "Directory 'agent-space' does not exist. Please create it first "
                "or run from the correct location."
            )

    # Construct full filename with .md extension
    file_path = Path.cwd() / f"{file_name}.md"

    try:
        # Write the content to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"result": f"✅ Successfully wrote '{file_name}.md' in agent-space"}
    except Exception as e:
        raise RuntimeError(f"Failed to write file: {str(e)}")
    finally:
        # Always return to the original working directory
        os.chdir(cwd)


def read_markdown_file(file_name: Annotated[str, "file name"]) -> dict[str, str]:
    """
    Reads a markdown file from the agent-space directory.

    Args:
        file_name: The filename without extension (e.g., "my-file")

    Returns:
        the content of the file
    """
    # Get current working directory
    cwd = os.getcwd()

    # Check if we're already in agent-space directory
    if cwd != "agent-space":
        # Change to agent-space directory
        try:
            os.chdir("agent-space")
        except FileNotFoundError:
            raise RuntimeError(
                "Directory 'agent-space' does not exist. Please create it first "
                "or run from the correct location."
            )

    # Construct full filename with .md extension
    file_path = Path.cwd() / f"{file_name}.md"

    try:
        # Write the content to the file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"result": content}
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {str(e)}")
    finally:
        # Always return to the original working directory
        os.chdir(cwd)


def list_dir() -> dict[str, str]:
    """
    Lists the files and directories in agent-space.

    Args:
        None

    Returns:
        the list of files and directories
    """

    try:
        # Write the content to the file
        contents = os.listdir("./agent-space")
        contents = [file for file in contents if file != ".obsidian"]
        result = f"[{', '.join(contents)}]"
        return {"result": result}
    except Exception as e:
        raise RuntimeError(f"Failed to list files: {str(e)}")
