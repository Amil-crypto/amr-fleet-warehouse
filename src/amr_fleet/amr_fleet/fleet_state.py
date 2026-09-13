import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class FleetState(Node):

    def __init__(self):
        super().__init__('fleet_state')

        self.robot_names = [
            'robot1',
            'robot2',
            'robot3'
        ]

        self.spawn_offsets = {
            'robot1': {
                'x': 0.0,
                'y': 0.0
            },
            'robot2': {
                'x': 2.0,
                'y': 0.0
            },
            'robot3': {
                'x': -2.0,
                'y': 0.0
            }
        }

        self.fleet = {}

        for robot in self.robot_names:
            self.fleet[robot] = {
                'x': 0.0,
                'y': 0.0,
                'local_x': 0.0,
                'local_y': 0.0,
                'vx': 0.0,
                'vy': 0.0,
                'received': False
            }

        self.subscribers = []

        for robot in self.robot_names:
            topic = f'/{robot}/odom'

            subscriber = self.create_subscription(
                Odometry,
                topic,
                lambda msg, name=robot:
                self.odom_callback(msg, name),
                10
            )

            self.subscribers.append(subscriber)

            self.get_logger().info(
                f'Subscribed to {topic}'
            )

        self.timer = self.create_timer(
            1.0,
            self.check_fleet
        )

        self.get_logger().info(
            'Fleet State + Collision Monitor started'
        )

    def odom_callback(self, msg, robot_name):

        local_x = msg.pose.pose.position.x
        local_y = msg.pose.pose.position.y

        self.fleet[robot_name]['local_x'] = local_x
        self.fleet[robot_name]['local_y'] = local_y

        offset_x = self.spawn_offsets[robot_name]['x']
        offset_y = self.spawn_offsets[robot_name]['y']

        world_x = local_x + offset_x
        world_y = local_y + offset_y

        self.fleet[robot_name]['x'] = world_x
        self.fleet[robot_name]['y'] = world_y

        self.fleet[robot_name]['vx'] = (
            msg.twist.twist.linear.x
        )

        self.fleet[robot_name]['vy'] = (
            msg.twist.twist.linear.y
        )

        self.fleet[robot_name]['received'] = True

    def check_fleet(self):

        self.get_logger().info(
            '========== FLEET STATE =========='
        )

        for robot in self.robot_names:

            state = self.fleet[robot]

            if state['received']:

                self.get_logger().info(
                    f'{robot}: '
                    f'World Position=('
                    f'{state["x"]:.2f}, '
                    f'{state["y"]:.2f}) '
                    f'Velocity=('
                    f'{state["vx"]:.2f}, '
                    f'{state["vy"]:.2f})'
                )

            else:

                self.get_logger().warn(
                    f'{robot}: Waiting for odometry'
                )

        for i in range(len(self.robot_names)):

            for j in range(i + 1, len(self.robot_names)):

                robot_a = self.robot_names[i]
                robot_b = self.robot_names[j]

                state_a = self.fleet[robot_a]
                state_b = self.fleet[robot_b]

                if not (
                    state_a['received']
                    and state_b['received']
                ):
                    continue

                dx = (
                    state_a['x']
                    - state_b['x']
                )

                dy = (
                    state_a['y']
                    - state_b['y']
                )

                distance = math.sqrt(
                    dx * dx + dy * dy
                )

                self.get_logger().info(
                    f'Distance '
                    f'{robot_a} ↔ {robot_b}: '
                    f'{distance:.2f} m'
                )

                if distance < 0.60:

                    self.get_logger().error(
                        f'⚠️ COLLISION WARNING: '
                        f'{robot_a} and {robot_b} '
                        f'are {distance:.2f} m apart!'
                    )

                elif distance < 1.00:

                    self.get_logger().warn(
                        f'⚠️ CAUTION: '
                        f'{robot_a} and {robot_b} '
                        f'are {distance:.2f} m apart.'
                    )

    def destroy_node(self):

        self.get_logger().info(
            'Fleet State Manager stopped'
        )

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = FleetState()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
