"""
Capture, process and store decoded and raw telemtry packets from an Alpha T-Motor ESC.
Generates two files:
    1. One CSV file containing decoded state packets
    2. One BIN file containing raw telemtry data

Usage:
    python captureeESCTelemtry.py ./file.bin
"""

import datetime
import os
import sys
import time

import serial
import serial.tools.list_ports as port_list

from alphaTelemetry import AlphaTelemetry, ALPHA_ESC_BAUD

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

ae = AlphaTelemetry(POLES_N=21)

_init = True
_escTelem = {}

if not os.path.isdir(os.path.join(os.path.dirname(__file__), "data")):
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"))

with open(
    os.path.join(
        os.path.dirname(__file__),
        "data",
        "{}_AlphaTelemetry.bin".format(
            datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        ),
    ),
    "wb",
) as f_bin, open(
    os.path.join(
        os.path.dirname(__file__),
        "data",
        "{}_AlphaTelemetry.csv".format(
            datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        ),
    ),
    "w+",
) as f_csv:
    try:
        while True:
            r = serialPort.read(1)
            if r:
                ae.capture(int(r.hex(), 16))
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

                    if _init:
                        f_csv.write(",".join(_escTelem.keys()) + "\n")
                        _init = False
                    f_csv.write(
                        ",".join([str(_escTelem[k]) for k in _escTelem.keys()]) + "\n"
                    )
    except KeyboardInterrupt:
        serialPort.close()
        sys.exit(0)
