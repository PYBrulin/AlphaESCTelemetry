"""
Decode an existing binary files containing raw telemetry packets capture from an Alpha T-Motor ESC

Usage:
    python decodeESCTelemetry.py ./file.bin
"""

import argparse
import os
import sys

import pandas

from AlphaESCTelemetry.alphaTelemetry import AlphaTelemetry


def decode_binary(file_path: str, verbose: bool = False, poles=21) -> pandas.DataFrame:
    if not os.path.exists(file_path):
        sys.exit(1)

    escTelemetry = {}
    output = pandas.DataFrame()

    with open(file_path, "rb") as f:
        while byte := f.read(1):
            if byte == b"\x9b":
                serialArray = b"\x9b" + f.read(23)

                if len(serialArray) != 24:
                    continue

                # sys.stdout.flush()

                escTelemetry["initialValue"] = (
                    (serialArray[0] << 8) + (serialArray[1] << 16) + (serialArray[2] << 24) + serialArray[3]
                )
                escTelemetry["baleNumber"] = (serialArray[4] << 8) + serialArray[5]
                escTelemetry["rxThrottle"] = (int((serialArray[6] << 8) + serialArray[7])) * 100.0 / 1024.0
                escTelemetry["outputThrottle"] = int((serialArray[8] << 8) + serialArray[9]) * 100.0 / 1024.0
                escTelemetry["rpm"] = int((serialArray[10] << 8) + serialArray[11]) * 10.0 / poles
                escTelemetry["busbarVoltage"] = int((serialArray[12] << 8) + serialArray[13]) / 10.0
                # escTelemetry["busbarCurrent"] = int_val = int.from_bytes(serialArray[14:16], "little", signed=True)
                escTelemetry["busbarCurrent"] = (int(serialArray[14] << 8) + serialArray[15]) / 64.0
                # escTelemetry["phaseWireCurrent"] = int.from_bytes(serialArray[16:18], "little", signed=True)
                escTelemetry["phaseWireCurrent"] = int((serialArray[16] << 8) + serialArray[17]) / 64.0
                escTelemetry["mosfetTemp"] = AlphaTelemetry.temperature_decode(serialArray[18])
                escTelemetry["capacitorTemp"] = AlphaTelemetry.temperature_decode(serialArray[19])
                escTelemetry["statusCode"] = (serialArray[20] << 8) + serialArray[21]
                escTelemetry["fault"] = escTelemetry["statusCode"] != 0x00

                if escTelemetry["initialValue"] != 18258690:
                    continue

                # Iterate over key/value pairs in dict and print them
                if verbose:
                    print(serialArray)
                    for key, value in escTelemetry.items():
                        print(key, " : ", value)

                    print("=" * 30)

                df = pandas.DataFrame([escTelemetry])
                output = pandas.concat([output, df], ignore_index=True)

    return output


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Decode an existing binary files containing raw telemetry packets capture from an Alpha T-Motor ESC"
    )
    ap.add_argument(
        "bin_file",
        type=str,
        default="",
        help="Load specific weights into the model. Doing so will overwrite the training phase.",
    )
    ap.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        required=False,
        default=False,
        help="Print telemetry data to stdout.",
    )
    ap.add_argument(
        "-o",
        "--out",
        type=str,
        dest="out_file",
        required=False,
        default="",
        help="Save processed data to file (CSV).",
    )
    ap.add_argument(
        "-p",
        "--poles",
        type=int,
        dest="poles",
        required=False,
        default=21,
        help="Number of poles of the motor.",
    )
    args = ap.parse_args()

    if not os.path.exists(args.bin_file):
        print("Error: file `{}` does not exist")
        sys.exit(1)

    ae = AlphaTelemetry(POLES_N=args.poles)

    _init = True
    _escTelem = {}
    with open(args.bin_file, "rb") as f_bin, open(
        args.bin_file.replace(".bin", ".csv") if not args.out_file else args.out_file,
        "w+",
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
                        print("busbarVoltage    : {} V".format(ae.busbarVoltage))
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
                    _escTelem["busbarVoltage"] = ae.busbarVoltage
                    _escTelem["busbarCurrent"] = ae.busbarCurrent
                    _escTelem["phaseWireCurrent"] = ae.phaseWireCurrent
                    _escTelem["mosfetTemp"] = ae.mosfetTemp
                    _escTelem["capacitorTemp"] = ae.capacitorTemp
                    _escTelem["statusCode"] = ae.statusCode
                    _escTelem["fault"] = int(ae.fault)

                    if _init:
                        f_csv.write(",".join(_escTelem.keys()) + "\n")
                        _init = False
                    f_csv.write(",".join([str(_escTelem[k]) for k in _escTelem.keys()]) + "\n")
        except KeyboardInterrupt:
            sys.exit(0)
