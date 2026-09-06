with open('minichinh.kicad_sch', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'global_label' in line or 'label' in line:
        print(f"L{idx+1}: {line.strip()}")
    if 'symbol' in line and ('"U1"' in line or '"U4"' in line or '"U5"' in line or '"U6"' in line or '"U7"' in line):
        print(f"L{idx+1}: {line.strip()}")
