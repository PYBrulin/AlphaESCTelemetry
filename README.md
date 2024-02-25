# T-Motor Alpha ESC Telemetry

Python library to read, analyse and replay telemetry data from T-Motor Alpha ESCs.

Main source of information regarding this telemetry and the Alpha ESC series comes from the page:
https://wiki.paparazziuav.org/wiki/Alpha_esc_with_telemetry_output

## Installation

As a python package:

```bash
cd /path/to/this/repo
pip install -e .
```

Then you can import the `AlphaESCTelemetry` package in your python scripts.

```python
import AlphaESCTelemetry
```

Or you can run the scripts directly from the command line.

```bash
cd /path/to/this/repo/AlphaESCTelemetry
python captureESCTelemetry.py [POLES_N (default=21)]
```

## Usage

| Script                     | Description                                                                                        |
| -------------------------- | -------------------------------------------------------------------------------------------------- |
| `captureESCTelemetry.py`   | Capture, process and store decoded and raw telemetry packets from an Alpha T-Motor ESC.            |
| `decodeESCTelemetry.py`    | Decode an existing binary files containing raw telemetry packets capture from an Alpha T-Motor ESC |
| `plot_export_telemetry.py` | Plot telemetry data from a CSV or BIN file using matplotlib.                                       |
| `plot_telemetry.py`        | Plot telemetry data from a CSV or BIN file.                                                        |
| `replay_telemetry.py`      | Script to load a binary file and transmit it over serial port to simulate a telemetry stream       |

Call `--help` to see the available options for each script.

## Output

![U8II-190KV Thrust test](2023-07-24T14-59-31.png)

![U8II-190KV Phase fault](2023-02-24T12-56-38_AlphaTelemetry_faultyESC_phaseFault.png)
