import re
from collections import defaultdict

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's extract all global_label, label, wire, junction, symbol pin locations.
# 1. Global labels
glabels = []
for m in re.finditer(r'\(global_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text):
    name, x, y = m.group(1), float(m.group(2)), float(m.group(3))
    glabels.append((name, x, y))

# 2. Local labels
labels = []
for m in re.finditer(r'\(label\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text):
    name, x, y = m.group(1), float(m.group(2)), float(m.group(3))
    labels.append((name, x, y))

# 3. Power symbols / global power labels (+3.3V, +5V, +BATT, GND, GNDA, etc.)
# (symbol (lib_id "power:...") (at X Y R) ... (property "Value" "GND" ...) ...)
powers = []
p_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"power:([^"]+)"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text)
for pm in p_matches:
    pname, px, py = pm.group(1), float(pm.group(2)), float(pm.group(3))
    powers.append((pname, px, py))

# Also search any property "Value" "+3.3V" or "+5V" or "+BATT" or "GND" or "GNDA"
p2_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"[^"]+"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)[\s\S]*?\(property\s+"Value"\s+"(\+3\.3V|\+5V|\+BATT|GND|GNDA|VDDA|GNDPWR)"', text)
for pm in p2_matches:
    px, py, pname = float(pm.group(1)), float(pm.group(2)), pm.group(3)
    powers.append((pname, px, py))

print(f"Parsed {len(glabels)} global labels, {len(labels)} local labels, {len(powers)} power symbols.")

# Let's inspect labels around U6 (90.17, 161.29) and U7 (157.48, 160.02)
def find_labels_around(center_x, center_y, radius=35):
    found = []
    for g, x, y in glabels:
        if abs(x - center_x) <= radius and abs(y - center_y) <= radius:
            found.append((g, 'global', x, y))
    for l, x, y in labels:
        if abs(x - center_x) <= radius and abs(y - center_y) <= radius:
            found.append((l, 'local', x, y))
    for p, x, y in powers:
        if abs(x - center_x) <= radius and abs(y - center_y) <= radius:
            found.append((p, 'power', x, y))
    return found

print("\n--- LABELS AROUND U6 (Encoder 1 / Left) ---")
for item in find_labels_around(90.17, 161.29):
    print(f"  {item[0]:15s} | {item[1]:7s} | ({item[2]}, {item[3]})")

print("\n--- LABELS AROUND U7 (Encoder 2 / Right) ---")
for item in find_labels_around(157.48, 160.02):
    print(f"  {item[0]:15s} | {item[1]:7s} | ({item[2]}, {item[3]})")

print("\n--- LABELS AROUND U1 (STM32 MCU) ---")
for item in find_labels_around(59.69, 72.39, radius=45):
    print(f"  {item[0]:15s} | {item[1]:7s} | ({item[2]}, {item[3]})")

print("\n--- LABELS AROUND U5 (5V Regulator) ---")
for item in find_labels_around(158.75, 95.25):
    print(f"  {item[0]:15s} | {item[1]:7s} | ({item[2]}, {item[3]})")

print("\n--- LABELS AROUND U4 (3.3V Regulator) ---")
for item in find_labels_around(208.28, 109.22):
    print(f"  {item[0]:15s} | {item[1]:7s} | ({item[2]}, {item[3]})")

print("\n--- LABELS AROUND J1 & SW1 (Battery & Power Switch) ---")
for item in find_labels_around(115.0, 106.0):
    print(f"  {item[0]:15s} | {item[1]:7s} | ({item[2]}, {item[3]})")
