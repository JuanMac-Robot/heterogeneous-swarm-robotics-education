import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.close("all")

# ============================================================
# 1. SIMULATION PARAMETERS
# ============================================================

dt = 0.05
num_iterations = 4000

# Gains
Kg = 2.0                  # Goal attraction gain
Ko = 4.5                  # Obstacle repulsion gain

# Maximum velocity
MAX_SPEED = 5

# Goal tolerance
GOAL_TOLERANCE = 1.0


# ============================================================
# 2. ENVIRONMENT
# ============================================================

START = np.array([10.0, 10.0])
GOAL = np.array([90.0, 90.0])
OBSTACLE = np.array([52.0, 45.0])
OBSTACLE_RADIUS = 6.0


# ============================================================
# 3. SENSOR PARAMETERS
# ============================================================

SENSING_RADIUS = 22.0
NUM_SENSING_DIRECTIONS = 360


# ============================================================
# 4. SIGMOID PARAMETERS
# ============================================================

# Goal attraction sigmoid
GOAL_MID_DISTANCE = 12.0
GOAL_SLOPE = 0.25

# Obstacle repulsion sigmoid
REPULSION_MID_DISTANCE = 10.0
REPULSION_SLOPE = 0.50


# ============================================================
# 5. CREATE THE 360 SENSING DIRECTIONS
# ============================================================

angles = np.linspace(0, 2 * np.pi, NUM_SENSING_DIRECTIONS, endpoint=False)
sensing_directions = np.column_stack((np.cos(angles), np.sin(angles)))


# ============================================================
# 6. SIGMOID FUNCTIONS
# ============================================================

def sigmoid_goal_attraction(distance):
    """
    Attraction increases with distance.

    Far from goal -> approximately 1
    Near the goal -> approximately 0
    """
    exponent = -GOAL_SLOPE * (distance - GOAL_MID_DISTANCE)
    exponent = np.clip(exponent, -60, 60)
    return 1.0 / (1.0 + np.exp(exponent))


def sigmoid_obstacle_repulsion(distance):
    """
    True decreasing logistic sigmoid.

    distance = REPULSION_MID_DISTANCE gives exactly 0.5.

    Close to obstacle -> approximately 1
    Far from obstacle -> approximately 0
    """
    exponent = REPULSION_SLOPE * (distance - REPULSION_MID_DISTANCE)
    exponent = np.clip(exponent, -60, 60)
    return 1.0 / (1.0 + np.exp(exponent))


# ============================================================
# 7. GOAL ATTRACTION
# ============================================================

def calculate_goal_attraction(pos):

    # Vector from robot to goal
    vec = GOAL - pos
    distance = np.linalg.norm(vec)

    if distance < 0.0001:
        return np.zeros(2)

    # Direction toward goal
    direction = vec / distance

    # Sigmoid magnitude
    magnitude = sigmoid_goal_attraction(distance)

    return direction * magnitude


# ============================================================
# 8. OBSTACLE REPULSION
# ============================================================

def calculate_obstacle_repulsion(pos):
    """
    The robot senses the environment in 360 directions.

    If the obstacle is inside the sensing range, the direction
    that best points toward the obstacle is identified.

    A repulsive force is generated in the opposite direction.
    """

    # Vector robot -> obstacle
    vec_obstacle = OBSTACLE - pos
    distance_to_center = np.linalg.norm(vec_obstacle)

    if distance_to_center < 0.0001:
        return np.zeros(2), True, 0.0

    # Distance from robot to obstacle surface
    distance_to_surface = distance_to_center - OBSTACLE_RADIUS
    distance_to_surface = max(distance_to_surface, 0.0)

    # Is obstacle inside sensing range?
    if distance_to_surface > SENSING_RADIUS:
        return np.zeros(2), False, distance_to_surface

    # Direction from robot toward obstacle
    direction_to_obstacle = vec_obstacle / distance_to_center

    # Search the 360 sensing directions
    similarity = sensing_directions @ direction_to_obstacle
    index = np.argmax(similarity)
    detected_direction = sensing_directions[index]

    # Sigmoid obstacle repulsion
    magnitude = sigmoid_obstacle_repulsion(distance_to_surface)

    # Repulsion is opposite to detected obstacle direction
    repulsion = -detected_direction * magnitude

    return repulsion, True, distance_to_surface


# ============================================================
# 9. SIMULATION
# ============================================================

position = START.copy()

positions_history = [position.copy()]
detected_history = [False]
repulsion_history = [0.0]
goal_force_history = [0.0]

for t in range(num_iterations):

    # Goal attraction
    fg = Kg * calculate_goal_attraction(position)

    # Obstacle repulsion
    fo_raw, detected, obstacle_distance = calculate_obstacle_repulsion(position)
    fo = Ko * fo_raw

    # Total force
    force = fg + fo

    # Limit maximum velocity
    speed = np.linalg.norm(force)

    if speed > MAX_SPEED:
        force = force / speed * MAX_SPEED

    # Update position
    position = position + force * dt

    # Save history
    positions_history.append(position.copy())
    detected_history.append(detected)
    repulsion_history.append(np.linalg.norm(fo))
    goal_force_history.append(np.linalg.norm(fg))

    # Goal reached?
    distance_goal = np.linalg.norm(GOAL - position)

    if distance_goal < GOAL_TOLERANCE:
        print("\nGOAL REACHED")
        print("Iteration:", t)
        print("Position:", position)
        break

positions_history = np.array(positions_history)


# ============================================================
# 10. ANIMATION
# ============================================================

fig, ax = plt.subplots(figsize=(8, 8))

ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_aspect("equal", adjustable="box")
ax.grid(True)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Single Agent Navigation\nGoal Attraction + Sigmoid Obstacle Repulsion")


# ------------------------------------------------------------
# Draw Goal
# ------------------------------------------------------------

ax.scatter(GOAL[0], GOAL[1], marker="X", s=200, label="Goal")


# ------------------------------------------------------------
# Draw Start
# ------------------------------------------------------------

ax.scatter(START[0], START[1], marker="o", s=100, label="Start")


# ------------------------------------------------------------
# Draw Obstacle
# ------------------------------------------------------------

obstacle_circle = plt.Circle(OBSTACLE, OBSTACLE_RADIUS, alpha=0.7, label="Obstacle")
ax.add_patch(obstacle_circle)


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

detection_line, = ax.plot([], [], linestyle="--", linewidth=1)


# ============================================================
# STATUS TEXT
# ============================================================

status_text = ax.text(2, 97, "", fontsize=11, verticalalignment="top")

ax.legend(loc="lower right")

# Show every simulation step
ANIMATION_SKIP = 1


# ============================================================
# 11. ANIMATION UPDATE
# ============================================================

def update(frame):

    pos = positions_history[frame]

    # Agent position
    agent.set_data([pos[0]], [pos[1]])

    # Path
    path_line.set_data(positions_history[:frame + 1, 0], positions_history[:frame + 1, 1])

    # Move sensing circle
    sensing_circle.center = (pos[0], pos[1])

    # Obstacle detection visualization
    if detected_history[frame]:
        detection_line.set_data([pos[0], OBSTACLE[0]], [pos[1], OBSTACLE[1]])
        status = "Obstacle detected: YES\n" f"Repulsion force: " f"{repulsion_history[frame]:.2f}"
    else:
        detection_line.set_data([], [])
        status = "Obstacle detected: NO\n" f"Repulsion force: " f"{repulsion_history[frame]:.2f}"

    status_text.set_text(status)

    return agent, path_line, sensing_circle, detection_line, status_text


# ============================================================
# 12. CREATE ANIMATION
# ============================================================

ani = FuncAnimation(fig, update, frames=range(0, len(positions_history), ANIMATION_SKIP), interval=20, repeat=False)


# ============================================================
# 13. FINAL PATH
# ============================================================

fig2, ax2 = plt.subplots(figsize=(8, 8))

ax2.set_xlim(0, 100)
ax2.set_ylim(0, 100)
ax2.set_aspect("equal", adjustable="box")
ax2.grid(True)
ax2.set_xlabel("X")
ax2.set_ylabel("Y")
ax2.set_title("Final Agent Path")


# Path
ax2.plot(positions_history[:, 0], positions_history[:, 1], linewidth=2, label="Path")

# Start
ax2.scatter(START[0], START[1], s=100, label="Start")

# Goal
ax2.scatter(GOAL[0], GOAL[1], marker="X", s=200, label="Goal")

# Obstacle
obstacle_final = plt.Circle(OBSTACLE, OBSTACLE_RADIUS, alpha=0.7)
ax2.add_patch(obstacle_final)

# Show the obstacle sensing boundary for reference in the final plot
obstacle_detection_zone = plt.Circle(OBSTACLE, OBSTACLE_RADIUS + SENSING_RADIUS, fill=False, linestyle=":", linewidth=1)
ax2.add_patch(obstacle_detection_zone)

ax2.legend()

plt.show()