"""Mr Pure (Pro)

A chlorinator for pools.
"""

from collections.abc import Iterable

from modbus_connection import ModbusUnit
from modbus_connection.model import (
    Device,
    Raw,
    UpdateReport,
)

from .components import Model

# Attribute names of the sub-systems each update method reads.
READINGS = ("model",)
SETTINGS: tuple[str, ...] = ()
ALL = (*READINGS, *SETTINGS)


class Chlorinator(Device):
    """A chlorinator reached through a ``ModbusUnit``."""

    def __init__(self, unit: ModbusUnit) -> None:
        super().__init__(unit)

        # Sub-systems, each a Component. Repeated ones take an index.
        self.model = Model(unit)

    async def _async_setup(self) -> None:
        """Read what never changes, and settle which sub-systems this model has."""
        await self.model.async_update()  # identity: read once, never polled

    async def async_update_readings(self) -> UpdateReport:
        """Refresh what the controller measures."""
        return await self.async_poll(READINGS)

    async def async_update_settings(self) -> UpdateReport:
        """Refresh what the controller has been configured to do."""
        return await self.async_poll(SETTINGS)

    async def async_update(self) -> UpdateReport:
        """Refresh all components."""
        report = await self.async_poll(READINGS)
        return await self.async_poll(SETTINGS, report)

    async def async_read_raw(self, names: Iterable[str] = ALL) -> Raw:
        """Every register this device reads, undecoded, for diagnostics."""
        return await super().async_read_raw(names)
