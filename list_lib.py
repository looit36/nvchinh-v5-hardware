import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

symbols_in_lib = re.findall(r'\(symbol "([^"]+)"', text)
print("Symbols in lib:", set(symbols_in_lib))
