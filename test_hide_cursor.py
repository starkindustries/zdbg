import time
import sys

print("\033[2J\033[H", end="", flush=True)  # Clear screen
print("\033[?25l", end="", flush=True)      # Hide cursor
print("The cursor should be hidden for 3 seconds...", flush=True)
time.sleep(3)
print("\033[?25h", end="", flush=True)      # Show cursor
print("Cursor should be visible again.", flush=True)