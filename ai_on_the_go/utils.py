def escape_markdown(text):
    """
    Escapes Markdown V2 special characters in the given text for Telegram messages.
    """
    escape_chars = "_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)


def load_markdown_message(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
