import re
from collections import defaultdict

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Extract all labels with positions
labels = []
for m in re.finditer(r'\((label|global_label)\s+"([^"]+)"\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text):
    ltype, name, x, y = m.group(1), m.group(2), float(m.group(3)), float(m.group(4))
    labels.append((name, ltype, x, y))

print(f"Found {len(labels)} labels.")

# Extract all symbol instances with ref, value, position, and pin details
# In KiCad 6+, a symbol instance looks like:
# (symbol (lib_id "...") (at X Y R) ... (property "Reference" "REF" ...) ... (pin "1" (uuid "...")) ...)
symbols = []
# Split by (symbol (lib_id
for sblock in text.split('(symbol (lib_id'):
    if not sblock.strip():
        continue
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', sblock)
    val_m = re.search(r'\(property "Value" "([^"]+)"', sblock)
    at_m = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', sblock)
    
    if ref_m and val_m and at_m:
        ref = ref_m.group(1)
        val = val_m.group(1)
        sx, sy = float(at_m.group(1)), float(at_m.group(2))
        symbols.append({'ref': ref, 'val': val, 'x': sx, 'y': sy, 'block': sblock})

print(f"Found {len(symbols)} symbol instances.")

# Let's inspect symbols of interest: U1, U4, U5, U6, U7, J1, SW1, SW2, SW3, R21, R22, C16, C17, C7
for s in sorted(symbols, key=lambda item: item['ref']):
    if s['ref'] in ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'J1', 'SW1', 'SW2', 'SW3', 'R21', 'R22', 'R1', 'R11', 'R16', 'R17', 'R18', 'R19', 'R20']:
        print(f"Ref: {s['ref']:5s} | Val: {s['val']:15s} | Pos: ({s['x']}, {s['y']})")
        # Find labels near this symbol (within +/- 30mm)
        nearby = [l for l in labels if abs(l[2] - s['x']) < 40 and abs(l[3] - s['y']) < 40]
        for l in nearby:
            print(f"   -> Nearby label: {l[0]} ({l[1]}) at ({l[2]}, {l[3]})")
