import os
import sys

import matplotlib.pyplot as plt
import pandas

# # Forces matplotlib to use Type 1 fonts
# plt.rcParams["text.usetex"] = True
# plt.rcParams["pdf.fonttype"] = 42
# plt.rcParams["ps.fonttype"] = 42

file = sys.argv[1]
if not os.path.exists(file):
    print(f"File {file} does not exist")
    sys.exit(1)

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

list_inputs = df.columns.values.tolist()

# Apply proportionnal gains
df["busbarCurrent"] = df["busbarCurrent"].apply(lambda x: x)
df["phaseWireCurrent"] = df["phaseWireCurrent"].apply(lambda x: x)
df["voltage"] = df["voltage"].apply(lambda x: x)

# Filter data
df["voltage_filtered"] = df["voltage"].ewm(span=50, adjust=False).mean()
df["busbarCurrent_filtered"] = df["busbarCurrent"].ewm(span=50, adjust=False).mean()


# make a copy of df
df_copy = df.copy()

df_copy["rxThrottle"] = df["rxThrottle"] / 100
df_copy["rpm_scaled"] = (df["rpm"] * ((6 * 4.2) / df["voltage"])) / 3000
df_copy["rpm"] = df_copy["rpm_scaled"] - df_copy["rxThrottle"]

df_copy["busbarCurrent_scaled"] = (
    df["busbarCurrent"] * ((6 * 4.2) / df["voltage"])
) / 38.7
df_copy["busbarCurrent"] = df_copy["busbarCurrent_scaled"] - df_copy["rxThrottle"]

df_copy["phaseWireCurrent_scaled"] = (
    df["phaseWireCurrent"] * ((6 * 4.2) / df["voltage"])
) / 38.7
df_copy["phaseWireCurrent"] = df_copy["phaseWireCurrent_scaled"] - df_copy["rxThrottle"]


plt.plot(
    df_copy["rxThrottle"],
    df_copy["rpm"],
    "o",
    alpha=0.2,
    label="rpm",
)
plt.plot(
    df_copy["rxThrottle"],
    df_copy["busbarCurrent"],
    "o",
    alpha=0.2,
    label="busbarCurrent",
)
plt.plot(
    df_copy["rxThrottle"],
    df_copy["phaseWireCurrent"],
    "o",
    alpha=0.2,
    label="phaseWireCurrent",
)


plt.legend()
plt.title(f"Thrust fitting: {os.path.basename(file)}")
plt.xlabel("rxThrottle")
plt.ylabel("RPM")
plt.show()
