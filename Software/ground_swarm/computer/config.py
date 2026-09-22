# Ground Swarm configuration
# Units:
# - ArUco positions and path goals are expressed in centimeters (cm).
# - Marker size is expressed in meters (m).
# - Angles are expressed in degrees.

import numpy as np

# ------------------------------------------------------------
# Robot IDs
# ------------------------------------------------------------
# This is the ID/message used by the computer to establish communication
# with the Spider in your current protocol.
SPIDER_COMM_ID = "12"

# This is the ArUco marker attached to the robot in your current vision code.
ROBOT_ARUCO_ID = 10

# ------------------------------------------------------------
# Serial communication
# ------------------------------------------------------------
SERIAL_PORT = "COM8"
BAUD_RATE = 115200
ESP32_STARTUP_DELAY_S = 3.0

# Commands observed in the original working program.
COMMAND_STOP = "0"
COMMAND_FORWARD = "1"
COMMAND_TURN_NEGATIVE = "5"
COMMAND_TURN_POSITIVE = "6"

# ------------------------------------------------------------
# Camera / ArUco
# ------------------------------------------------------------
CAMERA_INDEX = 0
CAMERA_BRIGHTNESS = 2.0

ARUCO_DICTIONARY = "DICT_4X4_250"
MARKER_SIZE_M = 0.065

# Approximate camera calibration copied from the original program.
# Replace with measured camera calibration parameters when available.
CAMERA_MATRIX = np.array([
    [1000.0, 0.0, 320.0],
    [0.0, 1000.0, 240.0],
    [0.0, 0.0, 1.0]
], dtype=np.float32)

DIST_COEFFS = np.zeros((5, 1), dtype=np.float32)

# ------------------------------------------------------------
# Navigation
# ------------------------------------------------------------
GOAL_X_PATH_CM = [50, 50, -50, -50]
GOAL_Y_PATH_CM = [-40, 40, 40, -40]

GOAL_TOLERANCE_CM = 2.0
HEADING_TOLERANCE_DEG = 10.0
