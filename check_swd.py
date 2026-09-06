import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Search for PA13, PA14, SWD, SWDIO, SWCLK in schematic text
for i, line in enumerate(text.split('\n')):
    if any(k in line for k in ['PA13', 'PA14', 'SWD', 'SWDIO', 'SWCLK', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7']):
        print(f"L{i+1}: {line.strip()}")
