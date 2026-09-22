Ground Swarm Computer Software
This folder contains the computer-side software for the first stage of the Ground Swarm project.
The current implementation controls one physical Spider/mobile robot using:
an overhead camera,
ArUco marker localization,
Python/OpenCV,
serial communication to an ESP32 communication interface,
and a simple closed-loop navigation controller.
Current software architecture
```text
Overhead Camera
      |
      v
aruco_localization.py
      |
      | robot position (x, y, orientation)
      v
navigation_controller.py
      |
      | motion command
      v
spider_communication.py
      |
      v
Spider Robot
```
Files
`config.py`
Contains project parameters such as:
serial port,
communication robot ID,
ArUco robot ID,
camera parameters,
marker size,
path goals,
navigation tolerances,
and command codes.
`aruco_localization.py`
Responsible only for the vision/localization subsystem.
It:
opens the camera,
detects ArUco markers,
estimates marker position,
estimates marker orientation,
returns a list of detected markers.
Positions used by the controller are expressed in centimeters.
`spider_communication.py`
Responsible only for serial communication with the Spider communication interface.
It:
opens COM8 by default,
reproduces the existing Spider-ID handshake,
sends line-based commands,
sends STOP before closing.
`navigation_controller.py`
Contains only navigation mathematics and control decisions.
Inputs:
robot X,
robot Y,
robot orientation,
goal X,
goal Y.
Outputs:
navigation distance,
relative goal angle,
Spider command.
`test_aruco_detection.py`
Hardware/subsystem test for the camera and ArUco system.
It does not communicate with the robot.
Run:
```bash
python test_aruco_detection.py
```
Expected output:
camera window with detected ArUco markers,
marker IDs,
X/Y/Z positions,
orientation.
`test_spider_communication.py`
Hardware/subsystem test for computer-to-Spider communication.
It does not use the camera.
Run:
```bash
python test_spider_communication.py
```
Safety: Run with the robot in a clear area and be ready to stop it.
`fixed_path_control.py`
Complete single-robot closed-loop experiment.
It combines:
```text
Camera
  -> ArUco localization
  -> navigation controller
  -> Spider communication
  -> robot motion
  -> camera feedback
```
The current path is:
```python
GOAL_X_PATH_CM = [50, 50, -50, -50]
GOAL_Y_PATH_CM = [-40, 40, 40, -40]
```
The robot cycles through these four goals.
Run:
```bash
python fixed_path_control.py
```
Press Q to exit.
Python dependencies
Install:
```bash
pip install opencv-contrib-python numpy pyserial
```
Important IDs in the current implementation
The original working program uses two different identifiers:
```text
Spider communication ID = 12
Robot ArUco marker ID    = 10
```
These are preserved intentionally.
If they are supposed to refer to the same physical identifier, update them in `config.py`.
