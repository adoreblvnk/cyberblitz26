---
title: "Whack-a-Mole"
ctf: "CYBERBLITZ '26"
date: 2026-10-16
category: misc
difficulty: medium
points: 100
flag_format: "CYBLTZ2026{...}"
author: "adoreblvnk"
---

# Whack-a-Mole

## Summary

In "Whack-a-Mole", players inspect 12 personal photographs taken across Singapore and Malaysia where elements were removed using smartphone AI object erasers (Samsung Galaxy AI Generative Edit and Object Eraser). Scoring at least 10 of 12 by identifying the altered grid squares or normalized coordinates ($[x, y]$) unlocks the flag via `/api/submit`.

## Solution

### Step 1: Frontend & Endpoint Reconnaissance

Inspecting `app.js` and `/api/puzzles` reveals 12 sequential rounds:
- **Grid rounds**: submit a list of 0-indexed cell indices: $\text{index} = \text{row} \times \text{cols} + \text{col}$.
- **Point rounds**: submit normalized $[x, y] \in [0.0, 1.0]$ coordinates.
- **Unedited rounds**: submit an empty array `[]` (selected via "Nothing was erased").

Submissions are sent to `POST /api/submit` as:
```json
{
  "picks": [
    [4],
    [8, 9],
    [],
    [[0.47, 0.67]],
    ...
  ]
}
```
If `score >= 10`, the server returns `{"total": 12, "pass": 10, "score": score, "flag": "..."}`. Otherwise, it withholds the score and returns `{"total": 12, "pass": 10}`.

### Step 2: Image Forensics & Anomaly Detection

Analyzing all 12 downloaded images through local frequency variance (Laplacian), Error Level Analysis (ELA), and visual inspection revealed the inpainting artifacts:

1. **Photo 0 (Waffle, $3\times 4$)**: **`[4]`** — Waffle ridges in the central quadrant are horizontally blurred and smeared with dark chocolate syrup residue where a second ice cream scoop was removed.
2. **Photo 1 (Russell Lee, $6\times 5$, 2 picks)**: **`[8, 9]`** — Author Russell Lee at Popular Bookstore signing books. Two squares on the table containing book stacks and pens were manipulated.
3. **Photo 2 (Bakery, $5\times 5$)**: **`[]`** — Unedited. The empty spot in the wicker basket reflects naturally sold sourdough bread.
4. **Photo 3 (Lok Lok Skewers, Point)**: **`[[0.47, 0.67]]`** — Center bamboo skewer has shattered wood artifacts and duplicate textures floating over the grease-stained brown kraft paper where skewered meat was erased.
5. **Photo 4 (Bougainvillea, $5\times 5$)**: **`[12]`** — The center flower features an AI-hallucinated 6-petal bloom with a brown starfish center and washed-out green/grey bottom (real bougainvillea has only 3 papery bracts).
6. **Photo 5 (Espresso Bar, $5\times 5$)**: **`[17]`** — Inpainting artifacts around the wooden service tray with jars on the cafe counter.
7. **Photo 6 (Balcony / Walkway, $5\times 6$)**: **`[12]`** — Stamped with a Samsung Galaxy AI `✨ AI-generated content` watermark in cell 25. The erased object was located along the curb edge in cell 12.
8. **Photo 7 (Joji's Diner, $3\times 4$, 2 picks)**: **`[7, 8]`** — Retro diner wall where a circular vinyl record and wall decor were erased, leaving circular grey smudges across cells 7 and 8.
9. **Photo 8 (Bicycle Rack, Point, 2 picks)**: **`[[0.08, 0.30], [0.88, 0.27]]`** — Stamped with a Samsung Galaxy AI watermark in cell 25. An erased bicycle in upper rack track 1 left behind an orphan wheel ($[0.08, 0.30]$), and words were erased from the left side of the "NOTICE" sign ($[0.88, 0.27]$).
10. **Photo 9 (Figurine Shelf, Point)**: **`[]`** — Unedited. The feathery shadow on the wall is an optically natural shadow cast by the dried wheat in the orange vase from the yellow lamp on the right.
11. **Photo 10 (Miniature Ducks & Cup, $6\times 5$)**: **`[13]`** — The wooden groove ends with a curved notch, dark water rings appear on the wood, and a white tip protrudes behind the iced cup where a miniature item was erased.
12. **Photo 11 (Shiba Inu Salad Counter, $5\times 6$)**: **`[23]`** — Subtle edit in cell 23 on the counter adjacent to the salad bar toppings.

### Step 3: Solve Script

```python
import urllib.request
import json

URL = "http://5.223.64.53:22001/api/submit"

picks = [
    [4],                               # Photo 0: Waffle (erased scoop)
    [8, 9],                            # Photo 1: Russell Lee (table books)
    [],                                # Photo 2: Bakery (unedited)
    [[0.47, 0.67]],                    # Photo 3: Lok lok (broken skewer)
    [12],                              # Photo 4: Bougainvillea (hallucinated flower)
    [17],                              # Photo 5: Espresso bar (wooden tray)
    [12],                              # Photo 6: Balcony (curb edge)
    [7, 8],                            # Photo 7: Joji's Diner (erased vinyl)
    [[0.08, 0.30], [0.88, 0.27]],      # Photo 8: Bicycle rack (upper bike + notice)
    [],                                # Photo 9: Shelf figurines (unedited)
    [13],                              # Photo 10: Miniature ducks & cup (slot item)
    [23]                               # Photo 11: Shiba Inu (salad counter)
]

payload = json.dumps({"picks": picks}).encode("utf-8")
req = urllib.request.Request(
    URL,
    data=payload,
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req, timeout=5) as resp:
    data = json.loads(resp.read().decode())
    print("Score:", data.get("score"), "/", data.get("total"))
    print("Flag:", data.get("flag"))
```

## Flag

```
CYBLTZ2026{wh4ck3d_th3_4i_3r4s3r}
```
