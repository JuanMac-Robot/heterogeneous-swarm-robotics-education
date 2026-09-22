"""
Hardware test: overhead camera + ArUco detection.

This program does NOT communicate with or move the Spider.
"""

import time
import cv2

from aruco_localization import ArucoLocalizer


def print_marker_table(markers):
    print("\nDetected markers:", len(markers))

    if not markers:
        print("No ArUco markers detected.")
        return

    print(
        f"{'ID':>4} | {'X (cm)':>9} | {'Y (cm)':>9} | "
        f"{'Z (cm)':>9} | {'Angle (deg)':>11}"
    )
    print("-" * 56)

    for marker in markers:
        print(
            f"{marker['id']:>4} | "
            f"{marker['x_cm']:>9.2f} | "
            f"{marker['y_cm']:>9.2f} | "
            f"{marker['z_cm']:>9.2f} | "
            f"{marker['orientation_deg']:>11.2f}"
        )


def main():
    print("ArUco detection hardware test")
    print("Press Q to exit.")

    last_print_time = 0.0

    with ArucoLocalizer() as localizer:
        while True:
            frame, markers = localizer.read()

            if frame is None:
                print("Warning: Could not read frame from camera.")
                continue

            # Print at a moderate rate so the console remains readable.
            now = time.time()
            if now - last_print_time >= 0.5:
                print_marker_table(markers)
                last_print_time = now

            cv2.imshow("Ground Swarm - ArUco Detection Test", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q")):
                break


if __name__ == "__main__":
    main()
