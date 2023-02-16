import os
import pickle
import sys

import serial

from ms40plus import Framing, Response, Window

port = sys.argv[1]

port = serial.Serial(port, baudrate=9600, timeout=0.33)

framing = Framing()

session = []

window = bytes([0x80 + 11])


def read_command(win):
    return framing.send(window + f"{win:03d}0".encode())


def show_response(win, payload):
    length = len(payload)
    response_window = payload[0]
    if length == 2:
        response = Response(payload[1])
        print(win.name, response)
    else:
        response_window = Window(int(payload[1:4]))
        response = Response(payload[4])
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
        print(response_window.name + ':', repr(value))

def scan_windows():
    for win in Window:
        command = read_command(win.value)
        # print(command)
        port.write(command)
        buffer = bytearray()
        while data := port.read(1):
            buffer.extend(data)
            if payload := framing.receive(data):
                # print('buffer', buffer, 'payload', payload)
                session.append([command, bytes(buffer), payload])
                buffer.clear()

                show_response(win, payload)
            if not buffer:
                # print("complete")
                break
        if buffer:
            session.append([win, command, bytes(buffer), None])
            print('leftover', buffer)
            buffer.clear()

    with open("session.part", "wb") as outfile:
        pickle.dump(session, outfile)
    os.replace("session.part", "session")

if __name__ == '__main__':
    scan_windows()
