import sys
import time

import serial

from ms40plus import Command, Framing, Response, Status, Window


def monitor():
    port = sys.argv[1]
    port = serial.Serial(port, baudrate=9600, timeout=0.33)
    framing = Framing()

    while True:
        for win in [Window.Power, Window.DrivingFrequency, Window.Status]:
            cmd = bytes([0x80 + 11, *list(f"{win.value:03d}".encode()), Command.Read.value])
            port.write(framing.send(cmd))
            time.sleep(0.1)
        power = None
        driving_frequency = None
        status = None

        while data := port.read(1):
            if payload := framing.receive(data):
                # print(payload)
                response_window = Window(int(payload[1:4]))
                _response = Response(payload[4])
                value_bytes = payload[5:]
                if len(value_bytes) == 1:
                    value = bool(value_bytes[0])
                elif len(value_bytes) == 6:
                    try:
                        value = int(value_bytes.decode())
                    except ValueError:
                        value = value_bytes
                elif len(value_bytes) == 10:
                    value = value_bytes.decode().strip()
                else:
                    print("invalid length", len(value_bytes))
                    exit()
                if response_window == Window.Power:
                    power = value
                elif response_window == Window.DrivingFrequency:
                    driving_frequency = value
                elif response_window == Window.Status:
                    status = Status(value)
                if power is not None and driving_frequency is not None and status is not None:
                    print(f"{power}W\t{driving_frequency}Hz\t{status.name}")
        
if __name__ == '__main__':
    monitor()


