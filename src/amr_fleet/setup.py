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
            'mission_controller = amr_fleet.mission_controller:main',
        ],
    },
)
