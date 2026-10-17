# Let's write an ASCII renderer for each route on a fine grid
# so we can see the exact drawing!

def draw_route(name, route, hint):
    print(f"\n==========================================")
    print(f"Route {name}: {route}")
    print(f"Hint: {hint}")
    
    # 3 rows, 10 columns
    # Let's use a high resolution grid: e.g. 15 rows x 40 cols
    # Row 0: y=0 (Q..P)
    # Row 1: y=7 (A..L)
    # Row 2: y=14 (Z..M)
    
    # Let's map each key to (r, c)
    # Standard stagger:
    key_pos = {
        'Q': (0, 0), 'W': (0, 4), 'E': (0, 8), 'R': (0, 12), 'T': (0, 16), 'Y': (0, 20), 'U': (0, 24), 'I': (0, 28), 'O': (0, 32), 'P': (0, 36),
        'A': (7, 2), 'S': (7, 6), 'D': (7, 10), 'F': (7, 14), 'G': (7, 18), 'H': (7, 22), 'J': (7, 26), 'K': (7, 30), 'L': (7, 34),
        'Z': (14, 4), 'X': (14, 8), 'C': (14, 12), 'V': (14, 16), 'B': (14, 20), 'N': (14, 24), 'M': (14, 28)
    }
    
    grid = [[' ' for _ in range(42)] for _ in range(16)]
    
    # Bresenham line
    coords = [key_pos[c] for c in route]
    for i in range(len(coords) - 1):
        r0, c0 = coords[i]
        r1, c1 = coords[i+1]
        dr = abs(r1 - r0)
        dc = abs(c1 - c0)
        sr = 1 if r0 < r1 else -1
        sc = 1 if c0 < c1 else -1
        err = dr - dc
        curr_r, curr_c = r0, c0
        while True:
            if grid[curr_r][curr_c] == ' ':
                grid[curr_r][curr_c] = '#'
            if curr_r == r1 and curr_c == c1:
                break
            e2 = 2 * err
            if e2 > -dc:
                err -= dc
                curr_r += sr
            if e2 < dr:
                err += dr
                curr_c += sc
                
    for c in route:
        r, col = key_pos[c]
        grid[r][col] = c
        
    # Crop grid to bounding box with 1 border
    min_r = min(key_pos[c][0] for c in route)
    max_r = max(key_pos[c][0] for c in route)
    min_c = min(key_pos[c][1] for c in route)
    max_c = max(key_pos[c][1] for c in route)
    
    r_start = max(0, min_r - 1)
    r_end = min(15, max_r + 1)
    c_start = max(0, min_c - 2)
    c_end = min(41, max_c + 2)
    
    for r in range(r_start, r_end + 1):
        line = "".join(grid[r][c_start:c_end+1])
        print(f"  {line}")

routes = [
    ("01", "QAZXC", "Every route leaves a mark."),
    ("02", "ZSEDCSD", "The order was not chosen by accident."),
    ("03", "RGYGB", "Follow where the movement leads."),
    ("04", "TGBNM", "The turns matter as much as the destination."),
    ("05", "CFTGBFG", "A strange path can still have a familiar shape."),
    ("06", "VFRTYHGFB", "Start from the beginning. Do not skip the bends."),
    ("07", "WSXCVFRE", "Some patterns are easier seen than read."),
    ("08", "BHUJMHJ", "What matters is what the route leaves behind."),
    ("09", "XDRFTGB", "Nine routes. One destination."),
    ("10", "YTRFGHNBV", "Every journey has one final turn.")
]

for num, route, hint in routes:
    draw_route(num, route, hint)
