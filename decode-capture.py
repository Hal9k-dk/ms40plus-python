"""
Decoder for serial protocol. Input is a Wireshark .CSV file with the "leftover
data" and "Direction" columns included.
"""

import sys
import colorama
import pandas as pd
from ms40plus import Command, Framing, Response, Window

in_framing = Framing()
out_framing = Framing()

framing = {
    'IN': in_framing,
    'OUT': out_framing
}

df = pd.read_csv(sys.argv[1])
for index, series in df.iterrows():
    data = bytes.fromhex(series["Leftover Capture Data"])
    direction = series["Direction"]
    if payload := framing[direction].receive(data):
        address = payload[0]
        payload = payload[1:]
        print(data, payload)
        if direction == 'OUT':
            try:
                win = Window(int(payload[0:3]))
            except ValueError:
                win = int(payload[0:3])
            command = Command(payload[3])
            print(f"{colorama.Fore.YELLOW}addr={address} win={win} {command}")
        elif direction == 'IN':
            if len(payload) == 1:
                response = Response(payload[0])
                print(f"\t{colorama.Fore.GREEN}{response}{colorama.Style.RESET_ALL}")
            else:
                win = Window(int(payload[0:3]))
                response = Response(payload[3])
                value_bytes = payload[4:]
                if len(value_bytes) == 1:
                    value = bool(value_bytes[0])
                elif len(value_bytes) == 6:
                    value = int(value_bytes)
                elif len(value_bytes) == 10:
                    value = value_bytes.decode().strip()
                else:
                    raise ValueError("Invalid value length")
                print(f"\t{colorama.Fore.GREEN}addr={address} win={win} response={response} value={value}{colorama.Style.RESET_ALL}")
    # print(series)
