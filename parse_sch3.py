import re
from collections import defaultdict
import math

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# 1. Parse lib_symbols to find pin relative positions & names
# (symbol "Sensor_Magnetic:MT6701CT" ... (pin passive line (at X Y R) ... (name "..." ...) (number "1" ...)))
lib_pins = defaultdict(dict) # lib_id -> pin_num -> (x, y, name, type)

# Extract lib_symbols section
lib_sec_match = re.search(r'\(lib_symbols([\s\S]*?)\n  \)', text)
if lib_sec_match:
    lib_sec = lib_sec_match.group(1)
    # find symbols in lib_sec
    # (symbol "NAME" ... )
    sym_blocks = re.findall(r'\(symbol "([^"]+)"([\s\S]*?)(?=\(symbol "|^\s*\)$)', lib_sec)
    for sym_name, sym_body in sym_blocks:
        # find pins
        pin_matches = re.finditer(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+(\d+)\)[\s\S]*?\(name\s+"([^"]+)"[\s\S]*?\(number\s+"([^"]+)"', sym_body)
        for pm in pin_matches:
            ptype, px, py, prot, pname, pnum = pm.group(1), float(pm.group(2)), float(pm.group(3)), int(pm.group(4)), pm.group(5), pm.group(6)
            lib_pins[sym_name][pnum] = (px, py, pname, prot, ptype)

print(f"Loaded pin definitions for {len(lib_pins)} library symbols.")

# Helper to rotate pin offset
def rotate_point(x, y, rot):
    # KiCad rotations: 0, 90, 180, 270 (in degrees counter-clockwise or clockwise)
    # In KiCad schematic: 0: (x,y), 90: (-y, x), 180: (-x, -y), 270: (y, -x)
    rad = math.radians(rot)
    rx = x * math.cos(rad) - y * math.sin(rad)
    ry = x * math.sin(rad) + y * math.cos(rad)
    return round(rx, 2), round(ry, 2)

# 2. Parse instances
# (symbol (lib_id "...") (at X Y R) ... (property "Reference" "U7" ...) ...)
instances = []
inst_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"([^"]+)"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\)[\s\S]*?\(property\s+"Reference"\s+"([^"]+)"[\s\S]*?\(property\s+"Value"\s+"([^"]+)"', text)

instance_pins = [] # (ref, val, pin_num, pin_name, abs_x, abs_y)

for im in inst_matches:
    lib_id, sx, sy, srot, ref, val = im.group(1), float(im.group(2)), float(im.group(3)), int(float(im.group(4))), im.group(5), im.group(6)
    instances.append((ref, val, lib_id, sx, sy, srot))
    
    # Calculate absolute pin positions
    if lib_id in lib_pins:
        for pnum, (px, py, pname, prot, ptype) in lib_pins[lib_id].items():
            rx, ry = rotate_point(px, py, srot)
            # In KiCad schematic, Y axis goes downwards
            # wait, rotate_point with KiCad standard angles:
            # Let's check KiCad transformation:
            # rot 0: (sx + px, sy - py) or (sx + px, sy + py)? In KiCad (at X Y R), pin at relative (px, py) from symbol center.
            # Usually pin endpoint is at sx + rx, sy - ry
            instance_pins.append((ref, val, pnum, pname, sx, sy, srot, px, py))

print(f"Parsed {len(instances)} schematic symbol instances.")

# Let's inspect U1, U4, U5, U6, U7 properties and pin functions
for ref, val, lib_id, sx, sy, srot in sorted(instances, key=lambda x: x[0]):
    if ref in ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'J1', 'J4', 'J5', 'J6', 'J7', 'SW1', 'SW2', 'SW3']:
        print(f"Symbol: {ref:5s} | Val: {val:15s} | Lib: {lib_id:30s} | Pos: ({sx}, {sy}, rot={srot})")

