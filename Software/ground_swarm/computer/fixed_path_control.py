"""
Ground Swarm - single Spider fixed-path controller.

This program combines:
1. ArUco localization
2. Navigation logic
3. Serial communication

Path copied from the original working program:
    X = [50, 50, -50, -50] cm
    Y = [-40, 40, 40, -40] cm
"""

import cv2

from config import (
    ROBOT_ARUCO_ID,
    SPIDER_COMM_ID,
    GOAL_X_PATH_CM,
    GOAL_Y_PATH_CM,
    GOAL_TOLERANCE_CM,
    COMMAND_STOP,
)

from aruco_localization import ArucoLocalizer
from spider_communication import SpiderCommunication
from navigation_controller import calculate_command


def main():
    goal_index = 0

    print("Ground Swarm fixed-path control")
    print(f"Spider communication ID: {SPIDER_COMM_ID}")
    print(f"Robot ArUco marker ID: {ROBOT_ARUCO_ID}")
    print("Press Q to stop.")

    with SpiderCommunication() as spider, ArucoLocalizer() as localizer:
        spider.select_spider(SPIDER_COMM_ID)

        try:
            while True:
                frame, markers = localizer.read()

                if frame is None:
                    print("Warning: Could not read frame from camera.")
                    spider.stop()
                    continue

                robot = localizer.find_marker(markers, ROBOT_ARUCO_ID)

                goal_x_cm = GOAL_X_PATH_CM[goal_index]
                goal_y_cm = GOAL_Y_PATH_CM[goal_index]

                # Safety improvement over the original program:
                # if the robot is not visible, do not navigate using stale/default data.
                if robot is None:
                    spider.stop()
                    print(
                        f"Robot marker ID {ROBOT_ARUCO_ID} not detected -> STOP"
                    )
                else:
                    command, telemetry = calculate_command(
                        robot_x_cm=robot["x_cm"],
                        robot_y_cm=robot["y_cm"],
                        robot_angle_deg=robot["orientation_deg"],
                        goal_x_cm=goal_x_cm,
                        goal_y_cm=goal_y_cm,
                    )

                    spider.send(command)

                    distance_cm = telemetry["goal_distance_cm"]
                    angle_deg = telemetry["angle_goal_robot_deg"]

                    print(
                        f"Goal[{goal_index}] = ({goal_x_cm:.1f}, {goal_y_cm:.1f}) cm | "
                        f"Robot = ({robot['x_cm']:.1f}, {robot['y_cm']:.1f}) cm | "
                        f"Dist = {distance_cm:.2f} cm | "
                        f"Angle = {angle_deg:.2f} deg | "
                        f"Cmd = {command}"
                    )

                    if distance_cm <= GOAL_TOLERANCE_CM:
                        spider.send(COMMAND_STOP)
                        goal_index = (goal_index + 1) % len(GOAL_X_PATH_CM)
                        print(f"Goal reached. Next goal index: {goal_index}")

                cv2.imshow(
                    "Ground Swarm - Fixed Path Control",
                    frame
                )

                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), ord("Q")):
                    break

        finally:
            spider.stop()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
