from scapy.all import rdpcap, IP
from datetime import datetime, timezone

packets = rdpcap("stairs.pcap")

print("Checking packets around 1782902525:")
target_time = 1782902525.0

matching_packets = []
for i, p in enumerate(packets):
    t = float(p.time)
    if abs(t - target_time) < 10.0:
        matching_packets.append((i, p))

print(f"Found {len(matching_packets)} packets within 10s of target_time:")
for idx, p in matching_packets:
    if IP in p:
        ip = p[IP]
        print(f"#{idx}: time={float(p.time):.3f}, src={ip.src}, dst={ip.dst}, proto={ip.proto}, id={ip.id}, flags={ip.flags}, frag={ip.frag}, len={ip.len}, payload_len={len(bytes(ip.payload))}")
        raw = bytes(p)
        # check if printable
        print(f"    raw payload preview: {bytes(ip.payload)[:30]}")
