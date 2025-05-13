import sys
import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from rich.console import Console
from rich.syntax import Syntax


class MyDebugger:
    def __init__(self, filename):
        self.filename = filename
        self._wait_for_input = True
        self.last_command = None
        self.last_highlight_lineno = None
        self.auto_step_count = int(os.environ.get('DEBUGGER_AUTO_STEP', '0'))
        self.step_count = int(os.environ.get('DEBUGGER_STEP_COUNT', '0'))

    def print_message_at_bottom(self, message):
        size = os.get_terminal_size()
        height, width = size.lines, size.columns
        # Move cursor to the last line
        print(f"\033[{height};1H", end="")
        # Clear the line
        print(" " * width, end="")
        # Move cursor back to the start and print the message
        print(f"\033[{height};1H{message}", end="", flush=True)

    def trace_calls(self, frame, event, arg):
        if event != 'line':
            return self.trace_calls
        if frame.f_code.co_filename != self.filename:
            return self.trace_calls
        lineno = frame.f_lineno
        while True:
            self.render_file(lineno, frame.f_locals)
            self.last_highlight_lineno = lineno
            stepped = False
            if self.auto_step_count > 0:
                self.auto_step_count -= 1
                self.last_command = 'step'
                stepped = True
                break
            cmd = input(f'[step {self.step_count}] > ').strip().lower()

            if cmd == '':
                cmd = self.last_command

            if cmd in ['step', 's']:
                self.last_command = 'step'
                stepped = True
                break
            elif cmd == 'back':
                print('Restarting program...', end='')
                # Clear state and restart with auto-step
                sys.settrace(None)
                new_env = os.environ.copy()
                new_env['DEBUGGER_AUTO_STEP'] = '10'
                new_env['DEBUGGER_STEP_COUNT'] = '0'
                os.execve(sys.executable, [sys.executable] + sys.argv, new_env)
            elif cmd == 'quit':
                self.last_command = 'quit'
                print('Exiting debugger.')
                sys.exit(0)
            else:
                self.print_message_at_bottom('Unknown command. Type step, back or quit.')
            if stepped:
                self.step_count += 1
        return self.trace_calls

    def get_line(self, lineno):
        with open(self.filename) as f:
            lines = f.readlines()
        return lines[lineno - 1] if 0 < lineno <= len(lines) else ''

    def run(self):
        with open(self.filename) as f:
            code = f.read()
        sys.settrace(self.trace_calls)
        globals_dict = {'__name__': '__main__'}
        exec(compile(code, self.filename, 'exec'), globals_dict)
        sys.settrace(None)

    def print_with_rich_syntax(self, line, start_line, highlight=False):
        theme = "lightbulb" if highlight else "github-dark"
        syntax = Syntax(line, "python", theme=theme, line_numbers=True, start_line=start_line)
        console = Console()
        console.print(syntax)

    def render_file(self, highlight_lineno, locals_dict=None):
        # Get terminal size
        try:
            size = os.get_terminal_size()
            height, width = size.lines, size.columns
        except OSError:
            height, width = 24, 80

        # Only clear the screen on the first render
        if self.last_highlight_lineno is None:
            print("\033c", end="")
        print("\033[?25l", end="", flush=True)  # Hide cursor

        with open(self.filename) as f:
            lines = f.readlines()

        # Number of lines to show above the prompt
        lines_to_show = height - 1  # 1 line for the prompt
        start_line = max(0, highlight_lineno - lines_to_show//2 - 1)
        end_line = min(len(lines), start_line + lines_to_show)
        visible_lines = lines[start_line:end_line]

        console = Console()
        # Only redraw the previously highlighted line and the new highlighted line
        # Calculate their positions in visible_lines
        lines_to_update = set()
        if self.last_highlight_lineno is not None:
            if start_line + 1 <= self.last_highlight_lineno <= end_line:
                lines_to_update.add(self.last_highlight_lineno)
        if start_line + 1 <= highlight_lineno <= end_line:
            lines_to_update.add(highlight_lineno)

        # Move cursor to the top of the code area
        print(f"\033[{1}H", end="")
        for idx, line in enumerate(visible_lines, start=start_line+1):
            line = line.rstrip('\n')
            # add extra padding if index is less than 10, i.e. less than 2 digits
            if idx < 10:
                line = " " + line
            if idx in lines_to_update or self.last_highlight_lineno is None:
                # Move cursor to the correct line
                line_pos = idx - start_line
                print(f"\033[{line_pos}H", end="")
                if idx == highlight_lineno:
                    self.print_with_rich_syntax(line, idx, highlight=True)
                else:
                    self.print_with_rich_syntax(line, idx, highlight=False)
            elif self.last_highlight_lineno is None:
                # On first render, print all lines
                if idx == highlight_lineno:
                    self.print_with_rich_syntax(line, idx, highlight=True)
                else:
                    self.print_with_rich_syntax(line, idx, highlight=False)

        # Print local variables immediately after the code
        # Move cursor to the line after the last code line
        print(f"\033[{len(visible_lines) + 1}H", end="")
        var_lines = 0
        if locals_dict:
            print("\nLocal variables:")
            print("=================")
            var_lines += 3
            for var, value in locals_dict.items():
                if not var.startswith('__'):
                    print(f"{var} = {value!r}")
                    var_lines += 1

        # Fill any remaining space with blank lines so the prompt is always at the bottom
        for _ in range((lines_to_show - len(visible_lines)) - var_lines - 1):
            print()
        print("\033[?25h", end="", flush=True)  # Show cursor

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python debugger.py <script.py>')
        sys.exit(1)
    dbg = MyDebugger(sys.argv[1])
    dbg.run() 