import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's find all symbol definitions in lib_symbols
# Format: (symbol "NAME_0_1" ... or "NAME_1_1" ...)
symbol_blocks = text.split('(symbol "')

pins_by_symbol = {}

for block in symbol_blocks[1:]:
    name_end = block.find('"')
    if name_end == -1:
        continue
    sym_name = block[:name_end]
    
    # Extract pins inside this block
    # (pin ptype line (at X Y R) ... (name "...") ... (number "..."))
    pin_matches = re.finditer(r'\(pin\s+\w+\s+\w+[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\)[\s\S]*?\(name\s+"([^"]+)"[\s\S]*?\(number\s+"([^"]+)"', block)
    
    pins = []
    for pm in pin_matches:
        px, py, prot, pname, pnum = float(pm.group(1)), float(pm.group(2)), int(float(pm.group(3))), pm.group(4), pm.group(5)
        pins.append((pnum, pname, px, py, prot))
        
    if pins:
        pins_by_symbol[sym_name] = pins

print("Parsed pin definitions for symbols:", list(pins_by_symbol.keys()))

# Let's map instances:
# (symbol (lib_id "...") (at X Y R) ... (property "Reference" "REF" ...))
instances = []
inst_blocks = text.split('(symbol\n')
if len(inst_blocks) == 1:
    inst_blocks = text.split('(symbol ')

for b in inst_blocks[1:]:
    if 'property "Reference"' not in b:
        continue
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', b)
    val_m = re.search(r'\(property "Value" "([^"]+)"', b)
    lib_m = re.search(r'\(lib_id "([^"]+)"', b)
    at_m = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\)', b)
    if not at_m:
        at_m = re.search(r'\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\)', b)
        srot = 0
    else:
        srot = int(float(at_m.group(3)))

    if ref_m and val_m and at_m:
        ref = ref_m.group(1)
        val = val_m.group(1)
        lib_id = lib_m.group(1) if lib_m else ""
        sx, sy = float(at_m.group(1)), float(at_m.group(2))
        instances.append((ref, val, lib_id, sx, sy, srot))

print(f"Parsed {len(instances)} instances.")

# Extract wires
wires = []
wire_matches = re.finditer(r'\(wire[\s\S]*?\(pts[\s\S]*?\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)[\s\S]*?\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', text)
for m in wire_matches:
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    wires.append(((round(x1, 2), round(y1, 2)), (round(x2, 2), round(y2, 2))))

# Extract labels & power symbols
labels = {}
for m in re.finditer(r'\((?:global_label|label)\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text):
    labels[(round(float(m.group(2)), 2), round(float(m.group(3)), 2))] = m.group(1)

for m in re.finditer(r'\(symbol\s+\(lib_id\s+"power:([^"]+)"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text):
    labels[(round(float(m.group(2)), 2), round(float(m.group(3)), 2))] = m.group(1)

for m in re.finditer(r'\(symbol\s+\(lib_id\s+"[^"]+"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)[\s\S]*?\(property\s+"Value"\s+"(\+3\.3V|\+5V|\+BATT|GND|GNDA|VDDA|GNDPWR)"', text):
    labels[(round(float(m.group(1)), 2), round(float(m.group(2)), 2))] = m.group(3)

# Build graph
from collections import defaultdict
adj = defaultdict(set)
for p1, p2 in wires:
    adj[p1].add(p2)
    adj[p2].add(p1)

def find_net(start_pt):
    visited = set([start_pt])
    queue = [start_pt]
    found = set()
    
    def check_pt(pt):
        f = set()
        for (lx, ly), lval in labels.items():
            if abs(lx - pt[0]) <= 0.8 and abs(ly - pt[1]) <= 0.8:
                f.add(lval)
        return f

    found.update(check_pt(start_pt))
    while queue:
        curr = queue.pop(0)
        # Search neighbors in graph
        for g_pt in adj:
            if abs(g_pt[0] - curr[0]) <= 0.3 and abs(g_pt[1] - curr[1]) <= 0.3:
                for nxt in adj[g_pt]:
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)
                        found.update(check_pt(nxt))
    return found

# Print pin net map for target ICs
for ref, val, lib_id, sx, sy, srot in sorted(instances, key=lambda x: x[0]):
    if ref in ['U1', 'U2', 'U3', 'U4', 'U5', 'U6', 'U7', 'J1', 'SW1']:
        print(f"\n================ NET MAP FOR {ref} ({val}) ================")
        # Find matching symbol in pins_by_symbol
        # lib_id format e.g. "MCU_ST_STM32F4:STM32F411CEUx" -> target symbol "STM32F411CEUx_0_1" or "STM32F411CEUx_1_1"
        target_base = lib_id.split(':')[-1]
        all_pins = []
        for sname, pins in pins_by_symbol.items():
            if sname.startswith(target_base) or target_base in sname:
                all_pins.extend(pins)
                
        # Sort pins
        all_pins.sort(key=lambda item: int(item[0]) if item[0].isdigit() else 999)
        for pnum, pname, px, py, prot in all_pins:
            # calculate pin absolute location based on symbol rotation srot
            # KiCad rotation:
            if srot == 0:
                ax, ay = sx + px, sy - py
            elif srot == 90:
                ax, ay = sx - py, sy - px
            elif srot == 180:
                ax, ay = sx - px, sy + py
            elif srot == 270:
                ax, ay = sx + py, sy + px
            else:
                ax, ay = sx + px, sy - py
                
            ax, ay = round(ax, 2), round(ay, 2)
            nets = find_net((ax, ay))
            print(f"Pin {pnum:4s} | {pname:15s} | Pos ({ax:6.2f}, {ay:6.2f}) | Nets: {', '.join(sorted(list(nets))) if nets else 'NC'}")
