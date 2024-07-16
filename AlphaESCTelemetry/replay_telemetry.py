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

from AlphaESCTelemetry.alphaTelemetry import ALPHA_ESC_B1, ALPHA_ESC_BAUD


def replay_log_file(file_path: str, port: str, rate: float = 1 / 20, debug: bool = False) -> None:
    """Replay the log file to the ESC

    Args:
        file_path (str): File path to the binary file
        port (str): Port to use to transmit the data
        rate (float, optional): Rate of transmission of each bale. Defaults to 1/20.
        debug (bool, optional): _description_. Defaults to False.
    """
    if not os.path.isfile(file_path):
        logging.error("File not found: {}".format(file_path))
        return

    if not file_path.endswith(".bin"):
        logging.error("File is not a binary file: {}".format(file_path))
        return

    serialPort = serial.Serial(
        port=port,
        baudrate=ALPHA_ESC_BAUD,
        bytesize=8,
        timeout=1,
        stopbits=serial.STOPBITS_ONE,
    )

    logging.info("Transmitting file: {}".format(file_path))
    if rate != 0:
        logging.info("Transmitting at {} Hz".format(1 / rate))
    else:
        logging.info("Transmitting without rate limitation")

    _time = time.perf_counter()

    track_time = 0
    counter = 0

    with open(file_path, "rb") as f_bin:
        data = f_bin.read()
        for b in tqdm(data, unit="B", unit_scale=True, smoothing=0):
            if b is ALPHA_ESC_B1:
                # If the byte is the start of a frame, wait for the rate limitation
                if rate != 0:
                    if time.perf_counter() - _time < rate:
                        time.sleep(rate - (time.perf_counter() - _time))
                    _time = time.perf_counter()

                counter += 1

            # print(b, end=' ')
            serialPort.write(b.to_bytes(1, byteorder="little"))

            if debug and time.perf_counter() - track_time > 1:
                # display how many messages we have sent
                logging.info(f"Messages sent: {counter}")
                counter = 0
                track_time = time.perf_counter()

    serialPort.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(
        description="Script to load a binary file and transmit it over serial port to simulate a telemetry stream",
    )
    parser.add_argument("file", metavar="file", type=str, nargs="+", help="file to transmit")
    parser.add_argument(
        "--rate",
        metavar="rate",
        type=float,
        nargs="?",
        default=1.0,
        help="Rate multiplier to transmit the file at. Default is 1.0 (20Hz). "
        + "Example if set to 2.0, the script will transmit at 40Hz, etc."
        + "If set to 0, the script will transmit as fast as possible",
    )
    parser.add_argument(
        "--port",
        metavar="port",
        type=str,
        nargs="?",
        default=None,
        help="Serial port to use. If not provided, the script will try to auto-detect the FTDI cable",
    )
    args = parser.parse_args()

    # Auto detect FTDI cable
    if args.port is None:
        ports = list(port_list.comports())
        port = None
        for p in ports:
            logging.info(f"Device: {p.device}, {p.name}, {p.product}, {p.serial_number}, {p.manufacturer}")
            if p.manufacturer == "FTDI":
                port = p.device
        if port is None:
            logging.error("No FTDI adapter found")
            sys.exit(1)
    else:
        port = args.port

    logging.info(f"Using port: {port}")

    rate = 0 if args.rate == 0 else 1 / (20 * args.rate)

    for log_file in args.file:
        replay_log_file(log_file, port, rate)
