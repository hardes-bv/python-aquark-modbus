"""Readings from the chlorinator."""

from modbus_connection.model import Component, integer


class Readings(Component):
    """Reading information and telemetry from the chlorinator."""

    register_space = "input"

    register_ranges = (
        (0, 0),  # ORP reading
    )

    # 0x0000 (0) - Oxidation-reduction potential (ORP) in mV [-2000..2000]
    _orp = integer(0, unit="mV")

    @property
    def orp(self) -> int | None:
        """Return the oxidation-reduction potential (ORP) in millivolts (mV)."""
        return self._orp
