"""
soundcheck-at-159
-----------------
The 8 kHz mono "test tone" is a decoy: the whole PCM payload is a 40 Hz square
wave with only two sample values (0x80 / 0xA3). The message lives in the WAV
container metadata:

  LIST/adtl  -> 10 x 'labl' sub-chunks, each holding a base64 fragment.
                (non-standard writer: the spec's dwName field is repurposed
                 to hold the cue identifier, not the string length)
  'cue '     -> 10 cue points; their dwIdentifier matches those labl values,
                dwSampleOffset points into the audio at 11 s intervals, but
                the points are STORED out of order -> "chorus before intro"
  LIST/INFO  -> ICMT "Rehearsal ledger order: 7,11,19,..." is the misleading
                cue-display order (sorted by id), NOT the message order.

Correct order = sort cue points by dwSampleOffset (chronological position).
"""

import base64
import re
import struct

raw = open('soundcheck.wav', 'rb').read()

# ---- top-level chunk walk -------------------------------------------------
chunks = []
off = 12
while off + 8 <= len(raw):
    cid = raw[off:off + 4]
    sz = struct.unpack('<I', raw[off + 4:off + 8])[0]
    chunks.append((cid, off, sz))
    off += 8 + sz + (sz & 1)

labels, cues, icmt = {}, [], None

for cid, o, sz in chunks:
    if cid == b'cue ':                                   # top-level cue chunk
        n = struct.unpack('<I', raw[o + 8:o + 12])[0]
        for i in range(n):
            ident, pos, fcc, cst, bst, soff = struct.unpack(
                '<IIIIII', raw[o + 12 + i * 24: o + 36 + i * 24])
            assert struct.pack('<I', fcc) == b'data'
            cues.append((ident, soff))
        continue

    if cid != b'LIST':
        continue
    p, end, ltype = o + 12, o + 8 + sz, raw[o + 8:o + 12]

    if ltype == b'adtl':
        while p + 8 <= end:
            scid = raw[p:p + 4]
            ssz = struct.unpack('<I', raw[p + 4:p + 8])[0]
            sb = p + 8
            if scid == b'labl':
                cue_id = struct.unpack('<I', raw[sb:sb + 4])[0]      # repurposed dwName
                labels[cue_id] = raw[sb + 4:sb + ssz].rstrip(b'\x00').decode()
            p = sb + ssz + (ssz & 1)

    elif ltype == b'INFO':
        q = o + 12
        while q + 8 <= end:
            sid = raw[q:q + 4]
            ssz = struct.unpack('<I', raw[q + 4:q + 8])[0]
            if sid == b'ICMT':
                icmt = raw[q + 8:q + 8 + ssz].rstrip(b'\x00').decode()
            q += 8 + ssz + (ssz & 1)

print('INFO/ICMT :', icmt)
print()
print('cue_id  fragment   stored#   sample_offset    time')
for i, (ident, soff) in enumerate(cues):
    print('%5d  %-9s %6d   %10d  %7.2fs'
          % (ident, labels[ident], i, soff, soff / 8000))

# ---- reorder chronologically (NOT by cue id / ledger) ---------------------
ordered = [labels[ident] for ident, _ in sorted(cues, key=lambda c: c[1])]
b64 = ''.join(ordered)
print('\nreassembled base64 :', b64)
print('decoded           :', base64.b64decode(b64, validate=True).decode())