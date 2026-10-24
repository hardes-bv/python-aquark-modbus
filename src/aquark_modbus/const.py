"""Constants and enumerations for Aquark Modbus devices."""

from enum import IntEnum


class DeviceType(IntEnum):
    """Known Aquark chlorinator device types."""

    MR_PURE = 0
    INVER_CLEAR = 1
    MR_PURE_PRO = 6


class OperatingMode(IntEnum):
    """Chlorinator operating modes."""

    SHUTDOWN = 0
    AUTO_MODE = 1
    SHOCK_MODE = 2
    FACTORY_TEST_MODE = 3


class WaterQuality(IntEnum):
    """Water quality ratings."""

    POOR = 0
    GOOD = 1
    PERFECT = 2
