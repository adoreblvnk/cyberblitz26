#!/usr/bin/env python3
"""
Solution script for forensics/roam-logs challenge.
Extracts EXIF UserComment logs from the recovered images,
traces the keyboard movement patterns on a QWERTY layout,
and reconstructs the flag word.
"""

import os
from PIL import Image, ExifTags

# Letter definitions based on QWERTY keyboard tracing
ROUTE_TO_LETTER = {
    "QAZXC": "L",
    "ZSEDCSD": "A",
    "RGYGB": "Y",
    "TGBNM": "L",
    "CFTGBFG": "A",
    "VFRTYHGFB": "R",
    "WSXCVFRE": "O",
    "BHUJMHJ": "A",
    "XDRFTGB": "M",
    "YTRFGHNBV": "S"
}

def solve():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    letters = []
    
    print("[*] Extracting hidden routes from images...")
    for i in range(1, 11):
        img_path = os.path.join(base_dir, f"img{i}.jpg")
        img = Image.open(img_path)
        exif = img.getexif()
        exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
        comment = exif_ifd.get(37510) # UserComment
        
        if isinstance(comment, bytes):
            # Strip ASCII header if present
            if comment.startswith(b"ASCII\x00\x00\x00"):
                comment_str = comment[8:].decode("ascii", errors="ignore")
            else:
                comment_str = comment.decode("ascii", errors="ignore")
        else:
            comment_str = str(comment)
            
        parts = [p.strip() for p in comment_str.split("//")]
        route = parts[1]
        letter = ROUTE_TO_LETTER.get(route, "?")
        letters.append(letter)
        print(f"  Image {i:02d}: route = {route:<12} -> letter = {letter} ({parts[2]})")
        
    word = "".join(letters)
    flag = f"CYBLTZ2026{{{word}}}"
    print(f"\n[+] Recovered Word: {word}")
    print(f"[+] Flag: {flag}")
    return flag

if __name__ == "__main__":
    solve()
