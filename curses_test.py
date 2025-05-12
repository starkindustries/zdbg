import curses

def main(stdscr):
    curses.curs_set(1)  # Show the cursor
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    output_win = curses.newwin(height - 1, width, 0, 0)
    input_win = curses.newwin(1, width, height - 1, 0)
    output_lines = []

    while True:
        output_win.clear()
        for idx, line in enumerate(output_lines[-(height-2):]):
            output_win.addstr(idx, 0, line[:width-1])
        output_win.refresh()

        input_win.clear()
        input_win.addstr(0, 0, "> ")
        input_win.refresh()

        # This turns on echoing, so when the user types their command, the characters they type are visible in the input window.
        curses.echo()
        # This reads a string from the user. Because echo is on, the user can see what they are typing.
        cmd = input_win.getstr(0, 2, width-3).decode('utf-8')
        # This turns echoing back off after the input is read, so that any further input (if any) will not be automatically displayed.
        curses.noecho()

        if cmd.strip() == "quit":
            break
        output_lines.append(f"You entered: {cmd}")

if __name__ == "__main__":
    curses.wrapper(main)
