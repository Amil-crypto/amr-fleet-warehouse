import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json


class DashboardNode(Node):

    def __init__(self):
        super().__init__('dashboard_node')

        self.positions = {
            i: {'x': 0.0, 'y': 0.0, 'status': 'UNKNOWN'}
            for i in range(1, 7)
        }

        self.subscription = self.create_subscription(
            String,
            '/fleet/world_poses',
            self.pose_callback,
            10
        )

        self.timer = self.create_timer(1.0, self.display_dashboard)

        self.get_logger().info(
            'FLEET DASHBOARD NODE ACTIVE'
        )

    def pose_callback(self, msg):

        try:
            data = json.loads(msg.data)

            for robot_id in range(1, 7):

                name = str(robot_id)

                if name in data:

                    pose = data[name]

                    self.positions[robot_id]['x'] = pose.get('x', 0.0)
                    self.positions[robot_id]['y'] = pose.get('y', 0.0)
                    self.positions[robot_id]['status'] = 'ACTIVE'

        except Exception as e:
            self.get_logger().warning(
                f'Pose parsing error: {e}'
            )

    def display_dashboard(self):

        print('\n' + '=' * 65)
        print('          EDGE AI AMR FLEET DASHBOARD')
        print('=' * 65)

        print(
            f"{'ROBOT':<10}"
            f"{'X':>10}"
            f"{'Y':>10}"
            f"{'STATUS':>15}"
        )

        print('-' * 65)

        for robot_id in range(1, 7):

            p = self.positions[robot_id]

            print(
                f"Robot {robot_id:<3}"
                f"{p['x']:>10.2f}"
                f"{p['y']:>10.2f}"
                f"{p['status']:>15}"
            )

        print('=' * 65)


def main(args=None):

    rclpy.init(args=args)

    node = DashboardNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
