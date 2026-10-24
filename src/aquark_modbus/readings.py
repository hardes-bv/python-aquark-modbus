"""Readings from the chlorinator."""

from modbus_connection.model import Component, enum, gauge, integer

from aquark_modbus.const import WaterQuality


class Readings(Component):
    """Reading information and telemetry from the chlorinator."""

    register_space = "input"

    register_ranges = (
        (0, 12),  # Telemetry readings (ORP, pH, EC, temps, chlorine, specs, V/I)
    )

    # 0x0000 (0) - Oxidation-reduction potential (ORP) in mV [-2000..2000]
    _orp = integer(0, unit="mV")

    # 0x0001 (1) - pH reading [0..1400], divided by 100
    _ph = gauge(1, 0.01, signed=False)

    # 0x0002 (2) - Electrical conductivity in ppm [0..9999]
    _electrical_conductivity = integer(2, signed=False, unit="ppm")

    # 0x0003 (3) - Pool water temperature in °C [-1000..1000], divided by 10
    _pool_temperature = gauge(3, 0.1, nan=0x7FFF, unit="°C")

    # 0x0004 (4) - Controller temperature in °C [-1000..1000], divided by 10
    _controller_temperature = gauge(4, 0.1, nan=0x7FFF, unit="°C")

    # 0x0005 (5) - Chlorine production percentage in % [0..120]
    _chlorine_production = integer(5, signed=False, unit="%")

    # 0x0006 (6) - Water quality rating [0..2]
    _water_quality = enum(6, WaterQuality)

    # 0x0007 (7) - Electrolytic plate specifications in g [13..25]
    _electrolytic_plate_specifications = integer(7, signed=False, unit="g")

    # 0x0008 (8) - SJ reading in mV [0..3300]
    _sj = integer(8, signed=False, unit="mV")

    # 0x0009 (9) - SI reading [0..4095]
    _si = integer(9, signed=False)

    # 0x000A (10) - SV reading [0..4095]
    _sv = integer(10, signed=False)

    # 0x000B (11) - Electrolytic current in A [0..1000], divided by 100
    _electrolytic_current = gauge(11, 0.01, signed=False, unit="A")

    # 0x000C (12) - Electrolytic voltage in V [0..2400], divided by 100
    _electrolytic_voltage = gauge(12, 0.01, signed=False, unit="V")

    @property
    def orp(self) -> int | None:
        """Return the oxidation-reduction potential (ORP) in millivolts (mV)."""
        return self._orp

    @property
    def ph(self) -> float | None:
        """Return the pH reading."""
        return self._ph

    @property
    def electrical_conductivity(self) -> int | None:
        """Return the electrical conductivity in parts per million (ppm)."""
        return self._electrical_conductivity

    @property
    def pool_temperature(self) -> float | None:
        """Return the pool water temperature in degrees Celsius (°C)."""
        return self._pool_temperature

    @property
    def controller_temperature(self) -> float | None:
        """Return the controller temperature in degrees Celsius (°C)."""
        return self._controller_temperature

    @property
    def chlorine_production(self) -> int | None:
        """Return the chlorine production percentage (%)."""
        return self._chlorine_production

    @property
    def water_quality(self) -> WaterQuality | None:
        """Return the water quality rating."""
        return self._water_quality

    @property
    def electrolytic_plate_specifications(self) -> int | None:
        """Return the electrolytic plate specifications in grams (g)."""
        return self._electrolytic_plate_specifications

    @property
    def sj(self) -> int | None:
        """Return the sj reading in millivolts (mV)."""
        return self._sj

    @property
    def si(self) -> int | None:
        """Return the si reading."""
        return self._si

    @property
    def sv(self) -> int | None:
        """Return the sv reading."""
        return self._sv

    @property
    def electrolytic_current(self) -> float | None:
        """Return the electrolytic current in amperes (A)."""
        return self._electrolytic_current

    @property
    def electrolytic_voltage(self) -> float | None:
        """Return the electrolytic voltage in volts (V)."""
        return self._electrolytic_voltage
