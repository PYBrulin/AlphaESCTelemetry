"""
Script to load a binary file and transmit it over a serial port to simulate a telemetry stream

Usage:
    python replay_telemetry.py ./file.bin
"""

import argparse
import logging
import os
import sys
import time

import serial
import serial.tools.list_ports as port_list
from tqdm import tqdm

from AlphaESCTelemetry.alphaTelemetry import ALPHA_ESC_BAUD

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to load a binary file and transmit it over serial port to simulate a telemetry stream",
    )
    parser.add_argument("file", metavar="file", type=str, nargs="+", help="file to transmit")
    parser.add_argument(
        "--rate",
        metavar="rate",
        type=float,
        nargs="?",
        default=-1,
        help="rate in seconds to transmit data",
    )
    args = parser.parse_args()

    logging.info("Transmitting file(s): {}".format(args.file))
    logging.info("Transmitting at rate: {}".format(args.rate))

    # Auto detect FTDI cable
    ports = list(port_list.comports())
    port = None
    for p in ports:
        logging.info(f"Device: {p.device}, {p.name}, {p.product}, {p.serial_number}, {p.manufacturer}")
        if p.manufacturer == "FTDI":
            port = p.device
    if port is None:
        logging.error("No FTDI adapter found")
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
            logging.error("File not found: {}".format(f))
            continue

        if not f.endswith(".bin"):
            logging.error("File is not a binary file: {}".format(f))
            continue

        with open(f, "rb") as f_bin:
            data = f_bin.read()
            for b in tqdm(data):
                serialPort.write(b.to_bytes(1, byteorder="little"))
                if args.rate > 0:
                    time.sleep(args.rate)
