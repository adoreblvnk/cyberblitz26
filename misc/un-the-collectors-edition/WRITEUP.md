---
title: "Unreliable Narrator: The Collector's Edition"
ctf: "CYBERBLITZ 2026"
date: 2026-10-17
category: misc
difficulty: medium
flag_format: "CYBLTZ2026{...}"
author: "team"
---

# Unreliable Narrator: The Collector's Edition

## Summary

Part 2 of the "Unreliable Narrator" EPUB challenge. The same EPUB from Part 1 contains a Collector's Edition (`alternate.opf`) with a 10-note spine. The colophon instructs us to reorder by spine, but the key insight is the `linear="no"` attribute on spine items: only the **non-linear** notes contribute their raw fragments to the flag — no font cipher needed.

## Solution

### Step 1: Read the colophon and spine

The Collector's Edition (`EPUB/alternate.opf`) defines a spine with 11 items, 8 of which are notes:

```
ch1, note05(yes), note07(no), ch2, note02(no), note10(no),
note08(yes), note04(no), note01(no), note09(no), collector-note(no)
```

Notes 3 and 6 are absent from the spine ("walked past"). The colophon at `EPUB/assets/colophon.txt` reads:

> I numbered the notes to remember them. That was my first mistake.
> The catalogue remembers everything I kept. The binding remembers where it belonged.
> What I walked past still travels with me.

### Step 2: Select non-linear notes and concatenate raw fragments

The `linear="no"` attribute marks notes that are out of the main reading flow — these are the "corrections" that survive the collector's printing. The `linear="yes"` notes (5, 8) and the walked-past notes (3, 6) are excluded. The remaining six notes, read in spine order, give the flag body:

```python
import zipfile

z = zipfile.ZipFile("unreliable-narrator.epub")
alt_opf = z.read("EPUB/alternate.opf").decode()

# Parse spine: extract note numbers and linear attributes
import re
spine_entries = re.findall(
    r'<itemref\s+idref="(note\d+)"(?:\s+linear="(\w+)")?\s*/>', alt_opf
)

fragments = {}
for i in range(1, 11):
    html = z.read(f"EPUB/notes/note{i}.xhtml").decode()
    m = re.search(r'class="flag-fragment">(\w+)<', html)
    fragments[i] = m.group(1)

# Default linear is "yes" (EPUB spec); only "no" is explicit
flag_body = ""
for idref, linear in spine_entries:
    n = int(idref.replace("note", ""))
    if linear == "no":          # only non-linear notes
        flag_body += fragments[n]

print(f"CYBLTZ2026{{{flag_body}}}")
# CYBLTZ2026{FGFIBCKJJMOADITIKXBBZYVRPVTJXV}
```

### Why no font cipher?

Part 1 used σ (the Narrator font's cmap permutation) to decode `PRNUFT2026{...}` → `CYBLTZ2026{ERRATA_IN_THE_MARGIN}`. Part 2 is purely structural — the raw fragment letters are the flag body as-is. "My eyes are tired already" hints that no further decoding is needed; the answer is in the *structure*, not the font.

## Flag

```
CYBLTZ2026{FGFIBCKJJMOADITIKXBBZYVRPVTJXV}
```
