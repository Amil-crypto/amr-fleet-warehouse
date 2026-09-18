import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class DashboardTaskReceiver(Node):

    def __init__(self):
        super().__init__('dashboard_task_receiver')

        self.subscription = self.create_subscription(
            String,
            '/dashboard/task',
            self.task_callback,
            10
        )

        self.get_logger().info(
            'DASHBOARD TASK RECEIVER ACTIVE'
        )

    def task_callback(self, msg):

        self.get_logger().info(
            f'NEW DASHBOARD TASK: {msg.data}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = DashboardTaskReceiver()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
