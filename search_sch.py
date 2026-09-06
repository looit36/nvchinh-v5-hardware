import re

with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print("--- SEARCHING FOR SYMBOLS IN MINICHINH.KICAD_SCH ---")

# Let's search all symbol definitions in schematic text
# Match (symbol (lib_id ...) ... (property "Reference" "U6" ...) ...)
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'property "Reference"' in line or 'property "Value"' in line:
        print(f"L{i+1}: {line.strip()}")

print("\n--- SEARCHING FOR LABELS IN SCHEMATIC ---")
for i, line in enumerate(lines):
    if 'label' in line.lower() or 'global_label' in line.lower():
        if any(w in line for w in ['A', 'B', 'VOL', 'SW', 'ENCODER', 'U6', 'U7', 'AL', 'AR', 'BL', 'BR']):
            print(f"L{i+1}: {line.strip()}")
