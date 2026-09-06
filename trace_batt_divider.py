import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's inspect wires around (118.11, 24.13) and (118.11, 34.29)
wire_matches = re.finditer(r'\(wire[\s\S]*?\(pts[\s\S]*?\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)[\s\S]*?\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', text)

print("Wires around R21 & R22 (X: 100..130, Y: 10..45):")
for m in wire_matches:
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    if 100 <= x1 <= 130 and 10 <= y1 <= 45:
        print(f"  Wire: ({x1}, {y1}) -> ({x2}, {y2})")

print("\nLabels around R21 & R22:")
for m in re.finditer(r'\((?:global_label|label)\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text):
    name, x, y = m.group(1), float(m.group(2)), float(m.group(3))
    if 100 <= x <= 130 and 10 <= y <= 45:
        print(f"  Label: {name} at ({x}, {y})")

for m in re.finditer(r'\(symbol\s+\(lib_id\s+"power:[^"]+"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text):
    x, y = float(m.group(1)), float(m.group(2))
    if 100 <= x <= 130 and 10 <= y <= 45:
        print(f"  Power sym at ({x}, {y})")

for m in re.finditer(r'\(symbol\s+\(lib_id\s+"[^"]+"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)[\s\S]*?\(property\s+"Value"\s+"(\+3\.3V|\+5V|\+BATT|GND|GNDA|VDDA|GNDPWR)"', text):
    x, y, pval = float(m.group(1)), float(m.group(2)), m.group(3)
    if 100 <= x <= 130 and 10 <= y <= 45:
        print(f"  Power {pval} at ({x}, {y})")
