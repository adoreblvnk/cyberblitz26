The rehearsal console has no encore menu option. Find a way to reach the encore using the supplied binary.

nc 45.77.247.35 22013

nc 5.223.64.53 22013

Rehearsal protocol:

NEW <label>          Create a cue and print its numeric ID.
SELECT <id>          Select a cue for playback.
DROP <id>            Remove a cue from the active table.
LABEL <size> <hex>   Store <size> bytes of historical label data (exactly two hex digits per byte).
PLAY                 Play the selected cue.
QUIT                 End the rehearsal.

The supplied ELF is the same non-PIE build used by the service; symbols are retained. A rehearsal card beside the console reads NEW encore, SELECT 0, PLAY — an ordinary cue-label playback sequence. Console output, not the word printed on the card, determines whether encore authorization occurred.
