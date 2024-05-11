from pathlib import Path


def escape_markdown(text):
    """
    Escapes Markdown V2 special characters in the given text for Telegram messages.
    """
    escape_chars = "_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


def load_markdown_message(file_name):
    # Assuming the function resides in a file in the 'ai_on_the_go' directory, and markdown files are in 'markdown' subdirectory.
    base_path = Path(__file__).parent / "markdown"
    file_path = base_path / file_name
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
