"""
Simple CSV reader for Alpha ESC telemetry data.

Usage:
    python plot_csv_telemetry.py ./file.csv
"""

import logging
import os
import sys

import matplotlib.style as mplstyle
import pandas

mplstyle.use(["fast"])
import argparse

import matplotlib.pyplot as plt

from AlphaESCTelemetry.decodeESCTelemetry import decode_binary

parser = argparse.ArgumentParser(description="Plot telemetry data from a CSV or BIN file using matplotlib.")
parser.add_argument("file", metavar="file", type=str, help="file to plot")
parser.add_argument("--poles", metavar="poles", type=int, nargs="?", default=21, help="number of poles")
parser.add_argument(
    "--decorrupt",
    metavar="decorrupt",
    type=bool,
    nargs="?",
    default=False,
    help="decorrupt data by removing invalid values",
)
args = parser.parse_args()

if not os.path.exists(args.file):
    logging.error(f"Error: file `{args.file}` does not exist")
    sys.exit(1)

if args.file.endswith(".csv"):
    df = pandas.read_csv(
        args.file,
        sep=",",
        low_memory=False,
        header=0,
        dtype=float,
        encoding="latin-1",
        parse_dates=False,
    )
elif args.file.endswith(".bin"):
    logging.info("File is a binary file, decoding...")
    # Decode binary file
    df = decode_binary(args.file, poles=args.poles)
else:
    logging.error("File format not supported")
    sys.exit(1)


# Fill NaN with the value from last row
df.ffill(inplace=True)

if "time" in df.keys():
    # convert column to datetime object
    df["time"] = pandas.to_datetime(df["time"], unit="s")
    df["timeFormat"] = df["time"].dt.strftime("%Y-%m-%d %H%M%S")

    # Hypothesis: The messages are sent at the frequency of the motor rotation.
    # Result: Wrong, or the messages are not captured fast enough by the host PC
    df["time_diff"] = df["time"].diff(-1).dt.total_seconds().div(60)
    try:
        df["time_freq"] = df["time_diff"].apply(lambda x: 1 / abs(x))
    except ZeroDivisionError:
        pass

# Remove corrputed data
if args.decorrupt:
    invalid_statusCode = df[df["statusCode"] != 0]
    logging.info(invalid_statusCode)
    df.drop(invalid_statusCode.index, inplace=True)

    invalid_outputThrottle = df[df["outputThrottle"] > 100]
    logging.info(invalid_outputThrottle)
    df.drop(invalid_outputThrottle.index, inplace=True)

    invalid_busbarCurrent = df[df["busbarCurrent"] > 150]
    logging.info(invalid_busbarCurrent)
    df.drop(invalid_busbarCurrent.index, inplace=True)

    invalid_phaseWireCurrent = df[df["phaseWireCurrent"] > 150]
    logging.info(invalid_phaseWireCurrent)
    df.drop(invalid_phaseWireCurrent.index, inplace=True)

if "time" in df.keys():
    df.set_index("time", inplace=True)  # set column 'time' to index
else:
    df.set_index("baleNumber", inplace=True)  # set column 'time' to index

list_inputs = df.columns.values.tolist()

# Apply proportionnal gains
df["busbarCurrent"] = df["busbarCurrent"].apply(lambda x: x)
df["phaseWireCurrent"] = df["phaseWireCurrent"].apply(lambda x: x)

if "voltage" in df.keys():  # Old syntax
    df["busbarVoltage"] = df["voltage"].apply(lambda x: x)
else:
    df["busbarVoltage"] = df["busbarVoltage"].apply(lambda x: x)

# Filter data
df["voltage_filtered"] = df["voltage"].ewm(span=50, adjust=False).mean()
df["busbarCurrent_filtered"] = df["busbarCurrent"].ewm(span=50, adjust=False).mean()


# Save formatted CSV
df.to_csv(os.path.join(os.path.dirname(args.file), "out.csv"))


def highlight(indices, ax):
    i = 0
    while i < len(indices):
        ax.axvspan(
            indices[i] - 0.5,
            indices[i] + 0.5,
            facecolor="pink",
            edgecolor="none",
            alpha=0.2,
        )
        i += 1


# Display data
fig, ax = plt.subplots(2, 2, sharex=True, sharey=False)
fig.suptitle("ESC Telemetry : " + os.path.basename(args.file), fontsize=16)
plt.get_current_fig_manager().window.showMaximized()

i = 1
# rxThrottle VS outputThrottle VS RPM
plt.subplot(2, 2, i)
df["rxThrottle"].plot(label="rxThrottle [%]", legend=True)
df["outputThrottle"].plot(label="outputThrottle [%]", legend=True)
df["rpm"].plot(secondary_y=True, label="RPM", legend=True)
# df["statusCode"].plot(secondary_y=True, label="statusCode", legend=True)
# highlight(df[df["statusCode"] > 0].index, ax)
plt.xlabel("time")
plt.title("rxThrottle VS outputThrottle")
plt.grid(True)

# voltage
i += 1
plt.subplot(2, 2, i)
df["voltage"].plot(label="Voltage [V]", legend=True, ylim=(20, 26))
df["voltage_filtered"].plot(label="Filtered voltage [V]", legend=True, ylim=(20, 26))
df["busbarCurrent"].plot(secondary_y=True, label="busbarCurrent [A]", legend=True, ylim=(0, 60))
df["busbarCurrent_filtered"].plot(secondary_y=True, label="Filtered busbarCurrent [A]", legend=True, ylim=(0, 60))
# highlight(df[df["statusCode"] > 0].index, ax)
plt.xlabel("time")
plt.title("Battery input")
plt.grid(True)

# busbarCurrent VS phaseWireCurrent
i += 1
plt.subplot(2, 2, i)
df["busbarCurrent"].plot(label="busbarCurrent [A]", legend=True, ylim=(0, 60))
df["phaseWireCurrent"].plot(label="phaseWireCurrent [A]", legend=True, ylim=(0, 60))
((df["phaseWireCurrent"] / (3**0.5)) * (6 * 4.2 / df["voltage"])).plot(
    label="phaseWireCurrent /(3**.5) [A]", legend=True, ylim=(0, 60)
)

# highlight(df[df["statusCode"] > 0].index, ax)
plt.xlabel("time")
plt.title("busbarCurrent VS phaseWireCurrent")
plt.grid(True)

# mosfetTemp VS capacitorTemp
i += 1
plt.subplot(2, 2, i)
# df["time_freq"].plot(label="mosfetTemp [°C]", legend=True)
df["mosfetTemp"].plot(label="mosfetTemp [°C]", legend=True)
df["capacitorTemp"].plot(label="capacitorTemp [°C]", legend=True)
# highlight(df[df["statusCode"] > 0].index, ax)
plt.xlabel("time")
plt.title("mosfetTemp VS capacitorTemp")
plt.grid(True)


plt.tight_layout()
plt.show()
