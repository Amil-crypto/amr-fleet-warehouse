from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'amr_fleet'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'msg'),
            glob('msg/*.msg')
        ),
        (
            os.path.join('lib', package_name), ['amr_fleet/travel_time_model.joblib']
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='amil',
    maintainer_email='amil@todo.todo',
    description='AMR Fleet Coordination System',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'fleet_state = amr_fleet.fleet_state:main',
            'spatial_mutex = amr_fleet.spatial_mutex:main',
            'mission_manager = amr_fleet.mission_manager:main',
            'dashboard_task_receiver = amr_fleet.dashboard_task_receiver:main',
            'dashboard_server = amr_fleet.dashboard_server:main',
            'mission_controller = amr_fleet.mission_controller:main',
            'safety_supervisor = amr_fleet.safety_supervisor:main',
            'gazebo_pose_bridge = amr_fleet.gazebo_pose_bridge:main',
            'dashboard_node = amr_fleet.dashboard_node:main',
        ],
    },
)
