"""Constants and enumerations for Aquark Modbus devices."""

from enum import IntEnum


class DeviceType(IntEnum):
    """Known Aquark chlorinator device types."""

    MR_PURE = 0
    INVER_CLEAR = 1
    MR_PURE_PRO = 6
