# Demonstrate syntax highlighting in the terminal using pygments and rich

# --- Using pygments ---
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

lines = [
    "x = 1",
    "y = 2",
    "z = x + y",
    "for i in range(3):",
    "    z += i",
    "    print(f'i={i}, z={z}')",
    "print('Done!')"
]

print("\nPygments highlighting:")
for line in lines:
    print(highlight(line, PythonLexer(), TerminalFormatter()), end='')

# --- Using rich ---
from rich.console import Console
from rich.syntax import Syntax

# Note: lightbulb, monokai, github-dark, and rrt are REALLY good.
themes = [
    # Good contrast
    "bw", "sas", "staroffice", "xcode", "default", "monokai", "lightbulb", "github-dark", "rrt",
    # Suboptimal contrast
    "abap", "algol", "algol_nu", "arduino", "autumn", "borland", "colorful", "igor", "lovelace",
    "murphy", "pastie", "rainbow_dash", "stata-light", "trac", "vs", "emacs", "tango",
    "solarized-light", "manni", "gruvbox-light", "friendly", "friendly_grayscale", "perldoc",
    "paraiso-light", "zenburn", "nord", "material", "one-dark", "dracula", "nord-darker",
    "gruvbox-dark", "stata-dark", "paraiso-dark", "coffee", "solarized-dark", "native", "inkpot",
    "fruity", "vim"
]

console = Console()
code = "\n".join(lines)
for theme in themes:
    print(f"\n{theme}:")
    syntax = Syntax(code, "python", theme=theme, line_numbers=True, highlight_lines={3})
    console.print(syntax) 
