# Script to load a binary file and transmit it over serial port to simulate a telemetry stream

import os
import sys
import time
import serial
import serial.tools.list_ports as port_list
from AlphaESCTelemtry.alphaTelemetry import ALPHA_ESC_BAUD
import argparse
from tqdm import tqdm

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transmit a binary file over serial port"
    )
    parser.add_argument(
        "file", metavar="file", type=str, nargs="+", help="file to transmit"
    )
    parser.add_argument(
        "--rate",
        metavar="rate",
        type=float,
        nargs="?",
        default=-1,
        help="rate in seconds to transmit data",
    )
    args = parser.parse_args()

    print("Transmitting file: {}".format(args.file))
    print("Transmitting at rate: {}".format(args.rate))

    # Auto detect FTDI cable
    ports = list(port_list.comports())
    port = None
    for p in ports:
        print(p.device, p.name, p.product, p.serial_number, p.manufacturer)
        if p.manufacturer == "FTDI":
            port = p.device
    if port is None:
        print("No FTDI adapter found")
        sys.exit(1)

    serialPort = serial.Serial(
        port=port,
        baudrate=ALPHA_ESC_BAUD,
        bytesize=8,
        timeout=1,
        stopbits=serial.STOPBITS_ONE,
    )

    for f in args.file:
        if not os.path.isfile(f):
            print("File not found: {}".format(f))
            continue

        if not f.endswith(".bin"):
            print("File is not a binary file: {}".format(f))
            continue

        with open(f, "rb") as f_bin:
            data = f_bin.read()
            for b in tqdm(data):
                serialPort.write(b.to_bytes(1, byteorder="little"))
                if args.rate > 0:
                    time.sleep(args.rate)
