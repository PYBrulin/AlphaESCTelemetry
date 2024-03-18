import logging
from typing import Union

# Set logger name to be "AlphaTelemetry"
logger = logging.getLogger("AlphaTelemetry")
# Set logging level to DEBUG
logger.setLevel(logging.DEBUG)

# fmt: off
# Note: deactivate black formatter temporarily
# temperature decoding table
# Yes, there are a lot of duplicate values. And no, I don't know why there are here.
temp_table = {
    241: 0, 240: 1, 239: 2, 238: 3, 237: 4, 236: 5, 235: 6, 234: 7, 233: 8, 232: 9,  # noqa: F601
    231: 10, 230: 11, 229: 12, 228: 13, 227: 14, 226: 15, 224: 16, 223: 17, 222: 18, 220: 19,  # noqa: F601
    219: 20, 217: 21, 216: 22, 214: 23, 213: 24, 211: 25, 209: 26, 208: 27, 206: 28, 204: 29,  # noqa: F601
    202: 30, 201: 31, 199: 32, 197: 33, 195: 34, 193: 35, 191: 36, 189: 37, 187: 38, 185: 39,  # noqa: F601
    183: 40, 181: 41, 179: 42, 177: 43, 174: 44, 172: 45, 170: 46, 168: 47, 166: 48, 164: 49,  # noqa: F601
    161: 50, 159: 51, 157: 52, 154: 53, 152: 54, 150: 55, 148: 56, 146: 57, 143: 58, 141: 59,  # noqa: F601
    139: 60, 136: 61, 134: 62, 132: 63, 130: 64, 128: 65, 125: 66, 123: 67, 121: 68, 119: 69,  # noqa: F601
    117: 70, 115: 71, 113: 72, 111: 73, 109: 74, 106: 75, 105: 76, 103: 77, 101: 78, 99: 79,  # noqa: F601
    97: 80, 95: 81, 93: 82, 91: 83, 90: 84, 88: 85, 85: 86, 84: 87, 82: 88, 81: 89,  # noqa: F601
    79: 90, 77: 91, 76: 92, 74: 93, 73: 94, 72: 95, 69: 96, 68: 97, 66: 98, 65: 99,  # noqa: F601
    64: 100, 62: 101, 62: 102, 61: 103, 59: 104, 58: 105, 56: 106, 54: 107, 54: 108, 53: 109,  # noqa: F601
    51: 110, 51: 111, 50: 112, 48: 113, 48: 114, 46: 115, 46: 116, 44: 117, 43: 118, 43: 119,  # noqa: F601
    41: 120, 41: 121, 39: 122, 39: 123, 39: 124, 37: 125, 37: 126, 35: 127, 35: 128, 33: 129,  # noqa: F601
    # The following data are purely extrapolations for missing values
    34: 128.5, 36: 127, 38: 123, 40: 122.5, 42: 120, 45: 116.5, 47: 115, 49: 113,  # noqa: F601
    52: 110, 55: 107, 57: 105.5, 60: 103.5, 63: 101, 67: 97.5, 70: 95.5, 71: 95.5,  # noqa: F601
    75: 92.5, 78: 90.5, 80: 89.5, 83: 87.5, 86: 86.5, 87: 86.5, 89: 84.5, 92: 82.5,  # noqa: F601
    94: 81.5, 96: 80.5, 98: 79.5, 100: 78.5, 102: 77.5, 104: 76.5, 107: 74.5, 108: 74.5,  # noqa: F601
    110: 73.5, 112: 72.5, 114: 71.5, 116: 70.5, 118: 69.5, 120: 68.5, 122: 67.5, 124: 66.5,  # noqa: F601
    126: 65.5, 127: 65.5, 129: 64.5, 131: 63.5, 133: 62.5, 135: 61.5, 137: 60.5, 138: 60.5,  # noqa: F601
    140: 59.5, 142: 58.5, 144: 57.5, 145: 57.5, 147: 56.5, 149: 55.5, 151: 54.5, 153: 53.5,  # noqa: F601
    155: 52.5, 156: 52.5, 158: 51.5, 160: 50.5, 162: 49.5, 163: 49.5, 165: 48.5, 167: 47.5,  # noqa: F601
    169: 46.5, 171: 45.5, 173: 44.5, 175: 43.5, 176: 43.5, 178: 42.5, 180: 41.5, 182: 40.5,  # noqa: F601
    184: 39.5, 186: 38.5, 188: 37.5, 190: 36.5, 192: 35.5, 194: 34.5, 196: 33.5, 198: 32.5,  # noqa: F601
    200: 31.5, 203: 29.5, 205: 28.5, 207: 27.5, 210: 25.5, 212: 24.5, 215: 22.5, 218: 20.5,  # noqa: F601
    221: 18.5, 225: 15.5,
}
# fmt: on

ALPHA_ESC_B1 = 0x9B  # byte 1 - header
ALPHA_ESC_B2 = 0x16  # byte 2 - packet size
ALPHA_ESC_PACKET_SIZE = 24  # 22 byte packet + 2 byte checksum
ALPHA_ESC_BAUD = 19200  # fixed baudrate


class AlphaTelemetry:
    """Alpha ESC Telemetry handler"""

    def __init__(self, POLES_N=21) -> None:
        """AlphaTelemetry class initialization.

        Args:
            POLES_N (int, optional): The number of pole pairs for the given motor
            configuration. Used to calculate accurate RPM values based on the
            rotational speed of the electric field. The default value is 21
            (U8II: 36N42P -> 21 magnet pairs).
        """
        self.POLES_N = POLES_N
        self.buf_len = 0
        self.rxbuf = bytearray(ALPHA_ESC_PACKET_SIZE)
        self._baleNumber = 0
        self._rxThrottle = 0
        self._outputThrottle = 0
        self._rpm = 0
        self._busbarVoltage = 0
        self._busbarCurrent = 0
        self._phaseWireCurrent = 0
        self._mosfetTemp = 0
        self._capacitorTemp = 0
        self._statusCode = 0
        self._fault = False
        self._ready = False

    @property
    def baleNumber(self) -> int:
        """Number of telemetry packets sent by the ESC since start-up"""
        return self._baleNumber

    @property
    def rxThrottle(self) -> Union[int, float]:
        """Percentage of throttle input"""
        return self._rxThrottle

    @property
    def outputThrottle(self) -> Union[int, float]:
        """Percentage of throttle output"""
        return self._outputThrottle

    @property
    def rpm(self) -> Union[int, float]:
        """Mechanical rotor speed"""
        return self._rpm

    @property
    def busbarVoltage(self) -> Union[int, float]:
        """Input busbarVoltage of the ESC"""
        return self._busbarVoltage

    @property
    def busbarCurrent(self) -> Union[int, float]:
        """Current drawn in the busbar"""
        return self._busbarCurrent

    @property
    def phaseWireCurrent(self) -> Union[int, float]:
        """Current drawn in the phase"""
        return self._phaseWireCurrent

    @property
    def mosfetTemp(self) -> int:
        """MOSFETs temperature"""
        return self._mosfetTemp

    @property
    def capacitorTemp(self) -> int:
        """Capacitor temperature"""
        return self._capacitorTemp

    @property
    def statusCode(self) -> int:
        """ESC status code"""
        return self._statusCode

    @property
    def fault(self) -> bool:
        """ESC fault state"""
        return self._fault

    @property
    def ready(self) -> bool:
        """Returns if the process buffer has new processed data"""
        if not self._ready:
            return False
        self._ready = False
        return True

    # decodes raw temperature reading
    @classmethod
    def temperature_decode(cls, temp_raw: int, integer_only: bool = True) -> int:
        """Decodes the temperature by matching the value returned by the ESC
        in the mapping table temp_table

        Args:
            temp_raw (int): temperature code

        Returns:
            int: Real temperature in Celsius
        """
        if temp_raw in temp_table.keys():
            if integer_only:
                return int(temp_table[temp_raw])
            return temp_table[temp_raw]

        return 130

    @classmethod
    def calc_checksum(cls, data: bytearray) -> int:
        """Calculate bale checksum

        Args:
            data (bytearray): bale data packet
            n (int): size of data packet

        Returns:
            int: Computed checksum
        """
        checksum = 0
        for d in data[: ALPHA_ESC_PACKET_SIZE - 2]:
            checksum += d
        return checksum

    def capture(self, rxbit: int) -> None:
        """Telemetry acquisition process. Initially focuses on finding the two
        header bytes and then feeds capture data to the reception buffer.

        Args:
            rxbit (bytes): Single byte received
        """

        if self.buf_len == 0:
            if rxbit == ALPHA_ESC_B1:
                self.rxbuf[0] = rxbit
            else:
                self.buf_len = 0

        elif self.buf_len == 1:
            if rxbit == ALPHA_ESC_B2:
                self.rxbuf[1] = rxbit
            else:
                self.buf_len = 0

        else:
            self.rxbuf[self.buf_len] = rxbit

        if self.buf_len == ALPHA_ESC_PACKET_SIZE - 1:
            self.processBuffer()
            self.buf_len = 0
        else:
            self.buf_len += 1

    def processBuffer(self) -> None:
        """Process the buffer and decodes values stored in packet.
        This function should not be called manually.
        """

        res = self.decodeBuffer(self.rxbuf, poles=self.POLES_N, integer_only=False)
        if res is not None:
            self._initialValue = res[0]
            self._baleNumber = res[1]
            self._rxThrottle = res[2]
            self._outputThrottle = res[3]
            self._rpm = res[4]
            self._busbarVoltage = res[5]
            self._busbarCurrent = res[6]
            self._phaseWireCurrent = res[7]
            self._mosfetTemp = res[8]
            self._capacitorTemp = res[9]
            self._statusCode = res[10]
            self._fault = res[10] != 0x0
            self._ready = True

    @classmethod
    def decodeBuffer(cls, buffer, poles: int = 1, integer_only: bool = True):
        # check packet integrity
        checksum_received = (buffer[23] << 8) + buffer[22]
        checksum_calculated = cls.calc_checksum(buffer)

        if checksum_received == checksum_calculated:
            _initialValue = (buffer[0] << 8) + (buffer[1] << 16) + (buffer[2] << 24) + buffer[3]
            _baleNumber = (buffer[4] << 8) + buffer[5]
            _rxThrottle = int((buffer[6] << 8) + buffer[7]) * 100.0 / 1024.0
            _outputThrottle = int((buffer[8] << 8) + buffer[9]) * 100.0 / 1024.0
            _rpm = int((buffer[10] << 8) + buffer[11]) * 10.0 / poles
            _busbarVoltage = int((buffer[12] << 8) + buffer[13]) / 10.0
            _busbarCurrent = int((buffer[14] << 8) + buffer[15]) / 64.0
            _phaseWireCurrent = int((buffer[16] << 8) + buffer[17]) / 64.0
            _mosfetTemp = cls.temperature_decode(buffer[18], integer_only)
            _capacitorTemp = cls.temperature_decode(buffer[19], integer_only)
            _statusCode = (buffer[20] << 8) + buffer[21]
            return [
                _initialValue,
                _baleNumber,
                _rxThrottle,
                _outputThrottle,
                _rpm,
                _busbarVoltage,
                _busbarCurrent,
                _phaseWireCurrent,
                _mosfetTemp,
                _capacitorTemp,
                _statusCode,
            ]
        else:
            logger.error("Checksum differs. Received: {} / Computed: {}".format(checksum_received, checksum_calculated))
            return None
