import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's inspect schematic around U6, U7, J4, J5, J6, J7 in detail!
# Let's search for wires/labels around U6 pos (90.17, 161.29) and U7 pos (157.48, 160.02)
lines = text.split('\n')
for idx, line in enumerate(lines):
    if any(k in line for k in ['MT6701', 'STAND_HOST', 'STAND_SLAVE', 'U6', 'U7', 'J4', 'J5', 'J6', 'J7']):
        print(f"L{idx+1}: {line.strip()}")
