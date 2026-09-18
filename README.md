Edge AI-Based Distributed Fleet Coordination for Autonomous Mobile Robots

A ROS 2 and Gazebo-based project for coordinating multiple Autonomous Mobile Robots (AMRs) in a smart warehouse environment.

The main idea is to make multiple robots work as a coordinated fleet instead of operating independently. The system focuses on mission management, task allocation, real-time robot state monitoring, collision-aware coordination, and lightweight Edge AI-based decision support.

Project Overview

In a warehouse with multiple AMRs, several robots may need to travel through the same aisle or junction at the same time. If every robot operates independently, it can result in congestion, conflicting paths, deadlocks, and inefficient task allocation.

This project explores a distributed fleet coordination approach where robots share their state and coordinate their movements through ROS 2.

The current prototype is being developed and tested using ROS 2 Jazzy and Gazebo Harmonic.

Objectives
Coordinate multiple AMRs inside a warehouse
Monitor the real-time state and position of each robot
Manage and assign missions
Coordinate robots in shared areas
Reduce unnecessary waiting and congestion
Use Edge AI for travel-time prediction
Provide a dashboard for fleet monitoring
Support testing with multiple AMRs
Keep AI-based optimization separate from safety-critical control
System Architecture
Warehouse Mission
       ↓
Mission Manager
       ↓
Task Allocation
       ↓
Edge AI
       ↓
Navigation
       ↓
Fleet Coordination
       ↓
Safety Layer
       ↓
AMR
       ↑
Sensor & Robot State

The main components communicate through ROS 2.

Edge AI

The project includes a lightweight Random Forest Regression model for travel-time prediction.

The model can use features such as:

Distance to target
Robot speed
Nearby robot count
Congestion level
Battery level
Current workload
Task priority

The output is an estimated travel time for a robot.

For example:

Robot 1 → 12.4 seconds
Robot 2 →  7.8 seconds
Robot 3 → 15.1 seconds

These predictions can be used by the task allocation layer when selecting a suitable robot for a mission.

The AI layer is intended for optimization and decision support. Safety-critical movement is handled separately by deterministic control and safety mechanisms.

Multi-AMR Simulation

The repository contains simulated AMR models for:

Robot 1
Robot 2
Robot 3
Robot 4
Robot 5
Robot 6

The simulated robots can include:

Differential-drive mobile base
LiDAR
IMU
Wheel encoder feedback
Odometry
Velocity control

The current demonstration focuses on testing fleet coordination in a simulated warehouse environment.

ROS 2 Communication

ROS 2 is used as the main communication framework between the robots and fleet-level components.

Example topics include:

/robot1/odom
/robot2/odom
/robot3/odom

/robot1/scan
/robot2/scan
/robot3/scan

/robot1/imu
/robot2/imu
/robot3/imu

/robot1/cmd_vel
/robot2/cmd_vel
/robot3/cmd_vel

Robot state and sensor information are continuously published, while movement commands are sent to the individual robots.

ROS 2 uses DDS as its underlying middleware. In a physical deployment, the same software architecture can communicate over the warehouse network.

Fleet Coordination
Spatial Mutex

The Spatial Mutex is used to coordinate access to shared areas.

For example, when two robots approach the same narrow junction, the system can control access to the shared region so that both robots do not attempt to use it at the same time.

It can be used for areas such as:

Narrow aisles
Junctions
Loading areas
Other shared regions

The current implementation also monitors the relative positions of the simulated robots.

Safety Supervisor

The Safety Supervisor provides an additional layer between fleet decisions and robot motion.

The basic flow is:

AI / Task Decision
       ↓
Navigation
       ↓
Fleet Coordination
       ↓
Safety Supervisor
       ↓
Robot Motion

This separation ensures that the AI layer does not directly control safety-critical robot movement.

Fleet Dashboard

The project also includes a web-based dashboard for monitoring the AMR fleet.

The dashboard is designed to provide information such as:

Robot positions
Robot status
Current missions
Task information
Fleet activity
Coordination status

Dashboard files are available in:

dashboard/
Project Structure
amr-fleet-warehouse/
│
├── ai/
│   ├── predict.py
│   ├── train_model.py
│   └── travel_time_model.joblib
│
├── amr_fleet/
│   ├── dashboard_node.py
│   ├── dashboard_server.py
│   ├── dashboard_task_receiver.py
│   ├── fleet_state.py
│   ├── gazebo_pose_bridge.py
│   ├── mission_controller.py
│   ├── mission_manager.py
│   ├── safety_supervisor.py
│   ├── spatial_mutex.py
│   └── travel_time_model.joblib
│
├── config/
│   ├── robot1_bridge.yaml
│   ├── robot2_bridge.yaml
│   └── robot3_bridge.yaml
│
├── dashboard/
│   └── index.html
│
├── launch/
│   └── multi_robot.launch.py
│
├── models/
│   ├── robot1/
│   ├── robot2/
│   ├── robot3/
│   ├── smart_amr/
│   ├── smart_amr_robot1.sdf
│   ├── smart_amr_robot2.sdf
│   ├── smart_amr_robot3.sdf
│   ├── smart_amr_robot4.sdf
│   ├── smart_amr_robot5.sdf
│   └── smart_amr_robot6.sdf
│
├── msg/
│   └── RobotState.msg
│
├── resource/
├── test/
├── package.xml
├── setup.py
├── setup.cfg
└── README.md
Technologies Used
Area	Technology
Operating System	Ubuntu 24.04
Robotics Middleware	ROS 2 Jazzy
Simulation	Gazebo Harmonic
Programming	Python
Robot Models	TurtleBot3-based / Custom AMR
Communication	ROS 2 / DDS
Machine Learning	Scikit-learn
AI Model	Random Forest Regression
Dashboard	HTML / Python
Version Control	Git / GitHub
Requirements
Ubuntu 24.04
ROS 2 Jazzy
Gazebo Harmonic
Python 3
ROS-Gazebo bridge
Scikit-learn
Joblib
Required ROS 2 Python dependencies
Running the Project

Build the workspace:

cd ~/amr_ws
colcon build --symlink-install

Source the workspace:

source ~/amr_ws/install/setup.bash

Launch the simulation:

ros2 launch amr_fleet multi_robot.launch.py

Start the Mission Manager in another terminal:

source ~/amr_ws/install/setup.bash
ros2 run amr_fleet mission_manager

Start the Spatial Mutex:

source ~/amr_ws/install/setup.bash
ros2 run amr_fleet spatial_mutex

Start the Mission Controller:

source ~/amr_ws/install/setup.bash
ros2 run amr_fleet mission_controller
Useful ROS 2 Commands

Check running nodes:

ros2 node list

Check available topics:

ros2 topic list

Check Robot 1 odometry:

ros2 topic echo /robot1/odom

Check Robot 1 velocity commands:

ros2 topic echo /robot1/cmd_vel

Check topic type:

ros2 topic type /robot1/cmd_vel

Check available package executables:

ros2 pkg executables amr_fleet
Current Progress

The following components have been implemented or prototyped:

ROS 2 communication
Gazebo multi-robot simulation
3-AMR coordination testing
Six AMR simulation models
Mission Manager
Mission Controller
Spatial Mutex
Safety Supervisor
Gazebo pose bridge
Edge AI travel-time model
Fleet dashboard components
Future Improvements

The next stages of development include:

Improved task allocation
Nav2 integration
Better global and local path planning
Dynamic obstacle avoidance
Improved congestion prediction
Larger fleet experiments
More realistic warehouse scenarios
Edge hardware deployment
Physical AMR testing
Evaluation

The system can be evaluated using:

Mission completion time
Average travel time
Collision count
Deadlock occurrences
Robot utilization
Task allocation time
Path efficiency
AI prediction MAE
AI prediction RMSE

These metrics can be used to compare different fleet coordination approaches.

Project Status

This project is an actively developed prototype.

The current system is primarily tested in a ROS 2 + Gazebo simulation environment. Simulation helps validate the software architecture and coordination logic, while physical deployment will require additional hardware and real-world testing.

Author

Amil-crypto

GitHub: https://github.com/Amil-crypto/amr-fleet-warehouse
