import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


DASHBOARD_DIR = os.path.expanduser(
    "~/amr_ws/src/amr_fleet/dashboard"
)


class DashboardNode(Node):

    def __init__(self):
        super().__init__("dashboard_server")

        self.task_publisher = self.create_publisher(
            String,
            "/dashboard/task",
            10
        )

        self.get_logger().info(
            "DASHBOARD ROS 2 SERVER ACTIVE"
        )

    def publish_task(self, task):

        msg = String()
        msg.data = json.dumps(task)

        self.task_publisher.publish(msg)

        self.get_logger().info(
            f"TASK SENT: {msg.data}"
        )


node = None


class DashboardHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/":

            file_path = os.path.join(
                DASHBOARD_DIR,
                "index.html"
            )

            try:
                with open(file_path, "rb") as file:
                    content = file.read()

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "text/html"
                )
                self.end_headers()

                self.wfile.write(content)

            except Exception as e:

                self.send_error(
                    500,
                    str(e)
                )

        else:

            self.send_error(404)

    def do_POST(self):

        if self.path != "/task":
            self.send_error(404)
            return

        try:

            length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(length)

            task = json.loads(body.decode("utf-8"))

            node.publish_task(task)

            response = {
                "message":
                "Task successfully sent to ROS 2."
            }

            data = json.dumps(response).encode()

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Content-Length",
                str(len(data))
            )

            self.end_headers()

            self.wfile.write(data)

        except Exception as e:

            self.send_error(
                400,
                str(e)
            )

    def log_message(self, format, *args):
        pass


def main():

    global node

    rclpy.init()

    node = DashboardNode()

    server = HTTPServer(
        ("0.0.0.0", 8000),
        DashboardHandler
    )

    print("DASHBOARD SERVER: http://localhost:8000")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        pass

    server.server_close()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
