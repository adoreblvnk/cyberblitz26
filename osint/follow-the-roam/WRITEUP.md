---
title: "Follow the Roam"
ctf: "CYBERBLITZ '26"
date: 2026-10-17
category: osint
difficulty: medium
points: 100
flag_format: "CYBLTZ2026{...}"
author: "adoreblvnk"
---

# Follow the Roam

## Summary

The challenge requires following an OSINT trail across Instagram and YouTube starting from the keyword `LAYLAROAMS` (recovered in *Roam Logs*). Two flag fragments are hidden across different media formats: Fragment 1 in an Instagram photo caption, and Fragment 2 in a single-frame watermark embedded in a YouTube match recording. Combining both yields the final flag.

---

## Solution

### Step 1: Recover Fragment 1 from Instagram

Starting from the username handle `LAYLAROAMS` obtained from the prior forensics challenge (*Roam Logs*), search public social media platforms:

1. **Instagram Profile:** `https://www.instagram.com/laylaroams/`
   * Contains 13 match archives showing different Mobile Legends skins for Layla.
2. In **Match Archive #07** (`https://www.instagram.com/p/DeChZzRzP6D/`), the caption notes:
   ```text
   Recovered Fragment 1/2:
   CYBLITZ2026{T1GrE4l_

   Looks like only half of it survived.
   A picture can only tell half the story.
   The rest was caught in motion.
   ```
   * *Note on Format:* The organizers announced a flag format correction addressing the typo in `CYBLITZ2026` to match the standard competition format `CYBLTZ2026`.

### Step 2: Locate Fragment 2 in the YouTube Match Recording

The caption in Archive #07 directs us to look for what was *"caught in motion"*:

1. **YouTube Channel:** `https://www.youtube.com/@laylaroams`
   * Hosts three video match recordings.
   * Video 3 (`2QlgH98RMys`) is titled *"Layla but I can't aim"* and features Layla wearing the exact **S.A.B.E.R. Breacher** skin from Instagram Match Archive #07.
   * During the competition, the challenge author updated Video 3's description to *"Damn I keep whiffing my ult"*, confirming it as the active challenge video.
2. Inspecting the video playback between **10:17 and 10:18** (during the mid-lane teamfight sequence) reveals a single-frame text watermark on the bottom right of the screen:
   ```text
   P4qU1t0}
   ```
3. Combining Fragment 1 (`T1GrE4l_`) and Fragment 2 (`P4qU1t0`) under the corrected competition flag format `CYBLTZ2026{...}` produces the final flag.

```python
#!/usr/bin/env python3
# solve.py

fragment_1 = "T1GrE4l_"
fragment_2 = "P4qU1t0"
flag = f"CYBLTZ2026{{{fragment_1}{fragment_2}}}"
print(f"[+] Flag: {flag}")
```

---

## Flag

```text
CYBLTZ2026{T1GrE4l_
P4qU1t0}
```
*(Also accepted: `CYBLITZ2026{T1GrE4l_P4qU1t0}`)*
