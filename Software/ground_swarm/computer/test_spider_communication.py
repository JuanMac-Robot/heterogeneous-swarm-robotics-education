"""
Hardware test: Computer <-> Spider communication.

This is not a pure software unit test because it requires the physical robot
and serial hardware.

IMPORTANT:
Run this test with the robot in a safe open area, or with the drive mechanism
raised if appropriate.
"""

import time

from config import SPIDER_COMM_ID
from spider_communication import SpiderCommunication


# Commands are intentionally limited to commands that appear in the
# original working control program.
COMMAND_SEQUENCE = [
    ("1", 1.0),   # forward command from the original code
    ("0", 0.5),   # stop
    ("5", 0.8),   # negative-angle turn command
    ("0", 0.5),   # stop
    ("6", 0.8),   # positive-angle turn command
    ("0", 0.5),   # stop
]


def main():
    print("Spider communication hardware test")
    print(f"Connecting to Spider communication ID {SPIDER_COMM_ID}...")

    with SpiderCommunication() as spider:
        spider.select_spider(SPIDER_COMM_ID)
        print("Connection sequence completed.")

        for command, duration_s in COMMAND_SEQUENCE:
            print(f"Sending command {command} for {duration_s:.1f} s")
            spider.send(command)
            time.sleep(duration_s)

        spider.stop()
        print("Test completed. STOP command sent.")


if __name__ == "__main__":
    main()
