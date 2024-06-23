import serial
from PyQt5.QtCore import QThread, pyqtSignal

class SerialThread(QThread):
    data_received = pyqtSignal(float, float, float, float, float, float)  # Define a signal for passing data to GUI
    def __init__(self):
        super().__init__()
        self.port = 'COM6'
        self.baud_rate = 9600
        self.serial_port = None
        self.running = True
        try:
            self.serial_port = serial.Serial(self.port, self.baud_rate)
        except serial.SerialException as e:
            self.running = False
            print(f"Serial communication error: {e}")

    def run(self):
        while self.running:
            if self.serial_port.in_waiting > 0:
                try:
                    line = self.serial_port.readline()
                    print(line)
                    line = line.decode().strip()
                except UnicodeDecodeError as e:
                    print(f"Error decoding serial data: {e}")
                    continue
                # Parse the sensor data
                data = self.parse_sensor_data(line)
                if data:
                    temperature, humidity, LPG, CH4, CO, Smoke = data
                    self.data_received.emit(temperature, humidity, LPG, CH4, CO, Smoke)

    def parse_sensor_data(self, data):
        try:
            # Split the main parts
            main_parts = data.split('|')
            temp_hum_part = main_parts[0]
            gas_readings_part = main_parts[1]

            # Parse temperature and humidity
            temp_str = temp_hum_part.split(',')[0].split(':')[1].strip().replace('°C', '')
            hum_str = temp_hum_part.split(',')[1].split(':')[1].strip().replace('%', '')

            # Parse gas readings
            gas_readings = gas_readings_part.split(',')
            LPG_str = gas_readings[0].split('=')[1].strip().replace(' ppm', '')
            CH4_str = gas_readings[1].split('=')[1].strip().replace(' ppm', '')
            CO_str = gas_readings[2].split('=')[1].strip().replace(' ppm', '')
            # Skipping Alcohol as it is not being used
            Smoke_str = gas_readings[4].split('=')[1].strip().replace(' ppm', '')

            temperature = float(temp_str)
            humidity = float(hum_str)
            LPG = float(LPG_str)
            CH4 = float(CH4_str)
            CO = float(CO_str)
            Smoke = float(Smoke_str)

            return temperature, humidity, LPG, CH4, CO, Smoke

        except (IndexError, ValueError) as e:
            print(f"Error parsing sensor data: {e}")
            return None

    def stop(self):
        self.running = False
        if self.serial_port:
            self.serial_port.close()
