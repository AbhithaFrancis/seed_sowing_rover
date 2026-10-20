"""Graphical (Tkinter) dashboard: status, counters, seed stock, battery and field map."""
import json
import tkinter as tk
import rclpy
from std_msgs.msg import String
from seed_rover_control.path_generator import build_cells, CELL, COLS, ROWS, START

PX = 20   # pixels per grid cell on the map

SEED_COLOR = {'A': '#e53935', 'B': '#fdd835', 'C': '#1e88e5'}
SEED_NAME = {'A': 'Seed A (dry soil)', 'B': 'Seed B (normal soil)', 'C': 'Seed C (wet soil)'}
ZONE_BG = {'A': '#e6d3b3', 'B': '#c9a577', 'C': '#9c7a54'}

STATE_TEXT = {
    'DRIVE': 'DRIVING TO NEXT POINT',
    'SOW': 'SOWING',
    'RETURN': 'SEED EMPTY - RETURNING TO GODOWN',
    'REFILL': 'REFILLING AT GODOWN',
    'RESUME': 'RETURNING TO SAVED POSITION',
    'DONE': 'PATH COMPLETE',
}
STATE_COLOR = {
    'DRIVE': '#1565c0', 'SOW': '#2e7d32', 'RETURN': '#ef6c00',
    'REFILL': '#6a1b9a', 'RESUME': '#ef6c00', 'DONE': '#455a64',
}


def zone_of(col):
    wx = (col + 0.5) * CELL
    if wx < 4.0:
        return 'A'
    if wx < 6.0:
        return 'B'
    return 'C'


class Dashboard:
    def __init__(self):
        rclpy.init()
        self.node = rclpy.create_node('rover_dashboard')
        self.latest = None
        self.node.create_subscription(String, '/rover_status', self.on_status, 10)
        self.node.create_subscription(String, '/battery_status', self.on_battery, 10)
        self.power = None
        self.cells = build_cells()

        self.root = tk.Tk()
        self.root.title('Seed Sowing Rover - Monitor')
        self.root.configure(bg='#fafafa')
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.build_ui()
        self.draw_static_map()
        self.poll()

    def on_status(self, msg):
        self.latest = json.loads(msg.data)

    def on_battery(self, msg):
        self.power = json.loads(msg.data)

    def close(self):
        self.node.destroy_node()
        rclpy.shutdown()
        self.root.destroy()

    # ---------- layout ----------
    def build_ui(self):
        r = self.root
        bg = '#fafafa'
        tk.Label(r, text='SOLAR-POWERED AUTONOMOUS SEED SOWING ROVER',
                 font=('Arial', 14, 'bold'), bg=bg).grid(row=0, column=0, columnspan=2, pady=(8, 4))
        self.banner = tk.Label(r, text='Waiting for rover...', font=('Arial', 16, 'bold'),
                               fg='white', bg='#757575', pady=6)
        self.banner.grid(row=1, column=0, columnspan=2, padx=10, pady=4, sticky='ew')

        left = tk.Frame(r, bg=bg)
        left.grid(row=2, column=0, padx=10, pady=6, sticky='n')
        right = tk.Frame(r, bg=bg)
        right.grid(row=2, column=1, padx=10, pady=6)

        self.vals = {}
        names = ['Position', 'Waypoint', 'Soil moisture', 'Selected seed',
                 'Pits formed', 'Successful drops', 'Skipped points', 'Refills']
        for i, name in enumerate(names):
            tk.Label(left, text=name + ':', font=('Arial', 12), bg=bg,
                     anchor='w', width=16).grid(row=i, column=0, sticky='w')
            v = tk.Label(left, text='-', font=('Arial', 12, 'bold'), bg=bg, anchor='w', width=24)
            v.grid(row=i, column=1, sticky='w')
            self.vals[name] = v

        tk.Label(left, text='Seed stock', font=('Arial', 12, 'bold'),
                 bg=bg).grid(row=len(names), column=0, columnspan=2, sticky='w', pady=(12, 2))
        self.bars = {}
        for j, k in enumerate('ABC'):
            tk.Label(left, text=f'Seed {k}', font=('Arial', 12), bg=bg,
                     anchor='w').grid(row=len(names) + 1 + j, column=0, sticky='w')
            c = tk.Canvas(left, width=260, height=24, bg='#eeeeee', highlightthickness=0)
            c.grid(row=len(names) + 1 + j, column=1, sticky='w', pady=2)
            self.bars[k] = c

        tk.Label(left, text='Battery', font=('Arial', 12), bg=bg,
                 anchor='w').grid(row=len(names) + 4, column=0, sticky='w', pady=(10, 2))
        self.batt = tk.Canvas(left, width=260, height=24, bg='#eeeeee', highlightthickness=0)
        self.batt.grid(row=len(names) + 4, column=1, sticky='w', pady=(10, 2))
        tk.Label(left, text='Solar input', font=('Arial', 12), bg=bg,
                 anchor='w').grid(row=len(names) + 5, column=0, sticky='w')
        self.solar_lbl = tk.Label(left, text='-', font=('Arial', 12, 'bold'), bg=bg, anchor='w')
        self.solar_lbl.grid(row=len(names) + 5, column=1, sticky='w')

        tk.Label(right, text='Field map', font=('Arial', 12, 'bold'), bg=bg).pack()
        self.map = tk.Canvas(right, width=COLS * PX, height=ROWS * PX,
                             bg='white', highlightthickness=1, highlightbackground='#999')
        self.map.pack()
        legend = tk.Frame(right, bg=bg)
        legend.pack(pady=4)
        for k, label in (('A', 'dry: Seed A'), ('B', 'moist: Seed B'), ('C', 'wet: Seed C')):
            tk.Label(legend, text=label, bg=ZONE_BG[k], font=('Arial', 9), padx=4).pack(side='left', padx=2)

    def draw_static_map(self):
        for col in range(COLS):
            for row in range(ROWS):
                self.map.create_rectangle(col * PX, row * PX, (col + 1) * PX, (row + 1) * PX,
                                          fill=ZONE_BG[zone_of(col)], outline='#d7ccc8')
        sc, sr = START
        self.map.create_rectangle(sc * PX, sr * PX, (sc + 1) * PX, (sr + 1) * PX,
                                  fill='#fdd835', outline='#f57f17', width=2)
        self.map.create_text(sc * PX + PX // 2, sr * PX + PX // 2, text='G', font=('Arial', 9, 'bold'))
        flat = []
        for c, r, _ in self.cells:
            flat += [(c + 0.5) * PX, (r + 0.5) * PX]
        self.map.create_line(*flat, fill='#5d4037', dash=(3, 3))

    # ---------- updates ----------
    def poll(self):
        rclpy.spin_once(self.node, timeout_sec=0)
        if self.latest is not None:
            s, self.latest = self.latest, None
            self.redraw(s)
        self.root.after(50, self.poll)

    def redraw(self, s):
        st = s['state']
        text = STATE_TEXT.get(st, st)
        if st in ('RETURN', 'REFILL'):
            text += f"  (Seed {s['seed']})"
        self.banner.config(text=text, bg=STATE_COLOR.get(st, '#757575'))
        p = self.power
        if p is not None:
            if p['paused']:
                self.banner.config(text='LOW BATTERY - PAUSED, CHARGING FROM SOLAR', bg='#b71c1c')
            self.batt.delete('all')
            level = p['battery']
            colr = '#43a047' if level > 50 else ('#fb8c00' if level > 25 else '#e53935')
            self.batt.create_rectangle(0, 0, 260 * level / 100.0, 24, fill=colr, outline='')
            self.batt.create_text(130, 12, text=f'{level:.0f} %', font=('Arial', 10, 'bold'))
            self.solar_lbl.config(text=f"sun {p['sun'] * 100:.0f} %   net {p['net'] * 60:+.1f} %/min")

        self.vals['Position'].config(text=f"x = {s['x']:.2f} m,  y = {s['y']:.2f} m")
        self.vals['Waypoint'].config(text=f"{s['waypoint']} / {s['total']}")
        if s['pits'] == 0 and s['moisture'] == 0.0:
            self.vals['Soil moisture'].config(text='-')
            self.vals['Selected seed'].config(text='-')
        else:
            self.vals['Soil moisture'].config(text=f"{s['moisture']:.0f} %")
            self.vals['Selected seed'].config(text=SEED_NAME.get(s['seed'], s['seed']))
        self.vals['Pits formed'].config(text=str(s['pits']))
        self.vals['Successful drops'].config(text=str(s['drops']))
        self.vals['Skipped points'].config(text=str(s['skipped']))
        self.vals['Refills'].config(text=str(s['refills']))

        for k in 'ABC':
            cap = s['capacity'][k]
            val = s['stock'][k]
            c = self.bars[k]
            c.delete('all')
            c.create_rectangle(0, 0, 260 * val / cap, 24, fill=SEED_COLOR[k], outline='')
            c.create_text(130, 12, text='EMPTY' if val == 0 else f'{val} / {cap}',
                          font=('Arial', 10, 'bold'))

        self.map.delete('dyn')
        for i, (col, row, plant) in enumerate(self.cells):
            if not plant:
                continue
            cx, cy = (col + 0.5) * PX, (row + 0.5) * PX
            if i < s['waypoint']:
                self.map.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                                     fill=SEED_COLOR[zone_of(col)], outline='#222', tags='dyn')
            else:
                self.map.create_oval(cx - 4, cy - 4, cx + 4, cy + 4,
                                     fill='', outline='#333', tags='dyn')
        rx = s['x'] / CELL * PX
        ry = (ROWS - s['y'] / CELL) * PX
        self.map.create_oval(rx - 7, ry - 7, rx + 7, ry + 7,
                             fill='#212121', outline='white', width=2, tags='dyn')


def main():
    app = Dashboard()
    app.root.mainloop()


if __name__ == '__main__':
    main()
