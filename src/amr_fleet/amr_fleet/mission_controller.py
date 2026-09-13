import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class MissionController(Node):

    def __init__(self):
        super().__init__('mission_controller')

        self.robots = ['robot1', 'robot2', 'robot3']

        self.positions = {
            'robot1': {'x': 0.0, 'y': 0.0, 'yaw': 0.0},
            'robot2': {'x': 0.0, 'y': 0.0, 'yaw': 0.0},
            'robot3': {'x': 0.0, 'y': 0.0, 'yaw': 0.0}
        }

        self.targets = {
            'robot1': {'x': 1.0, 'y': 0.0},
            'robot2': {'x': 2.0, 'y': 1.0},
            'robot3': {'x': -2.0, 'y': 1.0}
        }

        self.received = {
            'robot1': False,
            'robot2': False,
            'robot3': False
        }

        self.reached = {
            'robot1': False,
            'robot2': False,
            'robot3': False
        }

        self.cmd_publishers = {}

        for robot in self.robots:

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
                f'Subscribed to {odom_topic}'
            )

        self.timer = self.create_timer(
            0.1,
            self.control_loop
        )

        self.get_logger().info(
            'Mission Controller started'
        )

    def odom_callback(self, msg, robot):

        self.positions[robot]['x'] = msg.pose.pose.position.x
        self.positions[robot]['y'] = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        sin_yaw = 2.0 * (
            q.w * q.z + q.x * q.y
        )

        cos_yaw = 1.0 - 2.0 * (
            q.y * q.y + q.z * q.z
        )

        self.positions[robot]['yaw'] = math.atan2(
            sin_yaw,
            cos_yaw
        )

        self.received[robot] = True

    def normalize_angle(self, angle):

        while angle > math.pi:
            angle -= 2.0 * math.pi

        while angle < -math.pi:
            angle += 2.0 * math.pi

        return angle

    def control_loop(self):

        for robot in self.robots:

            if not self.received[robot]:
                continue

            if self.reached[robot]:
                self.stop_robot(robot)
                continue

            x = self.positions[robot]['x']
            y = self.positions[robot]['y']
            yaw = self.positions[robot]['yaw']

            target_x = self.targets[robot]['x']
            target_y = self.targets[robot]['y']

            dx = target_x - x
            dy = target_y - y

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            target_angle = math.atan2(
                dy,
                dx
            )

            angle_error = self.normalize_angle(
                target_angle - yaw
            )

            cmd = Twist()

            if distance < 0.15:

                self.reached[robot] = True

                self.stop_robot(robot)

                self.get_logger().info(
                    f'{robot} reached target '
                    f'({target_x:.2f}, {target_y:.2f})'
                )

                continue

            if abs(angle_error) > 0.15:

                cmd.linear.x = 0.0
                cmd.angular.z = max(
                    -0.8,
                    min(0.8, 1.5 * angle_error)
                )

            else:

                cmd.linear.x = min(
                    0.4,
                    0.5 * distance
                )

                cmd.angular.z = max(
                    -0.5,
                    min(0.5, 1.0 * angle_error)
                )

            self.cmd_publishers[robot].publish(cmd)

    def stop_robot(self, robot):

        cmd = Twist()

        cmd.linear.x = 0.0
        cmd.linear.y = 0.0
        cmd.linear.z = 0.0

        cmd.angular.x = 0.0
        cmd.angular.y = 0.0
        cmd.angular.z = 0.0

        self.cmd_publishers[robot].publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = MissionController()

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
