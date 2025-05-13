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

    def trace_calls(self, frame, event, arg):
        if event != 'line':
            return self.trace_calls
        if frame.f_code.co_filename != self.filename:
            return self.trace_calls
        lineno = frame.f_lineno
        while True:
            self.render_file(lineno, frame.f_locals)
            cmd = input('> ').strip().lower()

            if cmd == '':
                cmd = self.last_command

            if cmd in ['step', 's']:
                self.last_command = 'step'
                break
            elif cmd == 'quit':
                self.last_command = 'quit'
                print('Exiting debugger.')
                sys.exit(0)
            else:
                print('Unknown command. Type step or quit.')
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

    def render_file(self, highlight_lineno, locals_dict=None):
        # Get terminal size
        try:
            size = os.get_terminal_size()
            height, width = size.lines, size.columns
        except OSError:
            height, width = 24, 80

        # Clear the screen
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
        for idx, line in enumerate(visible_lines, start=start_line+1):
            line = line.rstrip('\n')
            # add extra padding if index is less than 10, i.e. less than 2 digits
            if idx < 10:
                line = " " + line
            if idx == highlight_lineno:
                syntax = Syntax("  " + line[:width-8], "python", theme="lightbulb", line_numbers=True, start_line=idx)
            else:
                syntax = Syntax("  " + line[:width-8], "python", theme="github-dark", line_numbers=True, start_line=idx)
            console.print(syntax)

        # Print local variables immediately after the code
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
        for _ in range((lines_to_show - len(visible_lines)) - var_lines):
            print()
        print("\033[?25h", end="", flush=True)  # Show cursor

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python debugger.py <script.py>')
        sys.exit(1)
    dbg = MyDebugger(sys.argv[1])
    dbg.run() 