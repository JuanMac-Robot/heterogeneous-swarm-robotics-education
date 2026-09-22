import numpy as np

from config import (
    GOAL_TOLERANCE_CM,
    HEADING_TOLERANCE_DEG,
    COMMAND_STOP,
    COMMAND_FORWARD,
    COMMAND_TURN_NEGATIVE,
    COMMAND_TURN_POSITIVE,
)


def compute_navigation_state(
    robot_x_cm,
    robot_y_cm,
    robot_angle_deg,
    goal_x_cm,
    goal_y_cm,
):
    """
    Reproduce the navigation geometry from the original working program.

    Returns:
        goal_distance_cm
        angle_goal_robot_deg
    """
    delta_x = goal_x_cm - robot_x_cm
    delta_y = goal_y_cm - robot_y_cm

    goal_distance_cm = (delta_x**2 + delta_y**2) ** 0.5

    theta = np.radians(robot_angle_deg)

    global_to_robot = np.array([
        [ np.cos(theta),  np.sin(theta)],
        [-np.sin(theta),  np.cos(theta)]
    ]) @ np.array([delta_x, delta_y])

    angle_goal_robot_deg = np.degrees(
        np.arctan2(
            global_to_robot[0],
            -global_to_robot[1]
        )
    )

    return float(goal_distance_cm), float(angle_goal_robot_deg)


def choose_command(
    goal_distance_cm,
    angle_goal_robot_deg,
    goal_tolerance_cm=GOAL_TOLERANCE_CM,
    heading_tolerance_deg=HEADING_TOLERANCE_DEG,
):
    """
    Convert navigation error into one of the existing Spider commands.

    Command meanings are preserved from the original program:
      0 = stop
      1 = forward
      5 = turn for negative angle error
      6 = turn for positive angle error
    """
    if goal_distance_cm <= goal_tolerance_cm:
        return COMMAND_STOP

    if abs(angle_goal_robot_deg) < heading_tolerance_deg:
        return COMMAND_FORWARD

    if angle_goal_robot_deg < -heading_tolerance_deg:
        return COMMAND_TURN_NEGATIVE

    return COMMAND_TURN_POSITIVE


def calculate_command(
    robot_x_cm,
    robot_y_cm,
    robot_angle_deg,
    goal_x_cm,
    goal_y_cm,
):
    """Convenience function: position + goal -> command + telemetry."""
    distance_cm, angle_deg = compute_navigation_state(
        robot_x_cm,
        robot_y_cm,
        robot_angle_deg,
        goal_x_cm,
        goal_y_cm,
    )

    command = choose_command(distance_cm, angle_deg)

    return command, {
        "goal_distance_cm": distance_cm,
        "angle_goal_robot_deg": angle_deg,
    }
