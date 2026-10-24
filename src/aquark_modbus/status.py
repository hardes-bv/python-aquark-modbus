"""Status and fault flags from the chlorinator."""

from modbus_connection.model import Component, discrete_input


class Status(Component):
    """Status information and fault flags from the chlorinator."""

    discrete_ranges = (
        (0, 9),  # 0x0000 - Fault and protection flags
        (48, 52),  # 0x0030 - System status and maintenance flags
    )

    # 0x0000 (0) - Power fault flag
    _power_fault = discrete_input(0)

    # 0x0001 (1) - pH regulation fault flag
    _ph_regulation_fault = discrete_input(1)

    # 0x0002 (2) - ORP regulation fault flag
    _orp_regulation_fault = discrete_input(2)

    # 0x0003 (3) - Controller over-temperature protection flag
    _controller_over_temperature_protection = discrete_input(3)

    # 0x0004 (4) - Electrolytic cell low-temperature protection flag
    _electrolytic_cell_low_temperature_protection = discrete_input(4)

    # 0x0005 (5) - Wi-Fi connection failure flag
    _wifi_connection_failure = discrete_input(5)

    # 0x0006 (6) - pH sensor data failed to read flag
    _ph_sensor_data_failed_to_read = discrete_input(6)

    # 0x0007 (7) - ORP sensor data failed to read flag
    _orp_sensor_data_failed_to_read = discrete_input(7)

    # 0x0008 (8) - Power module data failed to read flag
    _power_module_data_failed_to_read = discrete_input(8)

    # 0x0009 (9) - External RS485 communication failure flag
    _external_rs485_communication_failure = discrete_input(9)

    # 0x0030 (48) - Calibration required flag
    _calibration_required = discrete_input(48)

    # 0x0031 (49) - Probes need replacement flag
    _probes_need_replacement = discrete_input(49)

    # 0x0032 (50) - Flow switch flag
    _flow_switch = discrete_input(50)

    # 0x0033 (51) - Need to add acid flag
    _need_to_add_acid = discrete_input(51)

    # 0x0034 (52) - Need to add salt flag
    _need_to_add_salt = discrete_input(52)

    @property
    def power_fault(self) -> bool | None:
        """Return the power fault status flag."""
        return self._power_fault

    @property
    def ph_regulation_fault(self) -> bool | None:
        """Return the pH regulation fault status flag."""
        return self._ph_regulation_fault

    @property
    def orp_regulation_fault(self) -> bool | None:
        """Return the ORP regulation fault status flag."""
        return self._orp_regulation_fault

    @property
    def controller_over_temperature_protection(self) -> bool | None:
        """Return the controller over-temperature protection status flag."""
        return self._controller_over_temperature_protection

    @property
    def electrolytic_cell_low_temperature_protection(self) -> bool | None:
        """Return the electrolytic cell low-temperature protection status flag."""
        return self._electrolytic_cell_low_temperature_protection

    @property
    def wifi_connection_failure(self) -> bool | None:
        """Return the Wi-Fi connection failure status flag."""
        return self._wifi_connection_failure

    @property
    def ph_sensor_data_failed_to_read(self) -> bool | None:
        """Return the pH sensor data failed to read status flag."""
        return self._ph_sensor_data_failed_to_read

    @property
    def orp_sensor_data_failed_to_read(self) -> bool | None:
        """Return the ORP sensor data failed to read status flag."""
        return self._orp_sensor_data_failed_to_read

    @property
    def power_module_data_failed_to_read(self) -> bool | None:
        """Return the power module data failed to read status flag."""
        return self._power_module_data_failed_to_read

    @property
    def external_rs485_communication_failure(self) -> bool | None:
        """Return the external RS485 communication failure status flag."""
        return self._external_rs485_communication_failure

    @property
    def calibration_required(self) -> bool | None:
        """Return the calibration required status flag."""
        return self._calibration_required

    @property
    def probes_need_replacement(self) -> bool | None:
        """Return the probes need replacement status flag."""
        return self._probes_need_replacement

    @property
    def flow_switch(self) -> bool | None:
        """Return the flow switch status flag."""
        return self._flow_switch

    @property
    def need_to_add_acid(self) -> bool | None:
        """Return the need to add acid status flag."""
        return self._need_to_add_acid

    @property
    def need_to_add_salt(self) -> bool | None:
        """Return the need to add salt status flag."""
        return self._need_to_add_salt
