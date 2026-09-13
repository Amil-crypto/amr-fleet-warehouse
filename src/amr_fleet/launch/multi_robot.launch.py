import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    turtlebot3_gazebo = FindPackageShare('turtlebot3_gazebo')

    gazebo_launch = os.path.join(
        '/opt/ros/jazzy/share/turtlebot3_gazebo',
        'launch',
        'turtlebot3_world.launch.py'
    )

    model_base = '/home/amil/amr_ws/src/amr_fleet/models'

    config_base = '/home/amil/amr_ws/src/amr_fleet/config'

    return LaunchDescription([

        # Start Gazebo world
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gazebo_launch)
        ),

        # =========================
        # ROBOT 1
        # =========================

        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', 'robot1',
                '-file',
                os.path.join(
                    model_base,
                    'robot1',
                    'model.sdf'
                ),
                '-x', '0.0',
                '-y', '0.0',
                '-z', '0.01'
            ],
            output='screen'
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '--ros-args',
                '-p',
                'config_file:=' + os.path.join(
                    config_base,
                    'robot1_bridge.yaml'
                )
            ],
            output='screen'
        ),

        # =========================
        # ROBOT 2
        # =========================

        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', 'robot2',
                '-file',
                os.path.join(
                    model_base,
                    'robot2',
                    'model.sdf'
                ),
                '-x', '2.0',
                '-y', '0.0',
                '-z', '0.01'
            ],
            output='screen'
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '--ros-args',
                '-p',
                'config_file:=' + os.path.join(
                    config_base,
                    'robot2_bridge.yaml'
                )
            ],
            output='screen'
        ),

        # =========================
        # ROBOT 3
        # =========================

        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', 'robot3',
                '-file',
                os.path.join(
                    model_base,
                    'robot3',
                    'model.sdf'
                ),
                '-x', '-2.0',
                '-y', '0.0',
                '-z', '0.01'
            ],
            output='screen'
        ),

        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=[
                '--ros-args',
                '-p',
                'config_file:=' + os.path.join(
                    config_base,
                    'robot3_bridge.yaml'
                )
            ],
            output='screen'
        ),
    ])



