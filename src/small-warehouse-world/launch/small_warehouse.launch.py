import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():

    warehouse_dir = get_package_share_directory(
        'aws_robomaker_small_warehouse_world'
    )

    world = LaunchConfiguration('world')

    declare_world = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(
            warehouse_dir,
            'worlds',
            'small_warehouse',
            'small_warehouse.world'
        ),
        description='Path to the warehouse world'
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': ['-r ', world]
        }.items()
    )

    return LaunchDescription([
        declare_world,
        gazebo
    ])
