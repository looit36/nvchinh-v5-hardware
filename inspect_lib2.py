import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's search all occurrence of symbol definitions in lib_symbols
# (symbol "MCU_ST_STM32F4:STM32F411CEUx" ...
matches = re.finditer(r'\(symbol\s+"([^"]+)"[\s\S]*?\n  \)', text)
for m in matches:
    name = m.group(1)
    if any(k in name for k in ['STM32', 'MT6701', 'TPS', 'DRV', 'BMI']):
        print(f"\nFound symbol: {name}")
        body = m.group(0)
        pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+(\d+)\)[\s\S]*?\(name\s+"([^"]+)"[\s\S]*?\(number\s+"([^"]+)"', body)
        for px, py, prot, pname, pnum in pins:
            print(f"   Pin {pnum:4s} | {pname:15s} | Offset ({px}, {py}) | Rot: {prot}")
