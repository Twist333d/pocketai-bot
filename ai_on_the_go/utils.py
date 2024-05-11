def escape_markdown(text):
    """
    Accepts a text that will be returned in Markdown format.
    Correctly escapes special characters.
    :param text:
    :return:
    """
    # List of special characters that need to be escaped in MarkdownV2
    escape_chars = "_*[]()~`>#+-=|{}.!"

    # Escaping each character with a backslash
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)
