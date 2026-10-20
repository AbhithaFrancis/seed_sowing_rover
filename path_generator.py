"""Field layout and zigzag coverage path for the seed sowing rover."""

CELL = 0.5                      # metres per grid cell
COLS, ROWS = 20, 18             # arena size in cells
STRIP_ROWS = [14, 11, 8, 5, 2]  # 5 crop rows; first = nearest the godown (bottom)
FIRST_COL, LAST_COL = 4, 15     # each row covers 12 cells
SPACING = 2                     # plant one seed every 2 cells
START = (4, 17)                 # (column, row) of the start / godown pad


def build_cells():
    """Return the path as a list of (col, row, is_plant_point)."""
    cells = [(START[0], START[1], False)]
    for i, row in enumerate(STRIP_ROWS):
        cols = list(range(FIRST_COL, LAST_COL + 1))
        if i % 2 == 1:               # every second row is travelled right to left
            cols.reverse()
        for k, col in enumerate(cols):
            cells.append((col, row, k % SPACING == 0))
    return cells


def to_xy(col, row):
    """Cell to metres, relative to START, y pointing up."""
    x = (col - START[0]) * CELL
    y = (START[1] - row) * CELL
    return x, y


def show_map(cells):
    grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]
    for col, row, plant in cells:
        if (col, row) == START:
            grid[row][col] = 'S'
        elif plant:
            grid[row][col] = 'P'
        else:
            grid[row][col] = '#'
    for line in grid:
        print(''.join(line))


if __name__ == "__main__":
    cells = build_cells()
    show_map(cells)
    plants = [c for c in cells if c[2]]
    print()
    print("waypoints:", len(cells), "  plant points:", len(plants))
