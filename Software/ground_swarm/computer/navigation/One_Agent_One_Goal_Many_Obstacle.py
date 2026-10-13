# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 22:53:21 2026

@author: engineer
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.close("all")

# ============================================================
# 1. SIMULATION PARAMETERS
# ============================================================

dt = 0.1
num_iterations = 5000

# Goal attraction gain
Kg = 2.0

# Maximum velocity
MAX_SPEED = 5

# Distance used to determine that the goal was reached
GOAL_TOLERANCE = 5.0

# ============================================================
# 2. AGENT AND GOAL
# ============================================================

START = np.array([10.0, 10.0])
GOAL = np.array([90.0, 90.0])

# ============================================================
# 3. SENSOR PARAMETERS
# ============================================================

# Maximum sensing distance measured from the agent
SENSING_RADIUS = 15.0

# 360 sensing directions = 1 degree resolution
NUM_SENSING_DIRECTIONS = 360

# ============================================================
# 4. GOAL ATTRACTION SIGMOID
# ============================================================

GOAL_MID_DISTANCE = 12.0
GOAL_SLOPE = 0.25

# ============================================================
# 5. OBSTACLE LIST
# ============================================================
#
# Each obstacle has:
# name
# position
# physical radius
# sigmoid midpoint
# sigmoid slope
# repulsion gain
#
# ============================================================

OBSTACLES = [
    {
        "name": "Obstacle 1",
        "position": np.array([40.0, 34.0]),
        "radius": 6.0,
        "mid_distance": 10.0,
        "slope": 0.50,
        "gain": 3.5
    },
    {
        "name": "Obstacle 2",
        "position": np.array([65.0, 50.0]),
        "radius": 7.0,
        "mid_distance": 9.0,
        "slope": 0.60,
        "gain": 3.0
    },
    {
        "name": "Obstacle 3",
        "position": np.array([76.0, 70.0]),
        "radius": 5.0,
        "mid_distance": 8.0,
        "slope": 0.70,
        "gain": 2.8
    },
    {
        "name": "Obstacle 4",
        "position": np.array([40.0, 60.0]),
        "radius": 5.0,
        "mid_distance": 8.0,
        "slope": 0.70,
        "gain": 2
    },
    {
        "name": "Obstacle 5",
        "position": np.array([65.0, 80.0]),
        "radius": 2.0,
        "mid_distance": 8.0,
        "slope": 0.70,
        "gain": 1.8
    }
]

# ============================================================
# 6. CREATE 360 SENSING DIRECTIONS
# ============================================================

angles = np.linspace(0, 2 * np.pi, NUM_SENSING_DIRECTIONS, endpoint=False)
sensing_directions = np.column_stack((np.cos(angles), np.sin(angles)))

# ============================================================
# 7. GOAL SIGMOID
# ============================================================

def sigmoid_goal_attraction(distance):

    exponent = -GOAL_SLOPE * (distance - GOAL_MID_DISTANCE)
    exponent = np.clip(exponent, -60, 60)

    return 1.0 / (1.0 + np.exp(exponent))

# ============================================================
# 8. OBSTACLE REPULSION SIGMOID
# ============================================================

def sigmoid_obstacle_repulsion(distance, mid_distance, slope):
    """
    True decreasing logistic sigmoid.

    distance = mid_distance gives exactly:

        sigmoid = 0.5

    Close to obstacle:
        sigmoid -> 1

    Far from obstacle:
        sigmoid -> 0
    """

    exponent = slope * (distance - mid_distance)
    exponent = np.clip(exponent, -60, 60)

    return 1.0 / (1.0 + np.exp(exponent))

# ============================================================
# 9. GOAL ATTRACTION FORCE
# ============================================================

def calculate_goal_attraction(pos):

    vec_goal = GOAL - pos
    distance_goal = np.linalg.norm(vec_goal)

    if distance_goal < 0.0001:
        return np.zeros(2)

    direction_goal = vec_goal / distance_goal
    magnitude = sigmoid_goal_attraction(distance_goal)

    return direction_goal * magnitude

# ============================================================
# 10. FIND NEAREST DETECTED OBSTACLE
# ============================================================

def find_nearest_obstacle(pos):

    nearest_obstacle = None
    nearest_distance = np.inf

    for obstacle in OBSTACLES:

        vec = obstacle["position"] - pos
        distance_center = np.linalg.norm(vec)

        # Distance from agent to obstacle surface
        distance_surface = distance_center - obstacle["radius"]
        distance_surface = max(distance_surface, 0.0)

        # Check if obstacle is inside sensing region
        if distance_surface <= SENSING_RADIUS:

            if distance_surface < nearest_distance:
                nearest_distance = distance_surface
                nearest_obstacle = obstacle

    return nearest_obstacle, nearest_distance

# ============================================================
# 11. OBSTACLE REPULSION FORCE
# ============================================================

def calculate_obstacle_repulsion(pos):

    # --------------------------------------------------------
    # Find nearest obstacle inside sensing range
    # --------------------------------------------------------

    obstacle, distance_surface = find_nearest_obstacle(pos)

    # --------------------------------------------------------
    # No obstacle detected
    # --------------------------------------------------------

    if obstacle is None:
        return np.zeros(2), None, None, 0.0

    # --------------------------------------------------------
    # Vector from agent to obstacle
    # --------------------------------------------------------

    vec_obstacle = obstacle["position"] - pos
    distance_center = np.linalg.norm(vec_obstacle)

    if distance_center < 0.0001:
        return np.zeros(2), obstacle, 0.0, 0.0

    # --------------------------------------------------------
    # Direction toward obstacle
    # --------------------------------------------------------

    direction_to_obstacle = vec_obstacle / distance_center

    # --------------------------------------------------------
    # Search among the 360 sensing directions
    # --------------------------------------------------------

    similarity = sensing_directions @ direction_to_obstacle
    index = np.argmax(similarity)
    detected_direction = sensing_directions[index]

    # --------------------------------------------------------
    # Sigmoid magnitude
    # --------------------------------------------------------

    sigmoid_value = sigmoid_obstacle_repulsion(distance_surface, obstacle["mid_distance"], obstacle["slope"])

    # --------------------------------------------------------
    # Repulsive force
    # --------------------------------------------------------

    repulsion_force = -detected_direction * sigmoid_value * obstacle["gain"]

    return repulsion_force, obstacle, distance_surface, sigmoid_value

# ============================================================
# 12. SIMULATION
# ============================================================

position = START.copy()

positions_history = [position.copy()]
detected_obstacle_history = [None]
distance_obstacle_history = [None]
repulsion_history = [0.0]

for t in range(num_iterations):

    # --------------------------------------------------------
    # Goal attraction
    # --------------------------------------------------------

    fg = Kg * calculate_goal_attraction(position)

    # --------------------------------------------------------
    # Obstacle repulsion
    # --------------------------------------------------------

    fo, detected_obstacle, distance_obstacle, sigmoid_value = calculate_obstacle_repulsion(position)

    # --------------------------------------------------------
    # Total force
    # --------------------------------------------------------

    force = fg + fo

    # --------------------------------------------------------
    # Limit velocity
    # --------------------------------------------------------

    speed = np.linalg.norm(force)

    if speed > MAX_SPEED:
        force = force / speed * MAX_SPEED

    # --------------------------------------------------------
    # Update position
    # --------------------------------------------------------

    position = position + force * dt

    # --------------------------------------------------------
    # Save history
    # --------------------------------------------------------

    positions_history.append(position.copy())
    detected_obstacle_history.append(detected_obstacle)
    distance_obstacle_history.append(distance_obstacle)
    repulsion_history.append(np.linalg.norm(fo))

    # --------------------------------------------------------
    # Check goal
    # --------------------------------------------------------

    distance_goal = np.linalg.norm(GOAL - position)

    if distance_goal < GOAL_TOLERANCE:
        print()
        print("GOAL REACHED")
        print("Iteration:", t)
        print("Position:", position)
        break

positions_history = np.array(positions_history)

# ============================================================
# 13. ANIMATION
# ============================================================

fig, ax = plt.subplots(figsize=(9, 9))

ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal", adjustable="box")
ax.grid(True)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Single Agent Navigation\nGoal Attraction + Nearest Obstacle Repulsion")

# ============================================================
# GOAL
# ============================================================

ax.scatter(GOAL[0], GOAL[1], marker="X", s=200, label="Goal")

# ============================================================
# START
# ============================================================

ax.scatter(START[0], START[1], marker="o", s=100, label="Start")

# ============================================================
# DRAW ALL OBSTACLES
# ============================================================

for obstacle in OBSTACLES:

    obstacle_circle = plt.Circle(obstacle["position"], obstacle["radius"], alpha=0.7)
    ax.add_patch(obstacle_circle)

    ax.text(
        obstacle["position"][0],
        obstacle["position"][1],
        obstacle["name"],
        horizontalalignment="center",
        verticalalignment="center"
    )

# ============================================================
# AGENT
# ============================================================

agent, = ax.plot([], [], "o", markersize=10, label="Agent")

# ============================================================
# PATH
# ============================================================

path_line, = ax.plot([], [], linewidth=2, label="Path")

# ============================================================
# SENSING RANGE
# ============================================================

sensing_circle = plt.Circle(START, SENSING_RADIUS, fill=False, linestyle="--", linewidth=1.5)
ax.add_patch(sensing_circle)

# ============================================================
# DETECTION LINE
# ============================================================

detection_line, = ax.plot([], [], linestyle="--", linewidth=1.2)

# ============================================================
# STATUS TEXT
# ============================================================

status_text = ax.text(2, 98, "", fontsize=10, verticalalignment="top")

ax.legend(loc="lower right")

# ============================================================
# 14. ANIMATION UPDATE
# ============================================================

def update(frame):

    pos = positions_history[frame]

    # --------------------------------------------------------
    # Agent
    # --------------------------------------------------------

    agent.set_data([pos[0]], [pos[1]])

    # --------------------------------------------------------
    # Path
    # --------------------------------------------------------

    path_line.set_data(positions_history[:frame + 1, 0], positions_history[:frame + 1, 1])

    # --------------------------------------------------------
    # Move sensing range
    # --------------------------------------------------------

    sensing_circle.center = (pos[0], pos[1])

    # --------------------------------------------------------
    # Detected obstacle
    # --------------------------------------------------------

    obstacle = detected_obstacle_history[frame]

    if obstacle is not None:

        detection_line.set_data(
            [pos[0], obstacle["position"][0]],
            [pos[1], obstacle["position"][1]]
        )

        status_text.set_text(
            "Obstacle detected: YES\n"
            f"Nearest: {obstacle['name']}\n"
            f"Distance: {distance_obstacle_history[frame]:.2f}\n"
            f"Repulsion force: {repulsion_history[frame]:.2f}"
        )

    else:

        detection_line.set_data([], [])

        status_text.set_text(
            "Obstacle detected: NO\n"
            "Nearest: ---\n"
            "Repulsion force: 0.00"
        )

    return agent, path_line, sensing_circle, detection_line, status_text

# ============================================================
# 15. ANIMATION
# ============================================================

ani = FuncAnimation(fig, update, frames=range(len(positions_history)), interval=20, repeat=True, repeat_delay=500)

# ============================================================
# 16. FINAL PATH
# ============================================================

fig2, ax2 = plt.subplots(figsize=(9, 9))

ax2.set_xlim(0, 100)
ax2.set_ylim(0, 100)
ax2.set_aspect("equal", adjustable="box")
ax2.grid(True)
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.set_title("Final Navigation Path")

# ------------------------------------------------------------
# Complete path
# ------------------------------------------------------------

ax2.plot(positions_history[:, 0], positions_history[:, 1], linewidth=2, label="Agent Path")

# Start
ax2.scatter(START[0], START[1], s=100, label="Start")

# Goal
ax2.scatter(GOAL[0], GOAL[1], marker="X", s=200, label="Goal")

# Obstacles
for obstacle in OBSTACLES:

    obstacle_circle = plt.Circle(obstacle["position"], obstacle["radius"], alpha=0.7)
    ax2.add_patch(obstacle_circle)

    ax2.text(
        obstacle["position"][0],
        obstacle["position"][1],
        obstacle["name"],
        horizontalalignment="center",
        verticalalignment="center"
    )

ax2.legend()

plt.show()