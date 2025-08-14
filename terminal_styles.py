# terminal_styles.py

# ANSI escape codes
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

BG_COLORS = {
    "black": "\033[40m",
    "red": "\033[41m",
    "green": "\033[42m",
    "yellow": "\033[43m",
    "blue": "\033[44m",
    "magenta": "\033[45m",
    "cyan": "\033[46m",
    "white": "\033[47m",
}

def style(text, color=None, bg_color=None, bold=False, underline=False):
    """
    Apply terminal styles to a string.

    Args:
        text (str): The text to style.
        color (str): Foreground color name.
        bg_color (str): Background color name.
        bold (bool): Bold text if True.
        underline (bool): Underline text if True.

    Returns:
        str: Styled text.
    """
    styled_text = ""
    if bold:
        styled_text += BOLD
    if underline:
        styled_text += UNDERLINE
    if color and color in COLORS:
        styled_text += COLORS[color]
    if bg_color and bg_color in BG_COLORS:
        styled_text += BG_COLORS[bg_color]

    styled_text += text + RESET
    return styled_text
