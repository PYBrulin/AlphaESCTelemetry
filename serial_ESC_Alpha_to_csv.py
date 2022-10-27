import time
import serial
import serial.tools.list_ports as port_list
import sys
import os
import datetime

ports = list(port_list.comports())
port = None
for p in ports:
    print(p.device, p.name, p.product, p.serial_number, p.manufacturer)
    if p.manufacturer == "FTDI":
        port = p.device
if port is None: 
    print("No FTDI adapter found")
    sys.exit(1)
baudrate = 19200  # 115200
serialPort = serial.Serial(
    port=port, baudrate=baudrate, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE
)
serialArray = bytearray()
# serialPort.write(bytes.fromhex("A551F6"))
# serialPort.write("Hello\n".encode())  # "bytes.fromhex("A555FA"))

# packet = bytearray()
# packet.append(0xA5)
# packet.append(0x20)

# serialPort.write(packet)

escTelemetry = {}


def tempExtrapo(tempVal):
    return 0.0004 * tempVal**2 - 0.6604 * tempVal + 143.48
    # return 0.0001* tempVal**3 - 0.0242*tempVal**2- 0.7327*tempVal + 241.34

init=True
with open(
    "SerialAlpha-{}.csv".format(datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")),
    "w+",
) as f:
    while True:
        if serialPort.read() == b"\x9b":
            serialArray = b"\x9b" + serialPort.read(23)

            if len(serialArray) > 0:
                # sys.stdout.flush()

                escTelemetry["time"] = time.time()
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

                if init:
                    f.write(",".join(escTelemetry.keys())+"\n")
                    init = False
                f.write(",".join([str(escTelemetry[k]) for k in escTelemetry.keys()])+"\n")

                # print("=" * 30)

    serialPort.close()
