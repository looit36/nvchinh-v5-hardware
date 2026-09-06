import re

with open('minichinh.net', 'r', encoding='utf-8', errors='ignore') as f:
    net_text = f.read()

net_blocks = net_text.split('(net ')
net_map = {}
for block in net_blocks[1:]:
    name_m = re.search(r'\(name "([^"]+)"\)', block)
    if name_m:
        net_name = name_m.group(1)
        nodes = re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)(?:\s+\(pinfunction "([^"]+)"\))?', block)
        net_map[net_name] = nodes

def print_all_pins(ref):
    print(f"\n=================== ALL PINS FOR {ref} ===================")
    pins = []
    for net_name, nodes in net_map.items():
        for r, p, pf in nodes:
            if r == ref:
                pins.append((p, pf, net_name, nodes))
    
    def key_fn(item):
        try:
            return (0, int(item[0]))
        except:
            return (1, item[0])
            
    pins.sort(key=key_fn)
    for p, pf, net_name, nodes in pins:
        others = [f"{r}:{pin}" for r, pin, pfunc in nodes if r != ref]
        print(f"Pin {p:4s} | Function: {(pf or ''):15s} | Net: {net_name:25s} | Connections: {', '.join(others)}")

print_all_pins('U1')
print_all_pins('U5')
print_all_pins('U6')
print_all_pins('U7')
