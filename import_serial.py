import serial
import argparse
import time

class SerialPort:
    def __init__(self, port_name, baud_rate, byte_size, stop_bits, parity):
        self.ser = serial.Serial(
            port=port_name,
            baudrate=baud_rate,
            bytesize=byte_size,
            stopbits=stop_bits,
            parity=parity,
            timeout=0.5  # Read timeout in seconds
        )

    def read_data(self):
        data = bytearray()
        while self.ser.isOpen():
            while self.ser.in_waiting > 0:
                byte = self.ser.read(1)
                if byte == b'\r':
                    print("INFO: Successfully read from serial port.")
                    return data.decode()
                else:
                    data.extend(byte)
            time.sleep(0.5)  # Wait for more data to be available

    def write_string(self, message):
        try:
            self.ser.write(message.encode())
            print("INFO: Successfully wrote to serial port.")
            return True
        except serial.SerialException:
            print("ERROR: Unable to write to serial port.")
            return False
def get_port_settings():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default='COM8')
    parser.add_argument('--baudRate', type=int, default=9600)
    parser.add_argument('--byteSize', type=int, default=8)
    parser.add_argument('--stopBits', type=int, default=1)
    parser.add_argument('--parity', default='N')
    return parser.parse_args()

def main():
    settings = get_port_settings()

    #port = SerialPort(settings.port, settings.baudRate, settings.byteSize, settings.stopBits, settings.parity)
    # while True:
    #     data = port.read_data()
    #     if data:
    #         print(f"Received: {data}")
    #     else:
    #         break

if __name__ == "__main__":
    main()


