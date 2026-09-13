import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import String


class SpatialMutex(Node):

    def __init__(self):
        super().__init__('spatial_mutex')

        self.robot_names = ['robot1', 'robot2', 'robot3']

        self.spawn_offsets = {
            'robot1': {'x': 0.0, 'y': 0.0},
            'robot2': {'x': 2.0, 'y': 0.0},
            'robot3': {'x': -2.0, 'y': 0.0}
        }

        self.positions = {}

        for robot in self.robot_names:
            self.positions[robot] = {
                'x': 0.0,
                'y': 0.0,
                'received': False
            }

        self.clearance_publishers = {}
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

            self.clearance_publishers[robot] = self.create_publisher(
                String,
                f'/{robot}/mutex_clearance',
                10
            )

            self.get_logger().info(
                f'Subscribed to {topic}'
            )

        self.timer = self.create_timer(
            0.5,
            self.check_distances
        )

        self.get_logger().info(
            'Spatial Mutex started'
        )

    def odom_callback(self, msg, robot_name):

        self.positions[robot_name]['x'] = (
            msg.pose.pose.position.x
            + self.spawn_offsets[robot_name]['x']
        )

        self.positions[robot_name]['y'] = (
            msg.pose.pose.position.y
            + self.spawn_offsets[robot_name]['y']
        )

        self.positions[robot_name]['received'] = True

    def check_distances(self):

        for i in range(len(self.robot_names)):

            for j in range(i + 1, len(self.robot_names)):

                robot_a = self.robot_names[i]
                robot_b = self.robot_names[j]

                state_a = self.positions[robot_a]
                state_b = self.positions[robot_b]

                if not (
                    state_a['received']
                    and state_b['received']
                ):
                    continue

                dx = state_a['x'] - state_b['x']
                dy = state_a['y'] - state_b['y']

                distance = math.sqrt(
                    dx * dx + dy * dy
                )

                self.get_logger().info(
                    f'Distance {robot_a} ↔ {robot_b}: '
                    f'{distance:.2f} m'
                )

                if distance < 0.60:

                    self.get_logger().warn(
                        f'{robot_a} and {robot_b} '
                        f'are too close: '
                        f'{distance:.2f} m'
                    )

                    self.publish_clearance(
                        robot_a,
                        'WAIT'
                    )

                    self.publish_clearance(
                        robot_b,
                        'WAIT'
                    )

                else:

                    self.publish_clearance(
                        robot_a,
                        'CLEAR'
                    )

                    self.publish_clearance(
                        robot_b,
                        'CLEAR'
                    )

    def publish_clearance(self, robot, state):

        msg = String()
        msg.data = state

        self.clearance_publishers[robot].publish(msg)


def main(args=None):

    rclpy.init(args=args)

    node = SpatialMutex()

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
