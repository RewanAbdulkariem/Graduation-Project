import serial
from PyQt5.QtCore import QThread, pyqtSignal

class SerialThread(QThread):
    data_received = pyqtSignal(int, int)  # Define a signal for passing data to GUI
    def __init__(self):
        super().__init__()
        self.port = 'COM7'
        self.baud_rate = 115200
        self.serial_port = None
        self.running = True

    def run(self):
        try:
            self.serial_port = serial.Serial(self.port, self.baud_rate)

            while self.running:
                if self.serial_port.in_waiting > 0:
                    try:
                        line = self.serial_port.readline().decode().strip()
                    except UnicodeDecodeError as e:
                        print(f"Error decoding serial data: {e}")
                        continue
                    # Assuming data format is "temperature_value humidity_value"
                    data = line.split()
                    if len(data) == 2:
                        try:
                            temperature = int(data[0])
                            humidity = int(data[1])
                            self.data_received.emit(temperature, humidity)
                        except ValueError as e:
                            print(f"Error converting data to integers: {e}")
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")

    def stop(self):
        self.running = False
        if self.serial_port:
            self.serial_port.close()
