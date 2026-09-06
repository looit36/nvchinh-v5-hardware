import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Search all wires near X in [70, 180], Y in [140, 190]
wire_matches = re.finditer(r'\(wire[\s\S]*?\(pts[\s\S]*?\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)[\s\S]*?\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', text)

print("Wires in Encoder region (X: 70..180, Y: 130..190):")
for m in wire_matches:
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    if 70 <= x1 <= 180 and 130 <= y1 <= 190:
        print(f"  Wire: ({x1}, {y1}) -> ({x2}, {y2})")

print("\nGlobal Labels in Encoder region:")
for m in re.finditer(r'\(global_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text):
    name, x, y = m.group(1), float(m.group(2)), float(m.group(3))
    if 70 <= x <= 180 and 130 <= y <= 190:
        print(f"  Label: {name:10s} at ({x}, {y})")
