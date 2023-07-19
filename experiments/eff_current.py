import os

import matplotlib.pyplot as plt
import pandas

# # Forces matplotlib to use Type 1 fonts
# plt.rcParams["text.usetex"] = True
# plt.rcParams["pdf.fonttype"] = 42
# plt.rcParams["ps.fonttype"] = 42

file_U8II_thrust = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "data/2023-04-07T14-18-47_AlphaTelemetry.csv",
)
file_U8II_phase_fault = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "data/2023-04-07T14-27-40_AlphaTelemetry.csv",
)
# 2023-04-07T14-27-40


def read_file(file) -> pandas.DataFrame:
    df = pandas.read_csv(
        file,
        sep=",",
        low_memory=False,
        header=0,
        dtype=float,
        encoding="latin-1",
    )

    # Fill NaN with the value from last row
    print(df.isna().sum())
    df.fillna(method="pad", inplace=True)

    if "time" in df.keys():
        # convert column to datetime object
        df["time"] = pandas.to_datetime(df["time"], unit="s")
        df["timeFormat"] = df["time"].dt.strftime("%Y-%m-%d %H%M%S")

        # Hypothesis: The messages are sent at the frequency of the motor rotation.
        # Result: Wrong, or the messages are not captured fast enough by the host PC
        df["time_diff"] = df["time"].diff(-1).dt.total_seconds().div(60)
        df["time_freq"] = df["time_diff"].apply(lambda x: 1 / abs(x))

    if "time" in df.keys():
        df.set_index("time", inplace=True)  # set column 'time' to index
    else:
        df.set_index("baleNumber", inplace=True)  # set column 'time' to index

    # Apply proportionnal gains
    df["busbarCurrent"] = df["busbarCurrent"].apply(lambda x: x)
    df["phaseWireCurrent"] = df["phaseWireCurrent"].apply(lambda x: x)
    df["voltage"] = df["voltage"].apply(lambda x: x)

    # Filter data
    df["voltage_filtered"] = df["voltage"].ewm(span=50, adjust=False).mean()
    df["busbarCurrent_filtered"] = df["busbarCurrent"].ewm(span=50, adjust=False).mean()

    return df


df = read_file(file_U8II_thrust)

plt.figure()
plt.plot(df["phaseWireCurrent"], label="phaseWireCurrent")
plt.plot(df["phaseWireCurrent"] / (3**0.5), label="phaseWireCurrent / sqrt(3)")
plt.plot(df["busbarCurrent"], label="busbarCurrent")
plt.legend()
plt.grid()
plt.show()
