import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist


class MissionManager(Node):

    def __init__(self):
        super().__init__('mission_manager')

        self.robot_names = ['robot1', 'robot2', 'robot3']

        self.positions = {
            'robot1': {'x': 0.0, 'y': 0.0},
            'robot2': {'x': 2.0, 'y': 0.0},
            'robot3': {'x': -2.0, 'y': 0.0}
        }

        self.targets = {
            'robot1': {'x': 0.0, 'y': 3.0},
            'robot2': {'x': 2.0, 'y': 3.0},
            'robot3': {'x': -2.0, 'y': 3.0}
        }

        self.received = {
            'robot1': False,
            'robot2': False,
            'robot3': False
        }

        self.cmd_publishers = {}

        for robot in self.robot_names:

            odom_topic = f'/{robot}/odom'
            cmd_topic = f'/{robot}/cmd_vel'

            self.create_subscription(
                Odometry,
                odom_topic,
                lambda msg, name=robot:
                self.odom_callback(msg, name),
                10
            )

            self.cmd_publishers[robot] = self.create_publisher(
                Twist,
                cmd_topic,
                10
            )

            self.get_logger().info(
                f'Connected to {odom_topic}'
            )

        self.timer = self.create_timer(
            0.1,
            self.control_loop
        )

        self.get_logger().info(
            'Mission Manager started'
        )

    def odom_callback(self, msg, robot_name):

        self.positions[robot_name]['x'] = (
            msg.pose.pose.position.x
        )

        self.positions[robot_name]['y'] = (
            msg.pose.pose.position.y
        )

        self.received[robot_name] = True

    def control_loop(self):

        for robot in self.robot_names:

            if not self.received[robot]:
                continue

            x = self.positions[robot]['x']
            y = self.positions[robot]['y']

            target_x = self.targets[robot]['x']
            target_y = self.targets[robot]['y']

            dx = target_x - x
            dy = target_y - y

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            cmd = Twist()

            if distance > 0.15:

                cmd.linear.x = 0.5

                if abs(dy) > 0.2:
                    cmd.angular.z = 0.5

            else:

                cmd.linear.x = 0.0
                cmd.angular.z = 0.0

                self.get_logger().info(
                    f'{robot} reached target'
                )

            self.cmd_publishers[robot].publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = MissionManager()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
