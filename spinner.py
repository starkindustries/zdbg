import time
import sys

spinner = ['|', '/', '-', '\\']

for _ in range(20):  # Spin 20 times
    for ch in spinner:
        sys.stdout.write(f'\r{ch}')
        sys.stdout.flush()
        time.sleep(0.1)
print('\r ', end='')  # Clear spinner at the end
 