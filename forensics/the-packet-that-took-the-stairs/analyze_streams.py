from scapy.all import rdpcap, IP
import binascii

packets = rdpcap("stairs.pcap")

# Let's inspect packet #139
p139 = packets[139]
print("Packet #139:")
print(bytes(p139[IP].payload))

# Let's see what distinct src IPs and packet IDs exist
src_ips = set()
for p in packets:
    if IP in p:
        src_ips.add(p[IP].src)

print("\nDistinct src IPs:", sorted(src_ips))

# Let's inspect packets grouped by src IP around 1782902525
by_src = {}
for i, p in enumerate(packets):
    if IP in p:
        src = p[IP].src
        by_src.setdefault(src, []).append((i, p))

for src, pkts in sorted(by_src.items()):
    print(f"\n--- Source {src} ({len(pkts)} packets) ---")
    # Check if they form fragments
    for idx, p in pkts[:5]:
        ip = p[IP]
        print(f"  #{idx}: time={float(p.time):.3f}, id={ip.id}, frag={ip.frag}, flags={ip.flags}, len={ip.len}")
