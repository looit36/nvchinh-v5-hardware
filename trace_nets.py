import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's extract wire and label positions, or net connections.
# In KiCad 6+, schematic has (symbol ... (uuid ...) (property "Reference" "...") ... (pin "1" (uuid ...))) or connections are made by wires/labels.
# Alternatively, minichinh.net (netlist file) or minichinh.kicad_sch net connections can be parsed easily!
# Let's check if minichinh.net exists and is up to date!

try:
    with open('minichinh.net', 'r', encoding='utf-8', errors='ignore') as f:
        net_text = f.read()
    print("--- NETLIST PARSING ---")
    
    # Netlist format: (net (code "...") (name "...") (node (ref "...") (pin "...")) ...)
    nets = re.findall(r'\(net\s+\(code\s+"?\d+"?\)\s+\(name\s+"([^"]+)"\)([\s\S]*?)\n\s*\)', net_text)
    
    net_map = {}
    for name, nodes_str in nets:
        nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)(?:\s+\(pinfunction\s+"([^"]+)"\))?', nodes_str)
        net_map[name] = nodes

    # Print MCU pins (U1)
    print("\n=== U1 (STM32F411CEUx) PIN CONNECTIONS ===")
    mcu_pins = []
    for net_name, nodes in net_map.items():
        for ref, pin, *rest in nodes:
            if ref == 'U1':
                pfunc = rest[0] if rest and rest[0] else ""
                mcu_pins.append((int(pin) if pin.isdigit() else pin, pin, pfunc, net_name, nodes))

    mcu_pins.sort(key=lambda x: x[0] if isinstance(x[0], int) else 999)
    for num, pin, pfunc, net_name, nodes in mcu_pins:
        other_nodes = [f"{r}:{p}" for r, p, *rest in nodes if r != 'U1']
        print(f"Pin {pin:4s} | Net: {net_name:20s} | Function: {pfunc:15s} | Connected to: {', '.join(other_nodes)}")

    print("\n=== ENCODER U6 (MT6701 - Left/Right?) CONNECTIONS ===")
    for net_name, nodes in net_map.items():
        for ref, pin, *rest in nodes:
            if ref == 'U6':
                other_nodes = [f"{r}:{p}" for r, p, *rest in nodes if r != 'U6']
                print(f"U6 Pin {pin:4s} | Net: {net_name:20s} | Connected to: {', '.join(other_nodes)}")

    print("\n=== ENCODER U7 (MT6701 - Left/Right?) CONNECTIONS ===")
    for net_name, nodes in net_map.items():
        for ref, pin, *rest in nodes:
            if ref == 'U7':
                other_nodes = [f"{r}:{p}" for r, p, *rest in nodes if r != 'U7']
                print(f"U7 Pin {pin:4s} | Net: {net_name:20s} | Connected to: {', '.join(other_nodes)}")

    print("\n=== POWER & REGULATOR CONNECTIONS ===")
    for u in ['U4', 'U5', 'J1', 'SW1']:
        print(f"\n--- Connections for {u} ---")
        for net_name, nodes in net_map.items():
            for ref, pin, *rest in nodes:
                if ref == u:
                    other_nodes = [f"{r}:{p}" for r, p, *rest in nodes if r != u]
                    print(f"{u} Pin {pin:4s} | Net: {net_name:20s} | Connected to: {', '.join(other_nodes)}")

except Exception as e:
    print(f"Error parsing netlist: {e}")
