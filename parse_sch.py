import re
import sys

def main():
    with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    print("=== SCHEMATIC OVERVIEW ===")
    
    # Hierarchical sheets
    sheets = re.findall(r'\(sheet\s+\(at [^\)]+\)[\s\S]*?\(property "Sheetname" "([^"]+)"[\s\S]*?\(property "FileName" "([^"]+)"', content)
    print(f"Sub-sheets: {sheets}")

    # Symbols / Components
    # In KiCad 6+, (symbol (lib_id "...") (at ...) ... (property "Reference" "...") (property "Value" "..."))
    # Let's extract symbol blocks
    symbol_blocks = re.findall(r'\(symbol\s+[\s\S]*?\n  \)', content)
    print(f"Total symbol blocks: {len(symbol_blocks)}")

    components = []
    # Pattern to extract Ref, Value, Lib
    for block in content.split('(symbol'):
        ref_match = re.search(r'\(property "Reference" "([^"]+)"', block)
        val_match = re.search(r'\(property "Value" "([^"]+)"', block)
        lib_match = re.search(r'\(lib_id "([^"]+)"', block)
        fp_match = re.search(r'\(property "Footprint" "([^"]+)"', block)
        
        if ref_match and val_match:
            ref = ref_match.group(1)
            val = val_match.group(1)
            lib = lib_match.group(1) if lib_match else ""
            fp = fp_match.group(1) if fp_match else ""
            components.append({'ref': ref, 'val': val, 'lib': lib, 'fp': fp, 'block': block})

    print(f"Parsed {len(components)} components.")
    
    print("\n--- Key Components (ICs, Connectors, Diodes, Transistors, Regulators) ---")
    for c in sorted(components, key=lambda x: x['ref']):
        ref = c['ref']
        if not (ref.startswith('C') or ref.startswith('R') or ref.startswith('#')):
            print(f"{ref:8s} | {c['val']:25s} | {c['lib']:30s} | {c['fp']}")

    print("\n--- Capacitors & Resistors summary ---")
    caps = [c for c in components if c['ref'].startswith('C')]
    res = [c for c in components if c['ref'].startswith('R')]
    print(f"Total capacitors: {len(caps)}")
    for c in sorted(caps, key=lambda x: x['ref']):
        print(f"  {c['ref']:6s} : {c['val']}")
    print(f"Total resistors: {len(res)}")
    for r in sorted(res, key=lambda x: x['ref']):
        print(f"  {r['ref']:6s} : {r['val']}")

    # Search for pins of MCU (STM32)
    print("\n--- STM32 MCU Details ---")
    stm32_comp = [c for c in components if 'STM32' in c['val'].upper() or 'MCU' in c['val'].upper() or 'U' in c['ref']]
    for mcu in stm32_comp:
        print(f"MCU component: {mcu['ref']} - {mcu['val']}")

    # Labels and Global Labels
    labels = re.findall(r'\((?:label|global_label)\s+"([^"]+)"', content)
    unique_labels = sorted(list(set(labels)))
    print("\n--- Labels & Net Names ---")
    for l in unique_labels:
        print(f"  - {l}")

if __name__ == '__main__':
    main()
