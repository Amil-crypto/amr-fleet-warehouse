#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry


class SpatialMutex(Node):

    def __init__(self):
        super().__init__('spatial_mutex')

        self.robot_ids = [1, 2, 3, 4, 5, 6]

        self.positions = {
            i: [0.0, 0.0] for i in self.robot_ids
        }

        for i in self.robot_ids:
            self.create_subscription(
                Odometry,
                f'/robot{i}/odom',
                lambda msg, robot=i: self.odom_callback(msg, robot),
                10
            )

        self.timer = self.create_timer(
            0.5,
            self.check_collisions
        )

        self.get_logger().info(
            'Spatial Mutex active for 6 AMRs'
        )

    def odom_callback(self, msg, robot):

        self.positions[robot][0] = msg.pose.pose.position.x
        self.positions[robot][1] = msg.pose.pose.position.y

    def check_collisions(self):

        for i in self.robot_ids:

            for j in self.robot_ids:

                if i >= j:
                    continue

                x1, y1 = self.positions[i]
                x2, y2 = self.positions[j]

                distance = math.hypot(
                    x2 - x1,
                    y2 - y1
                )

                if distance < 1.0:

                    self.get_logger().warn(
                        f'CONFLICT: Robot {i} <-> Robot {j} '
                        f' distance={distance:.2f}m'
                    )


def main(args=None):

    rclpy.init(args=args)

    node = SpatialMutex()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

