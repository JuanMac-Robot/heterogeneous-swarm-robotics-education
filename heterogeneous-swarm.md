# Heterogeneous Swarm

The final objective of the project is to integrate the aerial and ground swarms into a cooperative heterogeneous robotic system.

The main challenge is that the two swarms are fundamentally different.

## Ground Swarm

The ground swarm uses:

- ESP32-controlled robots
- ArUco markers
- Overhead camera localization
- Ground robot motion control
- Wi-Fi or RF communication

## Aerial Swarm

The aerial swarm uses:

- Crazyflie drones
- Lighthouse localization
- Crazyradio communication
- Autonomous flight control
- Multi-drone swarm algorithms

## Main Integration Challenge

The two swarms use different:

- Localization systems
- Communication systems
- Motion dynamics
- Control architectures
- Operating spaces

The ground robots primarily move in two dimensions, while the aerial robots move in three dimensions.

For this reason, the heterogeneous system will require a coordination layer that allows both swarms to operate under a common mission.

## Proposed Architecture

The general system will follow this structure:

Mission Manager

↓

Heterogeneous Swarm Coordination Layer

↓

Aerial Swarm Controller + Ground Swarm Controller

↓

Crazyflie System + ESP32 Ground Robot System

## Common Coordinate System

The ArUco localization system and the Lighthouse localization system initially operate using different coordinate systems.

One of the integration objectives will be to transform the positions of both systems into a common mission coordinate frame.

This will allow the system to understand the relative position of every robot.

## Cooperative Behaviors

Possible heterogeneous swarm behaviors include:

- Shared navigation
- Aerial scout and ground follower
- Coordinated formations
- Cooperative search
- Formation transitions
- Coordinated arrival at a target
- Search and rescue missions

## Final Objective

The final system should demonstrate that aerial and ground robots can cooperate during a common mission while maintaining safe and coordinated swarm behavior.

---

[← Back to Home](index.md)
