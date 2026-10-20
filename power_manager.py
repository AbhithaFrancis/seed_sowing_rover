"""Simulated solar panel and battery. Publishes /battery_status and tells the
rover to pause and charge when the battery is low."""
import json
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# ---- simulation parameters (battery is in %, rates in % per second) ----
DAY = 600.0            # seconds for the sun to go dawn -> dusk (one simulated day)
SUN_START = 0.10       # start shortly after dawn (0 = dawn, 0.5 = noon)
SOLAR_MAX = 0.10       # panel output at full sun
START_BATTERY = 70.0
LOW = 20.0             # pause and charge below this level
RESUME_AT = 35.0       # carry on again above this level
IDLE = 0.010
LOADS = {'DRIVE': 0.060, 'SOW': 0.080, 'RETURN': 0.060,
         'RESUME': 0.060, 'REFILL': 0.020, 'DONE': 0.010}
DT = 0.2               # update period in seconds


class PowerManager(Node):
    def __init__(self):
        super().__init__('power_manager')
        self.battery = START_BATTERY
        self.t = 0.0
        self.state = 'IDLE'
        self.paused = False
        self.create_subscription(String, '/rover_status', self.status_cb, 10)
        self.pub = self.create_publisher(String, '/battery_status', 10)
        self.create_timer(DT, self.step)
        self.get_logger().info(f'Power manager started. Battery {self.battery:.0f}%')

    def status_cb(self, msg):
        self.state = json.loads(msg.data)['state']

    def step(self):
        self.t += DT
        phase = (self.t / DAY + SUN_START) % 1.0
        sun = max(0.0, math.sin(math.pi * phase))        # 0 at dawn/dusk, 1 at noon
        solar = SOLAR_MAX * sun
        load = IDLE if self.paused else LOADS.get(self.state, IDLE)
        net = solar - load
        self.battery = min(100.0, max(0.0, self.battery + net * DT))

        if not self.paused and self.battery <= LOW:
            self.paused = True
            self.get_logger().warn(f'Battery low ({self.battery:.0f}%): rover paused, charging')
        elif self.paused and self.battery >= RESUME_AT:
            self.paused = False
            self.get_logger().info(f'Battery {self.battery:.0f}%: rover resumes')

        msg = String()
        msg.data = json.dumps({
            'battery': round(self.battery, 2), 'sun': round(sun, 3),
            'solar': round(solar, 4), 'load': round(load, 4),
            'net': round(net, 4), 'paused': self.paused,
        })
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = PowerManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
