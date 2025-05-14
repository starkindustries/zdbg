import sys
import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from rich.console import Console
from rich.syntax import Syntax


CLEAR_LINE = '\033[K'
SHOW_CURSOR = '\033[?25h'
HIDE_CURSOR = '\033[?25l'


class MyDebugger:
    def __init__(self, filename):
        self.filename = filename
        self._wait_for_input = True
        self.last_command = os.environ.get('DEBUGGER_LAST_COMMAND', None)
        last_highlight_env = os.environ.get('DEBUGGER_LAST_HIGHLIGHT')
        self.last_highlight_lineno = int(last_highlight_env) if last_highlight_env is not None else None
        self.auto_step_count = int(os.environ.get('DEBUGGER_AUTO_STEP', '0'))
        self.step_count = int(os.environ.get('DEBUGGER_STEP_COUNT', '0'))
        self.height, self.width = self.get_terminal_size()
        with open(self.filename) as f:
            self.lines = [line.rstrip('\n') for line in f.readlines()]
    
    def get_terminal_size(self):
        # Get terminal size
        try:
            size = os.get_terminal_size()
            height, width = size.lines, size.columns
        except OSError:
            height, width = 24, 80
        return height, width

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
            self.render(lineno, frame.f_locals)
            self.last_highlight_lineno = lineno

            if self.auto_step_count > 0:
                self.auto_step_count -= 1
                self.step_count += 1
                break
            cmd = input(f'[step {self.step_count}] > {CLEAR_LINE}').strip().lower()

            if cmd == '':
                cmd = self.last_command
            else:
                self.last_command = cmd

            if cmd in ['step', 's']:
                print("Stepping...", end='')
                self.step_count += 1
                break
            elif cmd in ['back', 'b']:
                print('Restarting program...', end='')
                # Clear state and restart with auto-step
                sys.settrace(None)
                new_env = os.environ.copy()
                new_env['DEBUGGER_AUTO_STEP'] = str(max(self.step_count - 1, 0))
                new_env['DEBUGGER_STEP_COUNT'] = '0'
                if self.last_highlight_lineno is not None:
                    new_env['DEBUGGER_LAST_HIGHLIGHT'] = str(self.last_highlight_lineno)
                elif 'DEBUGGER_LAST_HIGHLIGHT' in new_env:
                    del new_env['DEBUGGER_LAST_HIGHLIGHT']
                new_env['DEBUGGER_LAST_COMMAND'] = "back"
                os.execve(sys.executable, [sys.executable] + sys.argv, new_env)
            elif cmd == 'quit':
                print('Exiting debugger.')
                sys.exit(0)
            else:
                self.print_message_at_bottom('Unknown command. Type step, back or quit.')
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
        # add extra padding if index is less than 10, i.e. less than 2 digits
        if start_line < 10:
            line = " " + line
        theme = "lightbulb" if highlight else "github-dark"
        syntax = Syntax(line, "python", theme=theme, line_numbers=True, start_line=start_line)
        console = Console()
        console.print(syntax)

    def render_full_file(self):
        # Move cursor to the top of the code area
        print(f"\033[{1}H", end="")
        for idx, line in enumerate(self.lines, start=1):
            self.print_with_rich_syntax(line, idx, highlight=False)

    def render(self, highlight_lineno, locals_dict=None):
        height = self.height
        lines = self.lines

        # Hide cursor
        print(HIDE_CURSOR, end="", flush=True)

        # Only clear the screen on the first render (or if last_highlight_lineno is None)
        if self.last_highlight_lineno is None:
            print("\033c", end="")
            self.render_full_file()

        # Highlight the new line
        print(f"\033[{highlight_lineno}H", end="")
        self.print_with_rich_syntax(lines[highlight_lineno - 1], highlight_lineno, highlight=True)

        # Unhighlight the previous line
        if self.last_highlight_lineno and self.last_highlight_lineno != highlight_lineno:
            print(f"\033[{self.last_highlight_lineno}H", end="")
            self.print_with_rich_syntax(lines[self.last_highlight_lineno - 1], self.last_highlight_lineno, highlight=False)

        # Print local variables immediately after the code
        # Move cursor to the line after the last code line
        print(f"\033[{len(lines) + 1}H", end="")
        var_lines = 0
        if locals_dict:
            print("\nLocal variables:")
            print("=================")
            var_lines += 3
            for var, value in locals_dict.items():
                if not var.startswith('__') and not isinstance(value, type) and var != 'self':
                    print(f"{var} = {value!r}{CLEAR_LINE}")
                    var_lines += 1

        # Fill any remaining space with blank lines so the prompt is always at the bottom
        for _ in range((height - len(lines)) - var_lines - 2):
            print()
        print(SHOW_CURSOR, end="", flush=True)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python debugger.py <script.py>')
        sys.exit(1)
    dbg = MyDebugger(sys.argv[1])
    dbg.run() 