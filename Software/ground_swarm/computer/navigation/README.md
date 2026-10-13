# Ground Robot Navigation

This section introduces the fundamental concepts used for autonomous navigation of the ground robots.

The tutorials should be completed in order.

---

## Tutorial 1 – Single Agent Navigation with One Obstacle

This tutorial introduces the basic navigation model used throughout the project.

The agent navigates toward a single goal while avoiding one obstacle using:

- Goal attraction
- Sigmoid obstacle repulsion
- 360-degree sensing
- Resultant-force navigation
- Path visualization

### Files

[Python Program – Single Agent / Single Obstacle](One_Agent_One_Goal_One_obstacle.py)

[Word Tutorial – Single Agent Navigation](Tutorial_Single_Agent_Navigation_English.pdf)

### Learning Objective

After completing this tutorial, students should understand how attractive and repulsive forces can be combined to generate autonomous navigation.

---

## Tutorial 2 – Single Agent Navigation with Multiple Obstacles

This tutorial extends the concepts introduced in Tutorial 1.

Instead of considering only one obstacle, the environment now contains multiple obstacles. The agent detects the obstacles within its sensing range and selects the nearest obstacle to calculate the repulsive force.

The navigation system includes:

- Goal attraction
- Multiple obstacles
- Individual sigmoid parameters for each obstacle
- 360-degree sensing
- Nearest-obstacle selection
- Obstacle repulsion
- Path visualization

### Files

[Python Program – Multiple Obstacles](single_agent_multiple_obstacles.py)

[Word Tutorial – Multiple Obstacle Navigation](Tutorial_Multi_Obstacle_Single_Agent_Navigation_English.docx)

### Learning Objective

After completing this tutorial, students should understand how the basic navigation method from Tutorial 1 can be extended to environments containing multiple obstacles.

---

## Recommended Learning Sequence

Tutorial 1: Single Agent + Single Obstacle

↓

Understand Goal Attraction and Obstacle Repulsion

↓

Tutorial 2: Single Agent + Multiple Obstacles

↓

Understand Obstacle Detection and Nearest-Obstacle Selection

↓

Physical Spider Navigation

↓

Multi-Agent Navigation

↓

Ground Swarm Navigation
