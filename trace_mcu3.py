import re
from collections import defaultdict

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Extract all wires
wires = []
wire_matches = re.finditer(r'\(wire[\s\S]*?\(pts[\s\S]*?\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)[\s\S]*?\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', text)
for m in wire_matches:
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    wires.append(((round(x1, 2), round(y1, 2)), (round(x2, 2), round(y2, 2))))

print(f"Extracted {len(wires)} wires.")

# Extract all global labels
glabels = []
g_matches = re.finditer(r'\(global_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text)
for m in g_matches:
    name, x, y = m.group(1), float(m.group(2)), float(m.group(3))
    glabels.append((name, round(x, 2), round(y, 2)))

# Extract power symbols
powers = []
p_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"power:([^"]+)"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text)
for m in p_matches:
    pname, px, py = m.group(1), float(m.group(2)), float(m.group(3))
    powers.append((pname, round(px, 2), round(py, 2)))

p2_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"[^"]+"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)[\s\S]*?\(property\s+"Value"\s+"(\+3\.3V|\+5V|\+BATT|GND|GNDA|VDDA|GNDPWR)"', text)
for pm in p2_matches:
    px, py, pname = float(pm.group(1)), float(pm.group(2)), pm.group(3)
    powers.append((pname, round(px, 2), round(py, 2)))

adj = defaultdict(set)
for p1, p2 in wires:
    adj[p1].add(p2)
    adj[p2].add(p1)

node_labels = defaultdict(set)
for name, x, y in glabels:
    node_labels[(x, y)].add(name)
for pname, x, y in powers:
    node_labels[(x, y)].add(f"PWR:{pname}")

# Get STM32 pin positions
stm_lib_match = re.search(r'\(symbol "MCU_ST_STM32F4:STM32F411CEUx"[\s\S]*?\n  \)', text)
stm_pins = {}
if stm_lib_match:
    stm_body = stm_lib_match.group(0)
    pins = re.findall(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+(\d+)\)[\s\S]*?\(name\s+"([^"]+)"[\s\S]*?\(number\s+"([^"]+)"', stm_body)
    for ptype, px, py, prot, pname, pnum in pins:
        # U1 is at (59.69, 72.39)
        ax = round(59.69 + float(px), 2)
        ay = round(72.39 - float(py), 2)
        stm_pins[pnum] = (pname, ax, ay)

def get_net(start_pt):
    visited = set([start_pt])
    queue = [start_pt]
    nets = set()
    
    # Check close coordinates (+/- 0.5mm)
    def find_close_labels(pt):
        lset = set()
        for (lx, ly), ls in node_labels.items():
            if abs(lx - pt[0]) <= 0.5 and abs(ly - pt[1]) <= 0.5:
                lset.update(ls)
        return lset

    nets.update(find_close_labels(start_pt))
        
    while queue:
        curr = queue.pop(0)
        for nxt in adj[curr]:
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
                nets.update(find_close_labels(nxt))
    return nets

print("\n================ STM32F411CEU6 PIN NET MAP ================")
for pnum in sorted(stm_pins.keys(), key=lambda k: int(k) if k.isdigit() else 999):
    pname, ax, ay = stm_pins[pnum]
    nets = get_net((ax, ay))
    print(f"Pin {pnum:2s} | {pname:15s} | Pos ({ax:6.2f}, {ay:6.2f}) | Net: {', '.join(nets) if nets else 'NC'}")

print("\n================ U6 (MT6701 - Left Encoder) PIN NET MAP ================")
# U6 is at (90.17, 161.29)
mt_lib_match = re.search(r'\(symbol "Sensor_Magnetic:MT6701CT"[\s\S]*?\n  \)', text)
if mt_lib_match:
    mt_body = mt_lib_match.group(0)
    mpins = re.findall(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+(\d+)\)[\s\S]*?\(name\s+"([^"]+)"[\s\S]*?\(number\s+"([^"]+)"', mt_body)
    for ptype, px, py, prot, pname, pnum in mpins:
        ax = round(90.17 + float(px), 2)
        ay = round(161.29 - float(py), 2)
        nets = get_net((ax, ay))
        print(f"U6 Pin {pnum:2s} | {pname:15s} | Pos ({ax:6.2f}, {ay:6.2f}) | Net: {', '.join(nets) if nets else 'NC'}")

print("\n================ U7 (MT6701 - Right Encoder) PIN NET MAP ================")
if mt_lib_match:
    for ptype, px, py, prot, pname, pnum in mpins:
        ax = round(157.48 + float(px), 2)
        ay = round(160.02 - float(py), 2)
        nets = get_net((ax, ay))
        print(f"U7 Pin {pnum:2s} | {pname:15s} | Pos ({ax:6.2f}, {ay:6.2f}) | Net: {', '.join(nets) if nets else 'NC'}")
