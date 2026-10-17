import sys
from scapy.all import rdpcap, IP, TCP, UDP, ICMP
from datetime import datetime, timezone

packets = rdpcap("stairs.pcap")
print(f"Total packets: {len(packets)}")

if packets:
    first_time = float(packets[0].time)
    last_time = float(packets[-1].time)
    print(f"First packet time: {first_time} ({datetime.fromtimestamp(first_time, tz=timezone.utc)})")
    print(f"Last packet time:  {last_time} ({datetime.fromtimestamp(last_time, tz=timezone.utc)})")

protocols = {}
for p in packets:
    layers = []
    layer = p
    while layer:
        layers.append(layer.name)
        layer = layer.payload
        if layer == b'' or layer is None or len(layers) > 10:
            break
    key = " / ".join(layers)
    protocols[key] = protocols.get(key, 0) + 1

print("\nProtocols breakdown:")
for k, v in sorted(protocols.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
