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


def write_note(
    note_name: Annotated[str, "note name"], content: Annotated[str, "markdown content"]
) -> dict[str, str]:
    """
    Writes a markdown file to the agent-space directory.

    Args:
        note_name: The name of the note we want to write
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
    file_path = Path.cwd() / f"{note_name}.md"

    try:
        # Write the content to the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"result": f"✅ Successfully wrote '{note_name}.md' in agent-space"}
    except Exception as e:
        raise RuntimeError(f"Failed to write file: {str(e)}")
    finally:
        # Always return to the original working directory
        os.chdir(cwd)


def read_note(note_name: Annotated[str, "note name"]) -> dict[str, str]:
    """
    Reads a markdown note from the agent-space directory.

    Args:
        note_name: The filename without extension (e.g., "my-file")

    Returns:
        the content of the note
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
    file_path = Path.cwd() / f"{note_name}.md"

    try:
        # Write the content to the file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"result": content}
    except Exception as _:
        # raise RuntimeError(f"Failed to read file: {str(e)}")
        return {"result": f"note {note_name} does not exist yet"}
    finally:
        # Always return to the original working directory
        os.chdir(cwd)


def list_notes() -> dict[str, str]:
    """
    Lists the notes in agent-space.

    Args:
        None

    Returns:
        the list of notes
    """

    try:
        # Write the content to the file
        contents = os.listdir("./agent-space")
        contents = [file.split(".")[0] for file in contents if file.endswith(".md")]
        result = f"[{', '.join(contents)}]"
        return {"result": result}
    except Exception as e:
        raise RuntimeError(f"Failed to list notes: {str(e)}")


def add_link_to_index(
    index_note_name: Annotated[str, "index note name"],
    note_file_name: Annotated[str, "note file name"],
    note_description: Annotated[str, "note description"],
) -> dict[str, str]:
    """
    Adds a link to an index file.

    Args:
        index_note_name: The name of the index file such as "index" or "<topic_name>-index"
        note_file_name: The name of the note we want to add to index. The file name should be without extension (.md)
        note_description: Short description of the link ( max 20 words)

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
    file_path = Path.cwd() / f"{index_note_name}.md"

    try:
        # Write the content to the file
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"- **[[{note_file_name}]]** - {note_description}\n")
        return {
            "result": f"✅ Successfully added link to '{index_note_name}' in agent-space"
        }
    except Exception as e:
        raise RuntimeError(f"Failed to write file: {str(e)}")
    finally:
        # Always return to the original working directory
        os.chdir(cwd)


def edit_note(
    note_name: Annotated[str, "note name"],
    old_text: Annotated[str, "content to replace"],
    new_text: Annotated[str, "content to add"],
) -> dict[str, str]:
    """
    Edits a markdown file in the agent-space directory by replacing the old text with the new text

    Args:
        note_name: The name of the note we want to write
        old_text: The old content to be replaced
        new_text: The new content to be changed

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
    file_path = Path.cwd() / f"{note_name}.md"

    try:
        with open(file_path, "r+", encoding="utf-8") as f:
            content = f.read()
            # Write the content to the file
            new_content = content.replace(old_text, new_text)
            f.seek(0)
            f.write(new_content)

        return {"result": f"✅ Successfully edited '{note_name}.md' in agent-space"}
    except Exception as e:
        raise RuntimeError(f"Failed to edit file: {str(e)}")
    finally:
        # Always return to the original working directory
        os.chdir(cwd)
