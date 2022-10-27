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


# plt.figure()
list_inputs = df.columns.values.tolist()
list_inputs.remove("initialValue")
list_inputs.remove("baleNumber")
list_inputs.remove("statusCode")
list_inputs.remove("verifyCode")

row = 1
for input in list_inputs:
    plt.subplot(
        len(list_inputs),
        1,
        row,
    )
    plt.plot(df[input])
    plt.xlabel("time")
    plt.ylabel(input)
    plt.legend()

    row += 1
plt.show()
