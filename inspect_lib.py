import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Search all symbol headers in lib_symbols
lib_sec_match = re.search(r'\(lib_symbols([\s\S]*?)\n  \)', text)
if lib_sec_match:
    lib_sec = lib_sec_match.group(1)
    sym_headers = re.findall(r'\(symbol "([^"]+)"', lib_sec)
    print("Library symbols found:", sym_headers[:30])

    # Let's inspect pins of STM32F411CEUx symbol in lib_sec
    for sh in sym_headers:
        if 'STM32' in sh or 'MT6701' in sh or 'TPS' in sh or 'DRV' in sh:
            print(f"\n--- Pins for symbol {sh} ---")
            m = re.search(r'\(symbol "' + re.escape(sh) + r'"([\s\S]*?)(?=\n    \(symbol|\n  \))', lib_sec)
            if m:
                pins = re.findall(r'\(pin\s+\w+\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)\s+\d+\)[\s\S]*?\(name\s+"([^"]+)"[\s\S]*?\(number\s+"([^"]+)"', m.group(1))
                for px, py, pname, pnum in pins:
                    print(f"  Pin {pnum:4s} | {pname:15s} at offset ({px}, {py})")
