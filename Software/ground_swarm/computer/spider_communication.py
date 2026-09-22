import time
import serial

from config import (
    SERIAL_PORT,
    BAUD_RATE,
    ESP32_STARTUP_DELAY_S,
    SPIDER_COMM_ID,
    COMMAND_STOP,
)


class SpiderCommunication:
    """Serial communication interface used by the ground-swarm computer."""

    def __init__(
        self,
        port=SERIAL_PORT,
        baud_rate=BAUD_RATE,
        startup_delay_s=ESP32_STARTUP_DELAY_S,
    ):
        self.port = port
        self.baud_rate = baud_rate
        self.startup_delay_s = startup_delay_s
        self.esp = None

    def connect(self):
        """Open the serial port and clear ESP32 boot messages."""
        self.esp = serial.Serial(self.port, self.baud_rate)
        time.sleep(self.startup_delay_s)
        self.esp.reset_input_buffer()
        return self

    def send(self, command):
        """Send one line-based command to the ESP32."""
        if self.esp is None or not self.esp.is_open:
            raise RuntimeError("Serial connection is not open.")

        self.esp.write((str(command) + "\n").encode())

    def select_spider(self, spider_id=SPIDER_COMM_ID):
        """
        Reproduce the robot-selection/handshake sequence from the original
        working program: send the Spider ID twice with the same delays.
        """
        self.send(spider_id)
        time.sleep(2.0)
        self.send(spider_id)
        time.sleep(1.0)

    def stop(self):
        """Send the STOP command."""
        if self.esp is not None and self.esp.is_open:
            self.send(COMMAND_STOP)

    def close(self):
        """Stop the robot and close the serial port."""
        if self.esp is not None and self.esp.is_open:
            try:
                self.stop()
            finally:
                self.esp.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
