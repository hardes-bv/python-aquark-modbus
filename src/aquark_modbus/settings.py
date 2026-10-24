"""Settings and configuration from the chlorinator."""

from datetime import time as dt_time

from modbus_connection.model import Component, enum, gauge, integer

from aquark_modbus.const import OperatingMode
from aquark_modbus.fields import time


class Settings(Component):
    """Settings and configuration for the chlorinator."""

    register_space = "holding"

    register_ranges = (
        (0, 7),  # Configuration settings
    )

    # 0x0000 (0) - Operating mode [0..3]
    _operating_mode = enum(0, OperatingMode)

    # 0x0001 (1) - Parallel address setting [1..28]
    _parallel_address_setting = integer(1, signed=False)

    # 0x0002 (2) - Ideal ORP setting in mV [650..800]
    _ideal_orp_settings = integer(2, signed=False, unit="mV")

    # 0x0003 (3) - Ideal pH setting [720..760], divided by 100
    _ideal_ph_setting = gauge(3, 0.01, signed=False)

    # 0x0004 (4) - Pool volume setting in m³ [5..120]
    _pool_volume_settings = integer(4, signed=False, unit="m³")

    # 0x0005 (5) - Timer enable setting [0..1]
    _timer_enable = integer(5, signed=False)

    # 0x0006 (6) - Power on time (hour:minute)
    _power_on_time = time(6)

    # 0x0007 (7) - Power off time (hour:minute)
    _power_off_time = time(7)

    @property
    def operating_mode(self) -> OperatingMode | None:
        """Return the operating mode."""
        return self._operating_mode

    @property
    def parallel_address_setting(self) -> int | None:
        """Return the parallel address setting."""
        return self._parallel_address_setting

    @property
    def ideal_orp_settings(self) -> int | None:
        """Return the ideal ORP setting in millivolts (mV)."""
        return self._ideal_orp_settings

    @property
    def ideal_ph_setting(self) -> float | None:
        """Return the ideal pH setting."""
        return self._ideal_ph_setting

    @property
    def pool_volume_settings(self) -> int | None:
        """Return the pool volume setting in cubic meters (m³)."""
        return self._pool_volume_settings

    @property
    def timer_enable(self) -> int | None:
        """Return the timer enable setting."""
        return self._timer_enable

    @property
    def power_on_time(self) -> dt_time | None:
        """Return the scheduled power-on time."""
        return self._power_on_time

    @property
    def power_off_time(self) -> dt_time | None:
        """Return the scheduled power-off time."""
        return self._power_off_time
