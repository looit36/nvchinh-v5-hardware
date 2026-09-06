import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    sch_text = f.read()

# Print symbol blocks for U1, U4, U5, U6, U7, SW1, J1
symbol_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"([^"]+)"\)[\s\S]*?\(property "Reference" "([^"]+)"[\s\S]*?\n  \)', sch_text)

for m in symbol_matches:
    lib_id = m.group(1)
    ref = m.group(2)
    if ref in ['U1', 'U4', 'U5', 'U6', 'U7', 'J1', 'SW1', 'SW2', 'SW3', 'J4', 'J5', 'J6', 'J7', 'R21', 'R22']:
        print(f"\n================ SYMBOL {ref} ({lib_id}) ================")
        block = m.group(0)
        # find properties
        props = re.findall(r'\(property "([^"]+)" "([^"]+)"', block)
        for p_name, p_val in props:
            if p_name in ['Reference', 'Value', 'Footprint']:
                print(f"  Property: {p_name} = {p_val}")
        # find pins inside symbol
        pins = re.findall(r'\(pin "([^"]+)" \(uuid "([^"]+)"\)\)', block)
        print(f"  Pins count: {len(pins)}")

# Let's inspect iremitter.kicad_sch if it exists
try:
    with open('iremitter.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
        ir_text = f.read()
    print("\n--- iremitter.kicad_sch components ---")
    ir_symbols = re.findall(r'\(property "Reference" "([^"]+)"[\s\S]*?\(property "Value" "([^"]+)"', ir_text)
    for r, v in ir_symbols:
        print(f"  {r}: {v}")
except Exception as e:
    print(f"Could not read iremitter.kicad_sch: {e}")
