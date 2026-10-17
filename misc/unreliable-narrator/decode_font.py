#!/usr/bin/env python3
"""Identify the real letter each glyph in the tampered narrator.ttf actually draws.

Strategy: for every uppercase letter we ask "which real DejaVu Serif glyph has
the identical outline as the glyph this font uses for that codepoint?"
"""
import os
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
BAD = TTFont(os.path.join(HERE, "work/EPUB/fonts/narrator.ttf"))
REF = TTFont(os.path.join(HERE, "DejaVuSerif.ttf"))

def outline_hash(gset, name):
    """Content fingerprint of a glyph: same outline -> same letter."""
    g = gset[name]
    if g.numberOfContours == 0:
        return ("empty",)
    c, _end, _flags = g.getCoordinates(gset)
    s = 0
    for x, y in zip(c[0], c[1]):
        s = (s * 1000003 + int(x) * 31 + int(y)) & 0xFFFFFFFFFFFF
    return (g.numberOfContours, g.xMin, g.yMin, g.xMax, g.yMax, len(c[0]), s)

ref_cmap = REF.getBestCmap()
ref_glyphs = REF["glyf"]
ref_index = {}
for cp, gname in ref_cmap.items():
    ref_index.setdefault(outline_hash(ref_glyphs, gname), chr(cp).upper())

bad_cmap = BAD.getBestCmap()
bad_glyphs = BAD["glyf"]
bad_order = BAD.getGlyphOrder()

mapping = {}
for cp in range(ord("A"), ord("Z") + 1):
    gname = bad_cmap[cp]
    key = outline_hash(bad_glyphs, gname)
    real = ref_index.get(key)
    mapping[chr(cp)] = real
    print(f"  code {chr(cp)}  glyph {gname:<12} -> really draws '{real}'")

print("\nchar->true mapping:", "".join(f"{k}->{v} " for k, v in mapping.items()))

def reveal(s):
    return "".join(mapping.get(c, c) for c in s)

clue = "PRNUFT2026{CMMHFH_OQ_FIC_DHMAOQ}"
print("\nclue  :", clue)
print("true  :", reveal(clue))

frags = {1:"ZYVRP",2:"CKJJM",3:"DNNWC",4:"IKXBB",5:"FPOUO",
         6:"STTPG",7:"FGFIB",8:"PCVLV",9:"VTJXV",10:"OADIT"}
print("\nnotes (as rendered / as underlying):")
for n, f in frags.items():
    print(f"  note{n:<3}{f}  ->  {reveal(f)}")