import curses
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

# Map pygments token types to curses colors
TOKEN_COLOR_MAP = {
    Token.Keyword: curses.COLOR_BLUE,
    Token.Name: curses.COLOR_CYAN,
    Token.Literal.String: curses.COLOR_GREEN,
    Token.Literal.Number: curses.COLOR_MAGENTA,
    Token.Operator: curses.COLOR_RED,
    Token.Comment: curses.COLOR_GREEN,
    Token.Punctuation: curses.COLOR_WHITE,
    Token.Text: -1,  # Default
}

def get_curses_color(token_type):
    for ttype in TOKEN_COLOR_MAP:
        if token_type in ttype:
            return TOKEN_COLOR_MAP[ttype]
    return -1  # Default

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    # Color pair 1: default fg, yellow bg (for highlight)
    curses.init_pair(1, -1, curses.COLOR_YELLOW)
    # Set up color pairs for syntax highlighting (foreground only)
    color_pair_map = {}
    pair_number = 2
    for color in set(TOKEN_COLOR_MAP.values()):
        if color == -1:
            continue
        curses.init_pair(pair_number, color, -1)
        color_pair_map[color] = pair_number
        pair_number += 1

    lines = [
        "x = 1",
        "y = 2",
        "z = x + y",
        "for i in range(3):",
        "    z += i",
        "    print(f'i={i}, z={z}')",
        "print('Done!')"
    ]
    active_line = 2  # Highlight line 3 (0-based)

    stdscr.clear()
    for idx, line in enumerate(lines):
        x = 0
        if idx == active_line:
            # Highlighted line: yellow background, syntax fg
            for token_type, token_value in lex(line, PythonLexer()):
                color = get_curses_color(token_type)
                if color != -1:
                    # Use a new color pair for fg on yellow bg
                    pair_id = 100 + color  # Arbitrary high number to avoid collision
                    try:
                        curses.init_pair(pair_id, color, curses.COLOR_YELLOW)
                    except:
                        pass  # Already initialized
                    stdscr.addstr(idx, x, token_value, curses.color_pair(pair_id))
                else:
                    stdscr.addstr(idx, x, token_value, curses.color_pair(1))
                x += len(token_value)
        else:
            # Normal line: syntax fg, default bg
            for token_type, token_value in lex(line, PythonLexer()):
                color = get_curses_color(token_type)
                if color != -1:
                    stdscr.addstr(idx, x, token_value, curses.color_pair(color_pair_map[color]))
                else:
                    stdscr.addstr(idx, x, token_value)
                x += len(token_value)
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)
