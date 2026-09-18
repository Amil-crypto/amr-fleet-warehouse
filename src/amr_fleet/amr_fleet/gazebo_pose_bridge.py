import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import gz.transport
from gz.msgs.pose_v_pb2 import Pose_V
import json


class GazeboPoseBridge(Node):

    def __init__(self):
        super().__init__('gazebo_pose_bridge')

        self.publisher = self.create_publisher(
            String,
            '/fleet/world_poses',
            10
        )

        self.node_gz = gz.transport.Node()

        self.node_gz.subscribe(
            Pose_V,
            '/world/default/dynamic_pose/info',
            self.pose_callback
        )

        self.get_logger().info(
            'GAZEBO WORLD POSE BRIDGE ACTIVE'
        )

    def pose_callback(self, msg):

        robots = {}

        for pose in msg.pose:

            name = pose.name

            if name.startswith('robot') and name[5:].isdigit():

                robot_id = int(name[5:])

                if 1 <= robot_id <= 6:

                    robots[robot_id] = {
                        'x': pose.position.x,
                        'y': pose.position.y,
                        'z': pose.position.z
                    }

        message = String()

        message.data = json.dumps(robots)

        self.publisher.publish(message)


def main(args=None):

    rclpy.init(args=args)

    node = GazeboPoseBridge()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
