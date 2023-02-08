"""
Decode an existing binary files containing raw telemtry packets capture from an Alpha T-Motor ESC

Usage:
    python decodeESCTelemtry.py ./file.bin
"""

import argparse
import os
import sys

from alphaTelemetry import *

ap = argparse.ArgumentParser()
ap.add_argument(
    "-f",
    "--file",
    type=str,
    dest="bin_file",
    required=True,
    default="",
    help="Load specific weights into the model. Doing so will overwrite the training phase.",
)
ap.add_argument(
    "-v",
    "--verbose",
    type=bool,
    dest="verbose",
    required=False,
    default=False,
    help="Display processed data in terminal.",
)
args = ap.parse_args()


if not os.path.exists(args.bin_file):
    print("Error: file `{}` does not exist")
    sys.exit(1)

ae = AlphaTelemetry(POLES_N=21)

_init = True
_escTelem = {}
with open(args.bin_file, "rb") as f_bin, open(
    args.bin_file.replace(".bin", ".csv"), "w+"
) as f_csv:
    try:
        while byte := f_bin.read(1):
            ae.capture(int(byte.hex(), 16))

            if ae.ready:
                if args.verbose:
                    print("baleNumber       : {}".format(ae.baleNumber))
                    print("rxThrottle       : {} %".format(ae.rxThrottle))
                    print("outputThrottle   : {} %".format(ae.outputThrottle))
                    print("rpm              : {} RPM".format(ae.rpm))
                    print("voltage          : {} V".format(ae.voltage))
                    print("busbarCurrent    : {} A".format(ae.busbarCurrent))
                    print("phaseWireCurrent : {} A".format(ae.phaseWireCurrent))
                    print("mosfetTemp       : {} °C".format(ae.mosfetTemp))
                    print("capacitorTemp    : {} °C".format(ae.capacitorTemp))
                    print("statusCode       : {}".format(ae.statusCode))
                    print("fault            : {}".format(ae.fault))
                    print("_____________________________")

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
