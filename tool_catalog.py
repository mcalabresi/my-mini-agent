import os
from pathlib import Path
from typing import Annotated

# example tools


def add(
    a: Annotated[int | float, "First number"],
    b: Annotated[int | float, "Second number"],
) -> dict[str, int | float]:
    """Add two numbers together."""
    return {"result": a + b}


def multiply(
    a: Annotated[int | float, "First number"],
    b: Annotated[int | float, "Second number"],
) -> dict[str, int | float]:
    """Multiplies two numbers together."""
    return {"result": a * b}


def secret() -> dict[str, str]:
    """Returns the secret key"""
    return {"result": "fluffy bunnies"}


def concatenate(
    a: Annotated[int | str, "First item"], b: Annotated[int | str, "Second item"]
) -> dict[str, str]:
    """Concatenates two items."""
    return {"result": str(a) + str(b)}


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


# useful tools


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
