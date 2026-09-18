import math
import os

import joblib
import numpy as np
import rclpy

from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import String
import json


class FleetManager(Node):

    def __init__(self):
        super().__init__('fleet_manager')

        self.robot_ids = [1, 2, 3, 4, 5, 6]

        self.positions = {
            i: None for i in self.robot_ids
        }

        self.orientations = {
            i: {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
            for i in self.robot_ids
        }

        self.busy = {
            i: False for i in self.robot_ids
        }

        self.current_tasks = {}
        self.dashboard_tasks = []

        self.blocked_time = {
            i: 0.0 for i in self.robot_ids
        }
        self.last_distance = {
            i: None for i in self.robot_ids
        }

        self.last_time = self.get_clock().now()

        odom_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.cmd_publishers = {}
        self.odom_subscriptions = {}

        for i in self.robot_ids:

            self.cmd_publishers[i] = self.create_publisher(
                Twist,
                f'/robot{i}/cmd_vel_desired',
                10
            )

            self.odom_subscriptions[i] = self.create_subscription(
                Odometry,
                f'/robot{i}/odom',
                lambda msg, robot=i: self.odom_callback(msg, robot),
                10
            )

        model_path = os.path.join(
            os.path.dirname(__file__),
            'travel_time_model.joblib'
        )

        self.model = joblib.load(model_path)

        self.dashboard_task_subscriber = self.create_subscription(
            String,
            '/dashboard/task',
            self.dashboard_task_callback,
            10
        )
        self.tasks = [
            (25.0, 10.0),
            (20.0, -10.0),
            (10.0, 12.0),
            (-10.0, 12.0),
            (-20.0, -10.0),
            (0.0, -12.0),
        ]

        self.timer = self.create_timer(
            0.1,
            self.control_loop
        )

        self.get_logger().info(
            'EDGE AI FLEET MANAGER STARTED'
        )

    def odom_callback(self, msg, robot):

        self.positions[robot] = [
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        ]

        q = msg.pose.pose.orientation

        self.orientations[robot] = {
            'x': q.x,
            'y': q.y,
            'z': q.z,
            'w': q.w
        }

    def predict_time(self, robot, target):

        if self.positions[robot] is None:
            return 9999.0

        x, y = self.positions[robot]

        distance = math.hypot(
            target[0] - x,
            target[1] - y
        )

        nearby = 0

        for other in self.robot_ids:

            if other == robot:
                continue

            if self.positions[other] is None:
                continue

            ox, oy = self.positions[other]

            if math.hypot(
                ox - x,
                oy - y
            ) < 5.0:
                nearby += 1

        congestion = min(
            1.0,
            nearby / 5.0
        )

        features = np.array([[
            distance,
            0.5,
            nearby,
            congestion,
            90,
            0
        ]])

        return float(
            self.model.predict(features)[0]
        )

    def allocate_task(self, target, excluded=None):

        if excluded is None:
            excluded = []

        available = [
            r for r in self.robot_ids
            if not self.busy[r]
            and r not in excluded
            and self.positions[r] is not None
        ]

        if not available:
            return None

        predictions = {}

        for robot in available:
            predictions[robot] = self.predict_time(
                robot,
                target
            )

        best_robot = min(
            predictions,
            key=predictions.get
        )

        self.current_tasks[best_robot] = target
        self.busy[best_robot] = True
        self.blocked_time[best_robot] = 0.0

        self.get_logger().info(
            f'AI ALLOCATION: Robot {best_robot} '
            f'-> {target} | '
            f'Predicted time = '
            f'{predictions[best_robot]:.2f}s'
        )

        return best_robot

    def is_conflicted(self, robot):

        if self.positions[robot] is None:
            return False

        x, y = self.positions[robot]

        for other in self.robot_ids:

            if robot == other:
                continue

            if self.positions[other] is None:
                continue

            ox, oy = self.positions[other]

            distance = math.hypot(
                ox - x,
                oy - y
            )

            if distance < 0.8:
                return True

        return False

    def reassign_task(self, robot):

        if robot not in self.current_tasks:
            return

        target = self.current_tasks[robot]

        self.get_logger().warn(
            f'DYNAMIC REASSIGNMENT: '
            f'Robot {robot} blocked for '
            f'{self.blocked_time[robot]:.1f}s'
        )

        self.busy[robot] = False

        del self.current_tasks[robot]

        self.blocked_time[robot] = 0.0

        new_robot = self.allocate_task(
            target,
            excluded=[robot]
        )

        if new_robot is not None:

            self.get_logger().info(
                f'REASSIGNED: Robot {robot} '
                f'-> Robot {new_robot} '
                f'for task {target}'
            )

    def dashboard_task_callback(self, msg):

        try:
            data = json.loads(msg.data)

            x = float(data['x'])
            y = float(data['y'])

            target = (x, y)

            self.dashboard_tasks.append(target)

            self.get_logger().info(
                f'DASHBOARD TASK RECEIVED: {target}'
            )

        except Exception as e:

            self.get_logger().error(
                f'INVALID DASHBOARD TASK: {e}'
            )
    def control_loop(self):

        now = self.get_clock().now()

        dt = (
            now - self.last_time
        ).nanoseconds / 1e9

        self.last_time = now

        # Wait until all six robots have valid odometry
        if not all(
            self.positions[r] is not None
            for r in self.robot_ids
        ):
            return

        # Allocate dashboard tasks to available robots
        if self.dashboard_tasks:
            for target in self.dashboard_tasks[:]:
                robot = self.allocate_task(target)

                if robot is not None:
                    self.dashboard_tasks.remove(target)
                    self.get_logger().info(
                        f'DASHBOARD AI ALLOCATION: Robot {robot} -> {target}'
                    )

        # Allocate tasks once
        if not self.current_tasks:

            self.get_logger().info(
                'ALL ROBOT ODOMETRY READY - STARTING AI ALLOCATION'
            )

            for target in self.tasks:

                robot = self.allocate_task(target)

                if robot is None:
                    self.get_logger().warn(
                        f'Could not allocate task {target}'
                    )

            self.get_logger().info(
                f'ACTIVE TASKS: {self.current_tasks}'
            )

        # Control every assigned robot
        for robot in self.robot_ids:

            if robot not in self.current_tasks:
                continue

            if self.positions[robot] is None:
                continue

            target = self.current_tasks[robot]

            x, y = self.positions[robot]

            dx = target[0] - x
            dy = target[1] - y

            distance = math.hypot(dx, dy)

            if self.last_distance[robot] is None:
                self.last_distance[robot] = distance

            cmd = Twist()

            # Task completed
            if distance < 0.5:

                self.cmd_publishers[robot].publish(cmd)

                self.get_logger().info(
                    f'Robot {robot} COMPLETED '
                    f'task {target}'
                )

                self.busy[robot] = False
                self.blocked_time[robot] = 0.0

                del self.current_tasks[robot]

                continue

            # Progress monitoring
            distance_change = (
                self.last_distance[robot] - distance
            )

            if distance_change < 0.02:
                self.blocked_time[robot] += dt
            else:
                self.blocked_time[robot] = max(
                    0.0,
                    self.blocked_time[robot] - dt
                )

            self.last_distance[robot] = distance

            if self.blocked_time[robot] >= 30.0:

                self.get_logger().warn(
                    f'Robot {robot} has made limited progress for '
                    f'{self.blocked_time[robot]:.1f}s'
                )

                self.blocked_time[robot] = 0.0

            # Motion control
            q = self.orientations[robot]

            # Convert quaternion to robot yaw
            yaw = math.atan2(
                2.0 * (q['w'] * q['z'] + q['x'] * q['y']),
                1.0 - 2.0 * (q['y']**2 + q['z']**2)
            )

            # Desired heading toward target
            desired_angle = math.atan2(dy, dx)

            # Normalize heading error to [-pi, pi]
            angle_error = desired_angle - yaw

            while angle_error > math.pi:
                angle_error -= 2.0 * math.pi

            while angle_error < -math.pi:
                angle_error += 2.0 * math.pi

            # Smooth proportional controller
            cmd.angular.z = max(
                -0.8,
                min(0.8, 2.0 * angle_error)
            )

            # Move forward when reasonably aligned
            if abs(angle_error) < 0.6:
                cmd.linear.x = min(
                    0.5,
                    0.4 * distance
                )
            else:
                cmd.linear.x = 0.0


            self.cmd_publishers[robot].publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = FleetManager()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
