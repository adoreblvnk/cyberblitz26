#!/usr/bin/env python3
"""Re-derive the font permutation sigma straight from the EPUB zip (no extraction dir needed).

Proves: stored uppercase A-Z codepoints in EPUB/fonts/narrator.ttf draw the glyphs
of sigma(letter) from stock DejaVu Serif; sigma(clue) == Part-1 flag.
Then prints the 10 collector's-edition fragments raw / revealed / unrevealed.

Run:  (uv pip install fonttools && uv run rederive.py)   or any python3 with fontTools.
Reference font must exist at ../unreliable-narrator/DejaVuSerif.ttf
"""
import io, os, zipfile
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
EPUB = os.path.join(HERE, "unreliable-narrator.epub")
REF_FONT = os.path.join(HERE, "..", "unreliable-narrator", "DejaVuSerif.ttf")

CLUE_STORED = "PRNUFT2026{CMMHFH_OQ_FIC_DHMAOQ}"
CLUE_PLAIN = "CYBLTZ2026{ERRATA_IN_THE_MARGIN}"

FRAGMENTS = {1: "ZYVRP", 2: "CKJJM", 3: "DNNWC", 4: "IKXBB", 5: "FPOUO",
             6: "STTPG", 7: "FGFIB", 8: "PCVLV", 9: "VTJXV", 10: "OADIT"}


def outline_hash(gset, name):
    """Content fingerprint of a glyph: identical outline -> identical letter."""
    g = gset[name]
    if g.numberOfContours == 0:
        return ("empty",)
    c, _e, _f = g.getCoordinates(gset)
    s = 0
    for x, y in zip(c[0], c[1]):
        s = (s * 1000003 + int(x) * 31 + int(y)) & 0xFFFFFFFFFFFF
    return (g.numberOfContours, g.xMin, g.yMin, g.xMax, g.yMax, len(c[0]), s)


def main():
    with zipfile.ZipFile(EPUB) as z:
        bad = TTFont(io.BytesIO(z.read("EPUB/fonts/narrator.ttf")))
    ref = TTFont(REF_FONT)

    ridx = {}
    for cp, gn in ref.getBestCmap().items():
        ridx.setdefault(outline_hash(ref["glyf"], gn), chr(cp).upper())
    bmap = bad.getBestCmap()
    bglyphs = bad["glyf"]
    sigma = {}
    for cp in range(ord("A"), ord("Z") + 1):
        sigma[chr(cp)] = ridx.get(outline_hash(bglyphs, bmap[cp]))

    def reveal(s):
        return "".join(sigma.get(c, c) for c in s)

    inv = {v: k for k, v in sigma.items() if v}
    def unreveal(s):
        return "".join(inv.get(c, c) for c in s)

    print("sigma:", " ".join(f"{k}->{v}" for k, v in sigma.items()))
    revealed = reveal(CLUE_STORED)
    print("clue check:", revealed, "->", "OK" if revealed == CLUE_PLAIN else "MISMATCH!")

    print("\nfragments (fragment at EPUB/notes/noteN.xhtml):")
    for n, f in FRAGMENTS.items():
        print(f"note{n:2} {f}  sigma={reveal(f)}  sigma^-1={unreveal(f)}")


if __name__ == "__main__":
    main()
