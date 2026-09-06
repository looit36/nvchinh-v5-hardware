import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Search all Resistors R1..R22
# match (symbol (lib_id "Device:R"...) ... (property "Reference" "R..." ...) (property "Value" "..." ...))
res_matches = re.finditer(r'\(symbol\s+\(lib_id\s+"(?:Device:R|R_[^"]+)"\)\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)[\s\S]*?\(property\s+"Reference"\s+"([^"]+)"[\s\S]*?\(property\s+"Value"\s+"([^"]+)"', text)

print("--- RESISTOR CONNECTIONS ---")
for rm in res_matches:
    rx, ry, ref, val = float(rm.group(1)), float(rm.group(2)), rm.group(3), rm.group(4)
    print(f"Resistor {ref:5s} | Value: {val:10s} | Pos: ({rx}, {ry})")
