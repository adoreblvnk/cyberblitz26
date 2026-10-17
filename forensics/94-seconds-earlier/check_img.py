import subprocess
from PIL import Image
from PIL.ExifTags import TAGS

img = Image.open("incident_report.jpg")
print("Format:", img.format, "Size:", img.size, "Mode:", img.mode)

exif = img.getexif()
if exif:
    for tag_id, value in exif.items():
        tag = TAGS.get(tag_id, tag_id)
        print(f"EXIF: {tag} = {value}")
else:
    print("No EXIF data found.")

with open("incident_report.jpg", "rb") as f:
    data = f.read()

# Check for appended data after EOI (\xff\xd9)
eoi_pos = data.find(b"\xff\xd9")
print("EOI pos:", eoi_pos, "Total size:", len(data))
if eoi_pos != -1 and eoi_pos + 2 < len(data):
    print("Trailing data found:", data[eoi_pos+2:eoi_pos+100])
else:
    print("No trailing data after JPEG EOI.")
