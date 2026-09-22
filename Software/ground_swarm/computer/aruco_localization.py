import cv2
from cv2 import aruco as ArUco
import numpy as np
import math

from config import (
    CAMERA_INDEX,
    CAMERA_BRIGHTNESS,
    CAMERA_MATRIX,
    DIST_COEFFS,
    MARKER_SIZE_M,
)


def normalize_angle(angle_deg):
    """Normalize an angle to [-180, 180] degrees."""
    while angle_deg > 180:
        angle_deg -= 360
    while angle_deg < -180:
        angle_deg += 360
    return angle_deg


def get_xy_orientation_degrees(rvec):
    """
    Project the marker local X-axis onto the camera X-Y plane
    and return its orientation in degrees.
    """
    rotation_matrix, _ = cv2.Rodrigues(rvec)
    marker_x_axis_camera = rotation_matrix[:, 0]

    angle_rad = math.atan2(
        marker_x_axis_camera[1],
        marker_x_axis_camera[0]
    )
    return normalize_angle(math.degrees(angle_rad))


class ArucoLocalizer:
    """Camera and ArUco localization subsystem."""

    def __init__(
        self,
        camera_index=CAMERA_INDEX,
        camera_matrix=CAMERA_MATRIX,
        dist_coeffs=DIST_COEFFS,
        marker_size_m=MARKER_SIZE_M,
    ):
        self.camera_index = camera_index
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.marker_size_m = marker_size_m

        half_size = marker_size_m / 2.0

        # Corner order required by SOLVEPNP_IPPE_SQUARE:
        # top-left, top-right, bottom-right, bottom-left
        self.obj_points = np.array([
            [-half_size,  half_size, 0.0],
            [ half_size,  half_size, 0.0],
            [ half_size, -half_size, 0.0],
            [-half_size, -half_size, 0.0]
        ], dtype=np.float32)

        aruco_dict = ArUco.getPredefinedDictionary(ArUco.DICT_4X4_250)
        aruco_params = ArUco.DetectorParameters()
        self.detector = ArUco.ArucoDetector(aruco_dict, aruco_params)

        self.camera = None

    def open(self):
        """Open the camera."""
        self.camera = cv2.VideoCapture(self.camera_index)

        if not self.camera.isOpened():
            raise RuntimeError("Could not access the camera.")

        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, CAMERA_BRIGHTNESS)
        return self

    def read(self):
        """
        Read one camera frame and detect all ArUco markers.

        Returns:
            frame: annotated BGR image
            markers: list of dictionaries with:
                id, x_cm, y_cm, z_cm, distance_m, orientation_deg
        """
        if self.camera is None or not self.camera.isOpened():
            raise RuntimeError("Camera is not open.")

        ret, frame = self.camera.read()
        if not ret:
            return None, []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detector.detectMarkers(gray)

        markers = []

        if ids is not None and len(corners) > 0:
            ArUco.drawDetectedMarkers(frame, corners, ids)

            for i in range(len(corners)):
                marker_id = int(ids[i][0])
                marker_corners = corners[i].reshape((4, 2)).astype(np.float32)

                success, rvec, tvec = cv2.solvePnP(
                    self.obj_points,
                    marker_corners,
                    self.camera_matrix,
                    self.dist_coeffs,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE
                )

                if not success:
                    continue

                coords_m = tvec.flatten()

                x_cm = coords_m[0] * 100.0
                y_cm = coords_m[1] * 100.0
                z_cm = coords_m[2] * 100.0
                distance_m = float(np.linalg.norm(coords_m))
                orientation_deg = get_xy_orientation_degrees(rvec)

                markers.append({
                    "id": marker_id,
                    "x_cm": float(x_cm),
                    "y_cm": float(y_cm),
                    "z_cm": float(z_cm),
                    "distance_m": distance_m,
                    "orientation_deg": float(orientation_deg),
                })

                # Draw marker center.
                center_pixel = marker_corners.mean(axis=0).astype(int)
                cx, cy = center_pixel
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

                # Draw camera/image center dynamically.
                height, width = frame.shape[:2]
                cv2.circle(
                    frame,
                    (width // 2, height // 2),
                    5,
                    (255, 255, 255),
                    -1
                )

                cv2.putText(
                    frame,
                    f"ID {marker_id}",
                    (cx + 8, cy - 8),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    2
                )

        return frame, markers

    @staticmethod
    def find_marker(markers, marker_id):
        """Return one marker dictionary by ID, or None if it is not detected."""
        for marker in markers:
            if marker["id"] == marker_id:
                return marker
        return None

    def close(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        cv2.destroyAllWindows()
