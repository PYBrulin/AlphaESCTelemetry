import time
import serial
import serial.tools.list_ports as port_list
import sys
import os
import datetime


import datetime
import sys
import time

import serial
import serial.tools.list_ports as port_list

from escTransport import *

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

with open(
    "{}_AlphaTelemetry.bin".format(
        datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    ),
    "wb",
) as f_bin, open(
    "{}_AlphaTelemetry.csv".format(
        datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    ),
    "w+",
) as f_csv:
    try:
        while True:

            r = serialPort.read()
            ae.capture(r)
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
                _escTelem["fault"] = ae.fault
                print("baleNumber       : {}".format(ae.baleNumber))
                print("rxThrottle       : {}".format(ae.rxThrottle))
                print("outputThrottle   : {}".format(ae.outputThrottle))
                print("rpm              : {}".format(ae.rpm))
                print("voltage          : {}".format(ae.voltage))
                print("busbarCurrent    : {}".format(ae.busbarCurrent))
                print("phaseWireCurrent : {}".format(ae.phaseWireCurrent))
                print("mosfetTemp       : {}".format(ae.mosfetTemp))
                print("capacitorTemp    : {}".format(ae.capacitorTemp))
                print("statusCode       : {}".format(ae.statusCode))
                print("fault            : {}".format(ae.fault))

                if _init:
                    f_csv.write(",".join(_escTelem.keys()) + "\n")
                    init = False
                f_csv.write(
                    ",".join([str(_escTelem[k]) for k in _escTelem.keys()]) + "\n"
                )
    except KeyboardInterrupt:
        serialPort.close()
        sys.exit(0)
