import argparse
import logging
import os
import sys

import numpy
import pandas
from signal_plotter.plot_window import plot_window

from AlphaESCTelemetry.decodeESCTelemetry import decode_binary

parser = argparse.ArgumentParser(description="""Plot telemetry data from a CSV or BIN file.""")
parser.add_argument("file", metavar="file", type=str, nargs="+", help="file to plot")
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
df["voltage"] = df["voltage"].apply(lambda x: x)

# Filter data
df["voltage_filtered"] = df["voltage"].ewm(span=50, adjust=False).mean()
df["busbarCurrent_filtered"] = df["busbarCurrent"].ewm(span=50, adjust=False).mean()

# Save formatted CSV
df.to_csv(os.path.join(os.path.dirname(args.file), "out.csv"))

# Format data
items = {
    key: {
        "x": numpy.ravel(df.index),
        "y": numpy.ravel(df[key]),
    }
    for key in list_inputs
}

plot_window(items)
