import sys
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
        line = self.get_line(lineno)
        print(f'-> {self.filename}:{lineno}: {line.strip()}')
        self.render_file(lineno)
        while True:
            cmd = input('(debugger) step/quit > ').strip().lower()

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

    def render_file(self, highlight_lineno):
        with open(self.filename) as f:
            lines = f.readlines()

        # use lightbulb for highlights and github-dark for normal line numbers
        console = Console()
        for lineno, line in enumerate(lines):
            line = line.strip()
            if (lineno + 1) == highlight_lineno:
                syntax = Syntax(line, "python", theme="lightbulb", line_numbers=True, start_line=lineno+1)
            else:
                syntax = Syntax(line, "python", theme="github-dark", line_numbers=True, start_line=lineno+1)
            console.print(syntax) 

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python debugger.py <script.py>')
        sys.exit(1)
    dbg = MyDebugger(sys.argv[1])
    dbg.run() 