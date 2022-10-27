import glob
import pandas
import numpy
import sys
import os
import matplotlib.pyplot as plt

file = sys.argv[1]
if not os.path.exists(file):
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

# REmove corrputed data
invalid_statusCode = df[df["statusCode"] != 0]
print(invalid_statusCode)
df.drop(invalid_statusCode.index, inplace=True)

invalid_initialValue = df[df["initialValue"] != 18258690]
print(invalid_initialValue)
df.drop(invalid_initialValue.index, inplace=True)

invalid_outputThrottle = df[df["outputThrottle"] > 100]
print(invalid_outputThrottle)
df.drop(invalid_outputThrottle.index, inplace=True)

invalid_busbarCurrent = df[df["busbarCurrent"] > 65000]
print(invalid_busbarCurrent)
df.drop(invalid_busbarCurrent.index, inplace=True)

invalid_phaseWireCurrent = df[df["phaseWireCurrent"] == 65535]
print(invalid_phaseWireCurrent)
df.drop(invalid_phaseWireCurrent.index, inplace=True)

# convert column to datetime object
df["time"] = pandas.to_datetime(df["time"], unit="s")
df.set_index("time", inplace=True)  # set column 'date' to index

list_inputs = df.columns.values.tolist()
list_inputs.remove("initialValue")
list_inputs.remove("baleNumber")
list_inputs.remove("statusCode")
list_inputs.remove("verifyCode")


fig, ax = plt.subplots(2, 2, sharex=True, sharey=False)
fig.suptitle("ESC Telemetry : "+os.path.basename(file), fontsize=16)

i = 1
# rxThrottle VS outputThrottle VS RPM
plt.subplot(2, 2, i)
df["rxThrottle"].plot(label="rxThrottle", legend=True)
df["outputThrottle"].plot(label="outputThrottle", legend=True)
df["rpm"].plot(secondary_y=True, label="RPM", legend=True)
plt.xlabel("time")
plt.title("rxThrottle VS outputThrottle")
plt.grid(True)

# voltage
i += 1
plt.subplot(2, 2, i)
df["voltage"].plot(label="voltage", legend=True)
plt.xlabel("time")
plt.title("voltage")
plt.grid(True)

# busbarCurrent VS phaseWireCurrent
i += 1
plt.subplot(2, 2, i)
df["busbarCurrent"].plot(label="busbarCurrent", legend=True)
df["phaseWireCurrent"].plot(label="phaseWireCurrent", legend=True)
plt.xlabel("time")
plt.title("busbarCurrent VS phaseWireCurrent")
plt.grid(True)

# mosfetTemp VS capacitorTemp
i += 1
plt.subplot(2, 2, i)
df["mosfetTemp"].plot(label="mosfetTemp", legend=True)
df["capacitorTemp"].plot(secondary_y=True, label="capacitorTemp", legend=True)
plt.xlabel("time")
plt.title("mosfetTemp VS capacitorTemp")
plt.grid(True)


plt.tight_layout()
plt.show()
