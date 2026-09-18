import json
import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class SafetySupervisor(Node):

    def __init__(self):
        super().__init__('safety_supervisor')

        self.robot_ids = [1, 2, 3, 4, 5, 6]

        # Actual Gazebo world positions
        self.positions = {
            i: None for i in self.robot_ids
        }

        self.desired_cmd = {
            i: Twist() for i in self.robot_ids
        }

        self.cmd_publishers = {}

        # Robots that are currently waiting
        self.blocked = {
            i: False for i in self.robot_ids
        }

        # Receive actual Gazebo world coordinates
        self.create_subscription(
            String,
            '/fleet/world_poses',
            self.world_pose_callback,
            10
        )

        # Receive desired commands from Mission Manager
        for i in self.robot_ids:

            self.create_subscription(
                Twist,
                f'/robot{i}/cmd_vel_desired',
                lambda msg, robot=i:
                    self.cmd_callback(msg, robot),
                10
            )

            self.cmd_publishers[i] = self.create_publisher(
                Twist,
                f'/robot{i}/cmd_vel',
                10
            )

        self.timer = self.create_timer(
            0.1,
            self.safety_loop
        )

        self.get_logger().info(
            'SPATIAL MUTEX SAFETY SUPERVISOR ACTIVE'
        )

    def world_pose_callback(self, msg):

        try:
            data = json.loads(msg.data)

            for robot in self.robot_ids:

                key = str(robot)

                if key in data:

                    self.positions[robot] = [
                        float(data[key]['x']),
                        float(data[key]['y'])
                    ]

        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            self.get_logger().warn(
                'Invalid world pose message received'
            )

    def cmd_callback(self, msg, robot):

        self.desired_cmd[robot] = msg

    def safety_loop(self):

        for robot in self.robot_ids:

            if self.positions[robot] is None:
                continue

            should_wait = False
            conflict_with = None
            conflict_distance = 999.0

            x1, y1 = self.positions[robot]

            for other in self.robot_ids:

                if self.positions[other] is None:
                    continue

                if robot == other:
                    continue

                x2, y2 = self.positions[other]

                distance = math.hypot(
                    x2 - x1,
                    y2 - y1
                )

                if distance < 0.8:

                    # Lower numbered robot gets priority
                    if robot > other:

                        should_wait = True
                        conflict_with = other
                        conflict_distance = distance
                        break

            if should_wait:

                if not self.blocked[robot]:

                    self.get_logger().warn(
                        f'MUTEX WAIT: Robot {robot} waiting for '
                        f'Robot {conflict_with} '
                        f'({conflict_distance:.2f}m)'
                    )

                self.blocked[robot] = True

                # Stop robot
                self.cmd_publishers[robot].publish(Twist())

            else:

                if self.blocked[robot]:

                    self.get_logger().info(
                        f'MUTEX RELEASE: Robot {robot} can move'
                    )

                self.blocked[robot] = False

                # Forward desired command
                self.cmd_publishers[robot].publish(
                    self.desired_cmd[robot]
                )


def main(args=None):

    rclpy.init(args=args)

    node = SafetySupervisor()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
