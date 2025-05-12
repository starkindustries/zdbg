import os

def main():
    output_lines = []

    while True:
        # Get terminal size
        try:
            size = os.get_terminal_size()
            height, width = size.lines, size.columns
        except OSError:
            # Fallback if not a real terminal
            height, width = 24, 80

        # Clear the screen
        print("\033c", end="")

        # Number of lines to show above the prompt
        lines_to_show = height - 1  # 1 line for the prompt

        # Get the lines to display
        visible_lines = output_lines[-lines_to_show:]

        # Print the output lines
        for line in visible_lines:
            print(line[:width-1])

        # Fill any remaining space with blank lines so the prompt is always at the bottom
        for _ in range(lines_to_show - len(visible_lines)):
            print()

        # Prompt for input at the bottom
        cmd = input("> ")

        if cmd.strip() == "quit":
            break
        output_lines.append(f"You entered: {cmd}")

if __name__ == "__main__":
    main()
