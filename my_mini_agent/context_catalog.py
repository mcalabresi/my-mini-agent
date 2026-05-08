import os

# import getpass
from datetime import datetime
from pathlib import Path


def current_date_time() -> str:
    return f"Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"


# def user_context() -> str:
#     return f"Current user: {getpass.getuser()}\n"


def user_context() -> str:
    return "Current user: Marcello"


def my_files() -> str:
    cwd = os.getcwd()
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
    file_path = Path.cwd() / "index.md"

    try:
        # Write the content to the file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        raise RuntimeError(f"Failed to read file: {str(e)}")
    finally:
        # Always return to the original working directory
        os.chdir(cwd)
