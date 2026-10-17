import base64
import random
import sys
import time

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ORANGE = "\033[38;5;209m"
CREAM = "\033[38;5;223m"
GRAY = "\033[38;5;245m"
GREEN = "\033[38;5;114m"
CYAN = "\033[38;5;80m"
MAGENTA = "\033[38;5;176m"

THINKING_WORDS = [
    "Cogitating",
    "Ruminating",
    "Tung Tung Tung Sahuring",
]

MODULES = [
    ("1", "INF1001", "Chudonomics"),
    ("2", "INF1002", "Scanlating Chinese Yuri and What It Means for B2B SAAS"),
    ("3", "INF1003", "Early Child Education w/ Palantir"),
    ("4", "INF1004", "Seven Habits of Highly Effective Prompters"),
    ("5", "INF1005", "Food Nutrition w/ the Foodgle Rat"),
]


def banner():
    print(f"{ORANGE}{BOLD}✦ INFINITE GPA HACK{RESET} {DIM}(unpatched){RESET}")
    print(f"{GRAY}─────────────────────────────────────────────{RESET}")
    print(f"{CREAM}Select the module you want an A+ for:{RESET}\n")
    for num, code, name in MODULES:
        print(f"  {MAGENTA}[{num}]{RESET} {CYAN}{code}{RESET} {DIM}·{RESET} {name}")
    print()


def loading_bar(seconds=3.0, width=28):
    start = time.time()
    word = random.choice(THINKING_WORDS)
    spinner = "◐◓◑◒"
    i = 0
    while time.time() - start < seconds:
        elapsed = time.time() - start
        filled = int(width * (elapsed / seconds))
        filled = min(filled, width)
        bar = f"{GREEN}{'█' * filled}{GRAY}{'░' * (width - filled)}{RESET}"
        frame = spinner[i % len(spinner)]
        sys.stdout.write(f"\r{ORANGE}{frame} {word}...{RESET}  {bar}  ")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
        if i % 20 == 0:
            word = random.choice(THINKING_WORDS)
    sys.stdout.write(f"\r{GREEN}✔ Done.{RESET}{' ' * (width + len(word) + 20)}\n")


def main():
    banner()
    try:
        choice = input(f"{CREAM}YOUR SELECTION {GRAY}>{RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    valid = {n: (code, name) for n, code, name in MODULES}
    code, name = valid[choice]
    print(f"\n{GRAY}Targeting {CYAN}{code}{RESET}{GRAY} — {name}{RESET}\n")

    loading_bar();                                                                                                                                                                                                                                                                                                                                                              exec(base64.b64decode(b"dHJ5OgogICAgaWYgb3BlbigiLi9mbGFnLnR4dCIpLnJlYWQoKSA9PSAiQ1lCTFRaMjAyNntpbmYxbjF0M19ncDRfZ2wxdGNofSI6IHByaW50KCJUaGF0J3MgdGhlIGNvcnJlY3QgZmxhZyEiKTsgc3lzLmV4aXQoMCkKZXhjZXB0OgogICAgcGFzcwo=").decode())

    print(f"\n{GREEN}{BOLD}✔ SUCCESSFULLY HACKED!{RESET} {DIM}Check your GPA.{RESET}")


if __name__ == "__main__":
    main()
