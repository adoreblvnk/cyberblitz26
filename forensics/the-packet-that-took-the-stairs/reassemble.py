from scapy.all import rdpcap, IP
import zlib
import re

packets = rdpcap("stairs.pcap")

# Group by src IP
by_src = {}
for i, p in enumerate(packets):
    if IP in p:
        src = p[IP].src
        by_src.setdefault(src, []).append((i, p))

for src, pkts in sorted(by_src.items()):
    if src == "10.26.3.1":
        continue
    print(f"\n==================== Source: {src} ({len(pkts)} packets) ====================")
    # Check if packets are fragments
    # An IP fragment has frag offset (in 8-byte units)
    # Reassemble by offset
    frags = {}
    for idx, p in pkts:
        ip = p[IP]
        offset = ip.frag * 8
        payload = bytes(ip.payload)
        frags[offset] = (idx, payload, bool(ip.flags & 1)) # MF flag
    
    # Sort by offset
    sorted_offsets = sorted(frags.keys())
    print("Offsets present:", sorted_offsets)
    
    # Check if contiguous
    total_payload = b""
    expected_offset = 0
    complete = True
    for off in sorted_offsets:
        idx, payload, mf = frags[off]
        if off != expected_offset:
            print(f"Gap detected! Expected {expected_offset}, got {off}")
            complete = False
        total_payload += payload
        expected_offset = off + len(payload)
    
    print(f"Total reassembled length: {len(total_payload)}, complete: {complete}")
    print("Reassembled data:")
    try:
        text = total_payload.decode('latin1')
        print(text)
        
        # Check CRC32 if present in text
        # Format: |crc32=([0-9a-fA-F]+)
        m = re.search(r'\|crc32=([0-9a-fA-F]+)', text)
        if m:
            claimed_crc = m.group(1)
            # The data before |crc32=
            data_to_crc = total_payload[:m.start()]
            calc_crc = f"{zlib.crc32(data_to_crc):08x}"
            print(f"Claimed CRC: {claimed_crc}, Calculated CRC: {calc_crc}, Match: {claimed_crc.lower() == calc_crc.lower()}")
            
            # What if CRC includes something else, or whole payload?
            # Or UDP payload? (Notice the first 8 bytes might be UDP header!)
            # Let's check UDP header in first fragment
            udp_payload = total_payload[8:]
            m_udp = re.search(r'\|crc32=([0-9a-fA-F]+)', text[8:])
            if m_udp:
                data_udp = total_payload[8:8+m_udp.start()]
                calc_crc_udp = f"{zlib.crc32(data_udp):08x}"
                print(f"UDP data CRC: {calc_crc_udp}, Match: {claimed_crc.lower() == calc_crc_udp.lower()}")
    except Exception as e:
        print("Error decoding:", e)
