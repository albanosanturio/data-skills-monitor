# Automate saving pages via the SingleFile browser extension.
#
# For each loop: press Ctrl+Shift+Y (SingleFile "download full page"),
# wait 20s for the download to finish, press Ctrl+W (close current tab),
# wait 1s, repeat.
#
# Usage:
#   python get_htmls.py 39
#
# Switch to the browser tab you want to start on before running —
# a countdown gives you time to do that.

import sys
import time
import pyautogui

DOWNLOAD_WAIT_SECS = 20
CLOSE_TAB_WAIT_SECS = 1
START_DELAY_SECS = 5


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: python get_htmls.py <number_of_iterations>")
        sys.exit(1)

    iterations = int(sys.argv[1])

    print("Switch to the browser tab now...")
    for remaining in range(START_DELAY_SECS, 0, -1):
        print(f"Starting in {remaining}...")
        time.sleep(1)

    for i in range(1, iterations + 1):
        print(f"[{i}/{iterations}] Saving page (Ctrl+Shift+Y)...")
        pyautogui.hotkey('ctrl', 'shift', 'y')
        time.sleep(DOWNLOAD_WAIT_SECS)

        print(f"[{i}/{iterations}] Closing tab (Ctrl+W)...")
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(CLOSE_TAB_WAIT_SECS)

    print("Done.")


if __name__ == "__main__":
    main()
