"""
Capture, process and store decoded and raw telemetry packets from an Alpha T-Motor ESC.
Generates two files:
    1. One CSV file containing decoded state packets
    2. One BIN file containing raw telemetry data

Usage:
    python captureeESCTelemetry.py ./file.bin
"""

import argparse
import datetime
import logging
import os
import sys
import time

import serial
import serial.tools.list_ports as port_list
from alphaTelemetry import ALPHA_ESC_BAUD, AlphaTelemetry

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Capture, process and store decoded and raw telemetry packets from an Alpha T-Motor ESC.
        Generates one binary file containing raw telemetry data and one CSV file containing decoded state packets."""
    )
    parser.add_argument("file", metavar="file", type=str, nargs="+", help="file to transmit")
    parser.add_argument("--poles", metavar="poles", type=int, nargs="?", default=21, help="number of poles")
    args = parser.parse_args()

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

    # Pass argv integer to set number of poles
    # Default to 21 poles
    ae = AlphaTelemetry(POLES_N=args.poles)

    _init = True
    _escTelem = {}

    # Create data directory if it does not exist
    if not os.path.isdir(os.path.join(os.path.dirname(__file__), "data")):
        os.makedirs(os.path.join(os.path.dirname(__file__), "data"))

    bin_file = os.path.join(
        os.path.dirname(__file__),
        "data",
        "{}_AlphaTelemetry.bin".format(datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")),
    )
    csv_file = os.path.join(
        os.path.dirname(__file__),
        "data",
        "{}_AlphaTelemetry.csv".format(datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")),
    )

    with open(bin_file, "wb") as f_bin, open(csv_file, "w+") as f_csv:
        try:
            while True:
                r = serialPort.read(1)
                if r:
                    ae.capture(int(r.hex(), 16))
                    # Store raw telemetry data directly to binary file
                    f_bin.write(r)

                    if ae.ready:
                        _escTelem["time"] = time.time()
                        _escTelem["baleNumber"] = ae.baleNumber
                        _escTelem["rxThrottle"] = ae.rxThrottle
                        _escTelem["outputThrottle"] = ae.outputThrottle
                        _escTelem["rpm"] = ae.rpm
                        _escTelem["voltage"] = ae.voltage
                        _escTelem["busbarCurrent"] = ae.busbarCurrent
                        _escTelem["phaseWireCurrent"] = ae.phaseWireCurrent
                        _escTelem["mosfetTemp"] = ae.mosfetTemp
                        _escTelem["capacitorTemp"] = ae.capacitorTemp
                        _escTelem["statusCode"] = ae.statusCode
                        _escTelem["fault"] = int(ae.fault)

                        # Store decoded telemetry data to CSV file
                        if _init:
                            f_csv.write(",".join(_escTelem.keys()) + "\n")
                            _init = False
                        f_csv.write(",".join([str(_escTelem[k]) for k in _escTelem.keys()]) + "\n")
        except KeyboardInterrupt:
            serialPort.close()
            sys.exit(0)
