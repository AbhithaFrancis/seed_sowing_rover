"""Text-mode monitor: shows the rover status in a terminal."""
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from seed_rover_control.path_generator import build_cells, CELL, COLS, ROWS

BAR = 20

STATE_TEXT = {
    'DRIVE': 'DRIVING TO NEXT POINT',
    'SOW': 'SOWING',
    'RETURN': 'RETURNING TO GODOWN (seed empty)',
    'REFILL': 'REFILLING AT GODOWN',
    'RESUME': 'RETURNING TO SAVED POSITION',
    'DONE': 'PATH COMPLETE',
}


def bar(value, cap):
    n = int(BAR * value / cap) if cap else 0
    return '#' * n + '-' * (BAR - n)


class Monitor(Node):
    def __init__(self):
        super().__init__('rover_monitor')
        self.cells = build_cells()
        self.create_subscription(String, '/rover_status', self.cb, 10)
        print('Waiting for /rover_status ...')

    def cb(self, msg):
        s = json.loads(msg.data)

        grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]
        for i, (col, row, plant) in enumerate(self.cells):
            if i < s['waypoint']:
                grid[row][col] = '*' if plant else '='
            else:
                grid[row][col] = 'o' if plant else '-'
        col = min(COLS - 1, max(0, int(s['x'] / CELL)))
        row = min(ROWS - 1, max(0, ROWS - 1 - int(s['y'] / CELL)))
        grid[row][col] = 'R'

        lines = []
        lines.append('=== SEED SOWING ROVER MONITOR ===')
        lines.append(f"Status    : {STATE_TEXT.get(s['state'], s['state'])}"
                     f"   (waypoint {s['waypoint']}/{s['total']})")
        lines.append(f"Position  : x={s['x']:.2f} m   y={s['y']:.2f} m")
        lines.append(f"Soil      : moisture {s['moisture']:.0f}%   Seed: {s['seed']}")
        lines.append(f"Pits      : {s['pits']}    Successful drops: {s['drops']}    Skipped: {s['skipped']}")
        lines.append(f"Refills   : {s['refills']}")
        lines.append('Seed stock:')
        for k in ('A', 'B', 'C'):
            cap = s['capacity'][k]
            lines.append(f"  {k} [{bar(s['stock'][k], cap)}] {s['stock'][k]:>2}/{cap}")
        lines.append('')
        lines.append('R = rover   * = sown   o = still to sow   = and - = path')
        for g in grid:
            lines.append(''.join(g))

        print('\033[H\033[J' + '\n'.join(lines), flush=True)


def main():
    rclpy.init()
    node = Monitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
