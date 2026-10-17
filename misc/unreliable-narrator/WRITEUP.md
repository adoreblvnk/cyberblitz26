# Unreliable Narrator — Part 1 Writeup

**Category:** misc
**Flag:** `CYBLTZ2026{ERRATA_IN_THE_MARGIN}`

## Prompt

> Got drunk at the ePUB and now the pages are blurry, the plot makes no sense, and the narrator is telling me things that never happened. I'm starting to think the copy I was handed isn't the only printing.

We're given `unreliable-narrator.epub`.

## Recon

An EPUB is just a ZIP. Unzip it:

```
mimetype
META-INF/container.xml
EPUB/main.opf
EPUB/alternate.opf          <-- two package files!
EPUB/nav.xhtml
EPUB/css/book.css
EPUB/fonts/narrator.ttf
EPUB/text/chapter01.xhtml
EPUB/text/chapter02.xhtml
EPUB/text/printer.xhtml      <-- not referenced by main.opf
EPUB/assets/colophon.txt
EPUB/notes/note1.xhtml ... note10.xhtml
```

The prompt's big hint is **"the copy I was handed isn't the only printing."** Sure enough,
`META-INF/container.xml` declares **two** rootfiles (two "editions"):

```xml
<rootfiles>
    <rootfile full-path="EPUB/main.opf" .../>        <!-- the standard printing -->
    <rootfile full-path="EPUB/alternate.opf" .../>   <!-- the Collector's Edition -->
</rootfiles>
```

A normal reader opens the **first** rootfile (`main.opf`). That standard edition only
contains the two chapters + the font — it deliberately **leaves out** the printer page,
the colophon and the annotations. Those extra files are only wired up by `alternate.opf`
("The Unreliable Narrator - Collector's Edition").

Chapter 2 spells out the next step in its last paragraphs:

> *This is not the only printing. Look at what the printer left out of yours.*

So: switch to the Collector's Edition and read what the standard printing omitted —
`EPUB/text/printer.xhtml`.

## The clue

`printer.xhtml` contains a flavour line and then a very flag-shaped string in a
`narrator-clue` paragraph:

> I remember the shape of the words more clearly than the words themselves.
>
> `PRNUFT2026{CMMHFH_OQ_FIC_DHMAOQ}`

That is the flag format (`CYBLTZ2026{...}`) but with every letter wrong. The hint
*"I remember the **shape** of the words more clearly than the words themselves"* points
at the embedded font `EPUB/fonts/narrator.ttf`: the glyphs have been **shuffled**. The
character stored in the file is not the character you see on screen — the font is the
"unreliable narrator."

## Cracking the font

`narrator.ttf` is a tampered copy of **DejaVu Serif 2.37**. The tamper is in the `cmap`:
the uppercase A–Z code points are remapped so that, e.g., typing `P` displays the glyph
that *draws* a `C`.

To recover the mapping, compare glyph **outlines** against a clean DejaVu Serif: for each
uppercase code point in the tampered font, hash the outline of the glyph it maps to and
look up which real letter has that identical outline. (This is exactly what
`decode_font.py` does with `outline_hash`.)

```python
from fontTools.ttLib import TTFont
BAD = TTFont("work/EPUB/fonts/narrator.ttf")
REF = TTFont("DejaVuSerif.ttf")

def outline_hash(gset, name):
    g = gset[name]
    if g.numberOfContours == 0: return ("empty",)
    c,_,_ = g.getCoordinates(gset); s = 0
    for x,y in zip(c[0],c[1]): s = (s*1000003 + int(x)*31 + int(y)) & 0xFFFFFFFFFFFF
    return (g.numberOfContours, g.xMin, g.yMin, g.xMax, g.yMax, len(c[0]), s)

ref = {}
for cp,gn in REF.getBestCmap().items():
    ref.setdefault(outline_hash(REF["glyf"], gn), chr(cp).upper())

bad = BAD.getBestCmap()
mapping = {chr(cp): ref[outline_hash(BAD["glyf"], bad[cp])] for cp in range(ord('A'), ord('Z')+1)}
```

Recovered mapping (call it **σ** — "what the font actually draws for each typed letter"):

```
A->G B->J C->E D->M E->F F->T G->O H->A I->H J->P K->S L->W M->R
N->B O->I P->C Q->N R->Y S->V T->Z U->L V->U W->X X->Q Y->D Z->K
```

As a permutation σ decomposes into cycles:

```
(A G O I H)                     len 5
(B J P C E F T Z K S V U L W X Q N)  len 17
(D M R Y)                       len 4
order = lcm(5,17,4) = 340
```

(σ is a single fixed permutation, **not** an involution — applying it twice does not
return the original, which matters if you try to "undo" it later.)

## Decode

Apply σ to the clue (digits, `{`, `}` and `_` pass through unchanged):

```
PRNUFT2026{CMMHFH_OQ_FIC_DHMAOQ}
C Y B L T Z 2026 { E R R A T A _ I N _ T H E _ M A R G I N }
```

→ **`CYBLTZ2026{ERRATA_IN_THE_MARGIN}`**

Fitting: the second flag is literally an *erratum in the margin* of the other printing.

## Loose thread → Part 2

The Collector's Edition also adds `colophon.txt` and ten `notes/noteN.xhtml` annotation
pages, each holding a 5-letter `flag-fragment`. Running σ on those fragments does **not**
immediately give readable text — they are the puzzle for Part 2 (`un-the-collectors-edition`).

```
note1  ZYVRP   note2  CKJJM   note3  DNNWC   note4  IKXBB   note5  FPOUO
note6  STTPG   note7  FGFIB   note8  PCVLV   note9  VTJXV   note10 OADIT
```
