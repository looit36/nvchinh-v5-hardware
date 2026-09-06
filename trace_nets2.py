import re

with open('minichinh.net', 'r', encoding='utf-8', errors='ignore') as f:
    net_text = f.read()

# Let's search for (net (code "...") (name "...")
net_blocks = net_text.split('(net ')

net_map = {}
for block in net_blocks[1:]:
    name_m = re.search(r'\(name "([^"]+)"\)', block)
    if name_m:
        net_name = name_m.group(1)
        nodes = re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)(?:\s+\(pinfunction "([^"]+)"\))?', block)
        net_map[net_name] = nodes

print(f"Parsed {len(net_map)} nets.")

def show_comp_nets(comp_ref):
    print(f"\n=================== CONNECTIONS FOR {comp_ref} ===================")
    comp_pins = []
    for net_name, nodes in net_map.items():
        for ref, pin, pfunc in nodes:
            if ref == comp_ref:
                comp_pins.append((pin, pfunc, net_name, nodes))
    
    # Sort pins numerically if possible
    def sort_key(p):
        try:
            return int(p[0])
        except:
            return 999
            
    comp_pins.sort(key=sort_key)
    for pin, pfunc, net_name, nodes in comp_pins:
        others = [f"{r}:{p}" for r, p, pf in nodes if r != comp_ref]
        print(f"Pin {pin:4s} | {pfunc:15s} | Net: {net_name:25s} | Connected to: {', '.join(others)}")

show_comp_nets('U1') # STM32F411CEU6
show_comp_nets('U6') # MT6701 #1
show_comp_nets('U7') # MT6701 #2
show_comp_nets('U4') # TPS73633 (3.3V LDO)
show_comp_nets('U5') # TPS76850 (5V LDO)
show_comp_nets('U2') # DRV8833
show_comp_nets('U3') # BMI160
show_comp_nets('J1') # Power input / battery connector
