from setuptools import find_packages, setup

setup(
    name="AlphaESCTelemetry",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pyserial",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "alpha-telemetry = AlphaESCTelemetry.alphaTelemetry:main",
            "decode-esc-telemetry = AlphaESCTelemetry.decodeESCTelemetry:main",
        ],
    },
    package_data={
        "AlphaESCTelemetry": ["*.py"],
    },
)
