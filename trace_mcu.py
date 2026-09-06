import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's find wires and global_labels connected to U1 symbol pins.
# First, find U1 symbol block in schematic:
u1_match = re.search(r'\(symbol\s+\(lib_id\s+"MCU_ST_STM32F4:STM32F411CEUx"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+([\d\.\-]+)\)[\s\S]*?\n  \)', text)

if u1_match:
    u1_x, u1_y = float(u1_match.group(1)), float(u1_match.group(2))
    print(f"U1 is at ({u1_x}, {u1_y})")

# Let's extract all global_labels with coordinates
glabels = []
for m in re.finditer(r'\(global_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+(\d+)\)', text):
    name, x, y, rot = m.group(1), float(m.group(2)), float(m.group(3)), int(m.group(4))
    glabels.append((name, x, y, rot))

# Let's extract all wires (wire (pts (xy X1 Y1) (xy X2 Y2)))
wires = []
for m in re.finditer(r'\(wire\s+\(pts\s+\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)\s+\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)\)', text):
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    wires.append(((x1, y1), (x2, y2)))

print(f"Extracted {len(wires)} wires.")

# Let's find lib symbol pins for STM32F411CEUx
# Match in lib_symbols
stm_lib_match = re.search(r'\(symbol "MCU_ST_STM32F4:STM32F411CEUx"[\s\S]*?\n  \)', text)
if stm_lib_match:
    stm_body = stm_lib_match.group(0)
    pins = re.findall(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+(\d+)\)[\s\S]*?\(name\s+"([^"]+)"[\s\S]*?\(number\s+"([^"]+)"', stm_body)
    print(f"Found {len(pins)} MCU pins in library.")
    
    # Calculate absolute coordinates for each pin
    # For U1 at (59.69, 72.39), rot=0: abs_x = 59.69 + px, abs_y = 72.39 - py
    pin_coords = {}
    for ptype, px, py, prot, pname, pnum in pins:
        ax = round(59.69 + float(px), 2)
        ay = round(72.39 - float(py), 2) # KiCad Y goes down in sch, lib pin Y goes up
        pin_coords[pnum] = (pname, ax, ay, ptype)

    # Now let's trace from each pin coordinate along wires to find connected labels/symbols!
    # Build graph of connected points
    from collections import defaultdict
    adj = defaultdict(set)
    for (x1, y1), (x2, y2) in wires:
        pt1 = (round(x1, 2), round(y1, 2))
        pt2 = (round(x2, 2), round(y2, 2))
        adj[pt1].add(pt2)
        adj[pt2].add(pt1)

    # Match labels to graph points
    label_pts = {}
    for name, x, y, rot in glabels:
        label_pts[(round(x, 2), round(y, 2))] = name

    # Also power symbols
    power_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"power:([^"]+)"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\)', text)
    for pm in power_matches:
        pname, px, py = pm.group(1), float(pm.group(2)), float(pm.group(3))
        label_pts[(round(px, 2), round(py, 2))] = f"POWER_{pname}"

    print("\n================ EXACT U1 PIN MAPPING ================")
    for pnum in sorted(pin_coords.keys(), key=lambda k: int(k) if k.isdigit() else 999):
        pname, ax, ay, ptype = pin_coords[pnum]
        
        # BFS to find connected labels
        start_pt = (ax, ay)
        visited = set([start_pt])
        queue = [start_pt]
        found_nets = set()
        
        # Check if direct label at pin
        if start_pt in label_pts:
            found_nets.add(label_pts[start_pt])

        while queue:
            curr = queue.pop(0)
            for nxt in adj[curr]:
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)
                    if nxt in label_pts:
                        found_nets.add(label_pts[nxt])

        print(f"Pin {pnum:2s} | {pname:15s} | Pos ({ax:6.2f}, {ay:6.2f}) | Nets: {', '.join(found_nets) if found_nets else 'NC'}")
