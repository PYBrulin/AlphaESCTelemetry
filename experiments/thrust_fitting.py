import os

import matplotlib.pyplot as plt
import numpy
import pandas
from scipy.optimize import curve_fit

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

file_sim = os.path.join(
    os.path.expanduser("~/OneDrive - ESTACA/These PYBrulin/SIMULATION/simple_AlphaESC"),
    "Alpha60AU8II-MF2815_000_export-2023-05-11T13-20-14.csv",
)


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
    df.ffill(inplace=True)

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


# %% Read Thrust data

df = read_file(file_U8II_thrust)

# %% RPM
x = df["rxThrottle"] / 100
y = df["rpm"]


def fit_func(x, a, b):
    # Curve fitting function
    return a * x**2 + b * x  # d=0 is implied


def rev_fit_func(x, a):
    return (1 - a) * x + a * x**2


# Curve fitting
params = curve_fit(fit_func, x, y)
[a, b] = params[0]
print([a, b])
x_fit = numpy.linspace(min(x), max(x), 100)
y_fit = a * x_fit**2 + b * x_fit

plt.figure()
plt.plot(x, y, "o", alpha=0.2, label="raw_data")
plt.plot(x_fit, y_fit, "-", label=f"curve_fit (y = {a:.1f}x^2 + {b:.1f}x)")

# Fit the data with a polynomial of degree 2
y_scale = df["rpm"] * ((6 * 4.2) / df["voltage"])

# Curve fitting
params = curve_fit(fit_func, x, y_scale)
[a_rpm, b_rpm] = params[0]
x_fit = numpy.linspace(min(x), max(x), 100)
y_fit = a_rpm * x_fit**2 + b_rpm * x_fit

plt.plot(x, y_scale, "o", alpha=0.2, label="scaled_data")
plt.plot(x_fit, y_fit, "-", label=f"scaled_curve_fit (y = {a_rpm:.1f}x^2 + {b_rpm:.1f}x)")

plt.plot(
    x,
    y_scale - (a_rpm * x**2 + b_rpm * x),
    "x",
    label="scaled_data - scaled_curve_fit",
)

plt.legend()

plt.title(f"RPM fitting: {os.path.basename(file_U8II_thrust)}")
plt.xlabel("rxThrottle")
plt.ylabel("RPM")
# plt.show()


# %% Currents

plt.figure()

# Fit the data with a polynomial of degree 2
x = df["rxThrottle"] / 100
y = df["phaseWireCurrent"]

# Curve fitting
params = curve_fit(fit_func, x, y)
[a, b] = params[0]
print([a, b])
x_fit = numpy.linspace(min(x), max(x), 100)
y_fit = a * x_fit**2 + b * x_fit

plt.plot(x, y, "o", alpha=0.2, label="raw_data")
plt.plot(x_fit, y_fit, "-", label=f"curve_fit (y = {a:.1f}x^2 + {b:.1f}x)")

# Scale
y_scale = df["phaseWireCurrent"] * ((6 * 4.2) / df["voltage"])

# Curve fitting
params = curve_fit(fit_func, x, y_scale)
[a_pwCurrent, b_pwCurrent] = params[0]
print([a_pwCurrent, b_pwCurrent])
x_fit = numpy.linspace(min(x), max(x), 100)
y_fit = a_pwCurrent * x_fit**2 + b_pwCurrent * x_fit

plt.plot(x, y_scale, "o", alpha=0.2, label="scaled_data")
plt.plot(
    x_fit,
    y_fit,
    "-",
    label=f"scaled_curve_fit (y = {a_pwCurrent:.1f}x^2 + {b_pwCurrent:.1f}x)",
)

plt.plot(
    x,
    y_scale - (a_pwCurrent * x**2 + b_pwCurrent * x),
    "x",
    label="scaled_data - scaled_curve_fit",
)

plt.legend()

plt.title(f"phaseWireCurrent fitting: {os.path.basename(file_U8II_thrust)}")
plt.xlabel("rxThrottle")
plt.ylabel("phaseWireCurrent")
plt.show()

# =============================================================================
# %% Read Phase fault data

del df
df = read_file(file_U8II_phase_fault)

# %% RPM
x = df["rxThrottle"] / 100
y = df["rpm"]

y_scale = df["rpm"] * ((6 * 4.2) / df["voltage"])

x_fit = numpy.linspace(min(x), max(x), 100)
y_fit = a_rpm * x_fit**2 + b_rpm * x_fit

plt.plot(x, y_scale, "o", alpha=0.2, label="scaled_data")
plt.plot(x_fit, y_fit, "-", label=f"scaled_curve_fit (y = {a_rpm:.1f}x^2 + {b_rpm:.1f}x)")
plt.plot(
    x,
    y_scale - (a_rpm * x**2 + b_rpm * x),
    "x",
    label="scaled_data - scaled_curve_fit",
)

plt.legend()

plt.title(f"RPM fitting: {os.path.basename(file_U8II_phase_fault)}")
plt.xlabel("rxThrottle")
plt.ylabel("RPM")
# plt.show()


# %% Currents

plt.figure()

# Fit the data with a polynomial of degree 2
x = df["rxThrottle"] / 100
y = df["phaseWireCurrent"]

y_scale = df["phaseWireCurrent"] * ((6 * 4.2) / df["voltage"])

x_fit = numpy.linspace(min(x), max(x), 100)
y_fit = a_pwCurrent * x_fit**2 + b_pwCurrent * x_fit

plt.plot(x, y_scale, "o", alpha=0.2, label="scaled_data")
plt.plot(
    x_fit,
    y_fit,
    "-",
    label=f"scaled_curve_fit (y = {a_pwCurrent:.1f}x^2 + {b_pwCurrent:.1f}x)",
)

plt.plot(
    x,
    y_scale - (a_pwCurrent * x**2 + b_pwCurrent * x),
    "x",
    label="scaled_data - scaled_curve_fit",
)

plt.legend()

plt.title(f"phaseWireCurrent fitting: {os.path.basename(file_U8II_phase_fault)}")
plt.xlabel("rxThrottle")
plt.ylabel("phaseWireCurrent")
plt.show()


# =============================================================================
# %% Read simulation data

# del df
df = read_file(file_sim)

plt.figure()

plt.plot(
    # df["rxThrottle"],
    df["busbarCurrent"],
    "o",
    alpha=0.2,
    label="busbarCurrent",
)
plt.plot(
    # df["rxThrottle"],
    df["phaseWireCurrent"],
    "o",
    alpha=0.2,
    label="phaseWireCurrent",
)
plt.legend()
plt.show()

# %% RPM
x = df["rxThrottle"]
y = df["rpm"]

y_scale = df["rpm"] * ((6 * 4.2) / df["voltage"])

x_fit = numpy.linspace(min(x), max(x), 100)
y_fit = a_rpm * x_fit**2 + b_rpm * x_fit

plt.plot(x, y_scale, "o", alpha=0.2, label="scaled_data")
plt.plot(x_fit, y_fit, "-", label=f"scaled_curve_fit (y = {a_rpm:.1f}x^2 + {b_rpm:.1f}x)")
plt.plot(
    x,
    y_scale - (a_rpm * x**2 + b_rpm * x),
    "x",
    label="scaled_data - scaled_curve_fit",
)

plt.legend()

plt.title(f"RPM fitting: {os.path.basename(file_U8II_phase_fault)}")
plt.xlabel("rxThrottle")
plt.ylabel("RPM")
# plt.show()


# %% Currents

plt.figure()
y = df["phaseWireCurrent"]
y_scale = df["phaseWireCurrent"] * ((6 * 4.2) / df["voltage"])

x_fit = numpy.linspace(min(x), max(x), 100)
y_fit = a_pwCurrent * x_fit**2 + b_pwCurrent * x_fit

plt.plot(x, y_scale, "o", alpha=0.2, label="scaled_data")
plt.plot(
    x_fit,
    y_fit,
    "-",
    label=f"scaled_curve_fit (y = {a_pwCurrent:.1f}x^2 + {b_pwCurrent:.1f}x)",
)

plt.plot(
    x,
    y_scale - (a_pwCurrent * x**2 + b_pwCurrent * x),
    "x",
    label="scaled_data - scaled_curve_fit",
)

plt.legend()

plt.title(f"phaseWireCurrent fitting: {os.path.basename(file_U8II_phase_fault)}")
plt.xlabel("rxThrottle")
plt.ylabel("phaseWireCurrent")
plt.show()
