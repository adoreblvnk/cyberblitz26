from scapy.all import rdpcap, IP, UDP
import zlib

packets = rdpcap("stairs.pcap")

# Let's inspect packet 139 (10.26.3.47)
p139 = packets[139]
print("Packet 139 details:")
print("Time:", float(p139.time))
print("IP len:", p139[IP].len)
print("IP flags:", p139[IP].flags)
print("Payload:", bytes(p139[IP].payload))

# Let's inspect source 10.26.3.27 packets
pkts_27 = [p for p in packets if IP in p and p[IP].src == "10.26.3.27"]
print(f"\nSource 10.26.3.27 has {len(pkts_27)} packets:")
frag_dict = {}
for p in pkts_27:
    frag_dict[p[IP].frag * 8] = bytes(p[IP].payload)

full_data = b"".join(frag_dict[k] for k in sorted(frag_dict.keys()))
print("Full reassembled IP payload len:", len(full_data))
print("Full IP payload:", full_data)

# The first 8 bytes is UDP header
udp_header = full_data[:8]
udp_payload = full_data[8:]
print("UDP header:", udp_header)
print("UDP payload:", udp_payload)

# Verify CRC32
# Notice the payload has: ...|receipt=CYBLTZ2026{fr4gm3n75_74k3_7h3_5741rS}|crc32=4d77a334
prefix = udp_payload[:udp_payload.rfind(b"|crc32=")]
crc_val = f"{zlib.crc32(prefix):08x}"
print("CRC prefix:", prefix)
print("Calculated CRC:", crc_val)

# Also check packet 139's CRC
p139_udp_payload = bytes(p139[IP].payload)[8:]
p139_prefix = p139_udp_payload[:p139_udp_payload.rfind(b"|crc32=")]
p139_crc_val = f"{zlib.crc32(p139_prefix):08x}"
print("\nPacket 139 prefix:", p139_prefix)
print("Packet 139 calculated CRC:", p139_crc_val)
