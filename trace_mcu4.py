import re
from collections import defaultdict

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# 1. Extract all wires
wires = []
wire_matches = re.finditer(r'\(wire[\s\S]*?\(pts[\s\S]*?\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)[\s\S]*?\(xy\s+([\d\.\-]+)\s+([\d\.\-]+)\)', text)
for m in wire_matches:
    x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
    wires.append(((round(x1, 2), round(y1, 2)), (round(x2, 2), round(y2, 2))))

# 2. Extract global labels
glabels = []
g_matches = re.finditer(r'\(global_label\s+"([^"]+)"[\s\S]*?\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text)
for m in g_matches:
    name, x, y = m.group(1), float(m.group(2)), float(m.group(3))
    glabels.append((name, round(x, 2), round(y, 2)))

# 3. Extract power symbols & power properties
powers = []
p_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"power:([^"]+)"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)', text)
for m in p_matches:
    powers.append((m.group(1), round(float(m.group(2)), 2), round(float(m.group(3)), 2)))

p2_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"[^"]+"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)[\s\S]*?\(property\s+"Value"\s+"(\+3\.3V|\+5V|\+BATT|GND|GNDA|VDDA|GNDPWR)"', text)
for pm in p2_matches:
    powers.append((pm.group(3), round(float(pm.group(1)), 2), round(float(pm.group(2)), 2)))

adj = defaultdict(set)
for p1, p2 in wires:
    adj[p1].add(p2)
    adj[p2].add(p1)

node_labels = defaultdict(set)
for name, x, y in glabels:
    node_labels[(x, y)].add(name)
for pname, x, y in powers:
    node_labels[(x, y)].add(f"{pname}")

def get_net(start_pt):
    visited = set([start_pt])
    queue = [start_pt]
    nets = set()
    
    def find_close_labels(pt):
        lset = set()
        for (lx, ly), ls in node_labels.items():
            if abs(lx - pt[0]) <= 0.6 and abs(ly - pt[1]) <= 0.6:
                lset.update(ls)
        return lset

    nets.update(find_close_labels(start_pt))
        
    while queue:
        curr = queue.pop(0)
        # also check close points in adj graph
        for graph_pt in adj:
            if abs(graph_pt[0] - curr[0]) <= 0.2 and abs(graph_pt[1] - curr[1]) <= 0.2:
                for nxt in adj[graph_pt]:
                    if nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)
                        nets.update(find_close_labels(nxt))
    return nets

# Function to parse symbol pins for a given ref
def trace_symbol(ref_id, center_x, center_y, lib_pattern):
    print(f"\n================ NETS FOR {ref_id} (Center: {center_x}, {center_y}) ================")
    # Find all pin definitions matching lib_pattern
    # (symbol "MCU_ST_STM32F4:STM32F411CEUx_1_1" ... (pin ... (at X Y R) ... (name "...") (number "1")))
    pattern = r'\(symbol\s+"' + re.escape(lib_pattern) + r'[^"]*"[\s\S]*?\n  \)'
    sym_blocks = re.findall(pattern, text)
    
    pins_found = []
    for sb in sym_blocks:
        pins = re.findall(r'\(pin\s+(\w+)\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+(\d+)\)[\s\S]*?\(name\s+"([^"]+)"[\s\S]*?\(number\s+"([^"]+)"', sb)
        for ptype, px, py, prot, pname, pnum in pins:
            ax = round(center_x + float(px), 2)
            ay = round(center_y - float(py), 2)
            pins_found.append((pnum, pname, ax, ay, ptype))

    pins_found.sort(key=lambda item: int(item[0]) if item[0].isdigit() else 999)
    for pnum, pname, ax, ay, ptype in pins_found:
        nets = get_net((ax, ay))
        net_str = ', '.join(sorted(list(nets))) if nets else 'NC / Direct Wire'
        print(f"Pin {pnum:4s} | {pname:15s} | Pos ({ax:6.2f}, {ay:6.2f}) | Nets: {net_str}")

trace_symbol('U1', 59.69, 72.39, 'MCU_ST_STM32F4:STM32F411CEUx')
trace_symbol('U4', 208.28, 109.22, 'Regulator_Linear:TPS73633DBV')
trace_symbol('U5', 158.75, 95.25, 'TPS76850QD:TPS76850QD')
trace_symbol('U6', 90.17, 161.29, 'Sensor_Magnetic:MT6701CT')
trace_symbol('U7', 157.48, 160.02, 'Sensor_Magnetic:MT6701CT')
trace_symbol('U2', 175.26, 50.8, 'Driver_Motor:DRV8833PW')
