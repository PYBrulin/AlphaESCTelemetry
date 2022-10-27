import time
import serial
import serial.tools.list_ports as port_list
import sys
import os
import datetime
import pandas

if not os.path.exists(sys.argv[1]):
    sys.exit(1)

escTelemetry = {}


def tempExtrapo(tempVal):
    return 0.0004 * tempVal**2 - 0.6604 * tempVal + 143.48
    # return 0.0001* tempVal**3 - 0.0242*tempVal**2- 0.7327*tempVal + 241.34


output = pandas.DataFrame()

with open(sys.argv[1], "rb") as f:
    while byte := f.read(1):

        if byte == b"\x9b":
            serialArray = b"\x9b" + f.read(23)

            if len(serialArray) == 24:
                # sys.stdout.flush()

                escTelemetry["initialValue"] = (
                    (serialArray[0] << 8)
                    + (serialArray[1] << 16)
                    + (serialArray[2] << 24)
                    + serialArray[3]
                )
                escTelemetry["baleNumber"] = (serialArray[4] << 8) + serialArray[5]
                escTelemetry["rxThrottle"] = (
                    ((serialArray[6] << 8) + serialArray[7]) / 1024
                ) * 100  # * 100 / 1024
                escTelemetry["outputThrottle"] = (
                    ((serialArray[8] << 8) + serialArray[9]) / 1024
                ) * 100
                escTelemetry["rpm"] = (serialArray[10] << 8) + serialArray[11]  # / 22
                escTelemetry["voltage"] = (
                    (serialArray[12] << 8) + serialArray[13]
                ) * 10
                # escTelemetry["busbarCurrent"] = int_val = int.from_bytes(
                #     serialArray[14:16], "little", signed=True
                # )
                escTelemetry["busbarCurrent"] = (serialArray[14] << 8) + serialArray[15]
                # escTelemetry["phaseWireCurrent"] = int.from_bytes(
                #     serialArray[16:18], "little", signed=True
                # )
                escTelemetry["phaseWireCurrent"] = (serialArray[16] << 8) + serialArray[
                    17
                ]
                escTelemetry["mosfetTemp"] = tempExtrapo(serialArray[18])
                escTelemetry["capacitorTemp"] = tempExtrapo(serialArray[19])
                escTelemetry["statusCode"] = (serialArray[20] << 8) + serialArray[21]
                escTelemetry["verifyCode"] = (serialArray[22] << 8) + serialArray[23]

                # print(escTelemetry)
                # Iterate over key/value pairs in dict and print them
                print(serialArray)
                for key, value in escTelemetry.items():
                    print(key, " : ", value)

                print("=" * 30)

                df = pandas.DataFrame([escTelemetry])
                output = pandas.concat([output, df], ignore_index=True)

print(output)
output.to_csv(os.path.splitext(os.path.basename(sys.argv[1]))[0] + ".csv", index=False)
