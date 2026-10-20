# Seed Sowing Rover

Project Overview

The Solar-Powered Autonomous Seed-Sowing Rover is a robotics simulation project designed to demonstrate intelligent and efficient agricultural seed sowing using ROS 2 and Gazebo.

The system simulates an autonomous rover navigating through predefined field rows, selecting suitable seed types based on soil-condition parameters, and monitoring the seed-sowing process through a graphical dashboard. It also incorporates seed inventory monitoring and a refill-and-resume mechanism to handle seed shortages without losing the previously saved sowing position.

Key Features

Autonomous Field Navigation: Simulates rover movement through predefined agricultural rows.

Soil-Based Seed Selection: Selects among three seed types according to simulated soil conditions.

Pit Formation and Seed Dispensing: Simulates pit formation before seed placement.

Seed-Drop Monitoring: Tracks and verifies simulated seed drops.

Seed Stock Management: Monitors the availability of different seed types.

Automatic Refill and Recovery: Simulates returning for replenishment and resuming sowing from a saved position.

Real-Time Monitoring Dashboard: Displays rover position, waypoint progress, soil moisture, selected seed, sowing statistics, seed inventory, battery status, and simulated solar input.

Field Visualization: Represents planting rows and seed positions in a simulated agricultural environment.

Technologies Used

ROS 2 Jazzy

Gazebo Sim

Python

Robot modelling with URDF/Xacro

Graphical monitoring dashboard
