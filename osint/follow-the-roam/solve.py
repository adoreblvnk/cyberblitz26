#!/usr/bin/env python3
"""
Solution script for osint/follow-the-roam challenge.
Combines Fragment 1 from Instagram Archive #07 with Fragment 2 from YouTube Video 3.
"""

def solve():
    # Fragment 1/2 recovered from Instagram @laylaroams (Match Archive #07 caption):
    # Originally posted as CYBLITZ2026{T1GrE4l_ (with known format typo CYBLITZ -> CYBLTZ)
    fragment_1 = "T1GrE4l_"

    # Fragment 2/2 recovered from YouTube @laylaroams Video 3 ("Layla but I can't aim"):
    # Single-frame watermark appearing at 10:17 - 10:18 in the bottom right:
    fragment_2 = "P4qU1t0"

    flag = f"CYBLTZ2026{{{fragment_1}{fragment_2}}}"
    print(f"[+] Fragment 1: {fragment_1}")
    print(f"[+] Fragment 2: {fragment_2}")
    print(f"[+] Final Flag: {flag}")
    return flag

if __name__ == "__main__":
    solve()
