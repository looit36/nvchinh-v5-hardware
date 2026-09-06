import pcbnew
import math

def group_components(board):
    # Dictionaries to hold components
    mcu = ['U1', 'Y2', 'SW1', 'C3', 'C4', 'C5']
    motor = ['U2', 'J2', 'J3', 'L2', 'L3', 'C18', 'C19', 'C20', 'C23', 'C21', 'C22', 'C14', 'C13']
    imu = ['U3', 'C7']
    power = ['U4', 'J1', 'L1', 'D5', 'R6', 'C16', 'NT1', 'NT2']
    
    # Centers
    centers = {
        'MCU': (200, 160),
        'MOTOR': (200, 175),
        'IMU': (200, 150),
        'POWER': (200, 185)
    }
    
    groups = {'MCU': mcu, 'MOTOR': motor, 'IMU': imu, 'POWER': power}
    
    fps = board.GetFootprints()
    for fp in fps:
        ref = fp.GetReference()
        
        # Check which group it belongs to
        my_group_name = None
        for gname, glist in groups.items():
            if ref in glist:
                my_group_name = gname
                break
                
        if my_group_name:
            # Simple grid placement around the center
            idx = groups[my_group_name].index(ref)
            cols = 4
            row = idx // cols
            col = idx % cols
            
            cx, cy = centers[my_group_name]
            # Spacing 6mm
            x = cx + (col - cols/2.0) * 6
            y = cy + (row) * 6
            
            fp.SetPosition(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6)))

board = pcbnew.LoadBoard('minichinh.kicad_pcb')
group_components(board)
pcbnew.SaveBoard('minichinh.kicad_pcb', board)
print('Successfully organized components!')
