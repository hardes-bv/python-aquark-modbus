"""Tests for the Chlorinator device model."""

import pytest
from modbus_connection.mock import MockModbusConnection
from semver import Version

from aquark_modbus.chlorinator import Chlorinator
from aquark_modbus.const import DeviceType, WaterQuality
from aquark_modbus.readings import Readings
from aquark_modbus.status import Status


@pytest.fixture
def mock_unit() -> MockModbusConnection:
    """Fixture providing a mock Modbus connection."""
    return MockModbusConnection()


async def test_chlorinator_reads_firmware_version(
    mock_unit: MockModbusConnection,
) -> None:
    """The Chlorinator decodes input registers 13 and 14 into a semver Version."""
    unit = mock_unit.for_unit(8)
    unit.input[13] = 1
    unit.input[14] = 0x0201  # 513 -> minor 2, patch 1
    unit.input[15] = 6

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()

    assert chlorinator.model.version == Version(1, 2, 1)
    assert chlorinator.model.device_type is DeviceType.MR_PURE_PRO


@pytest.mark.parametrize(
    ("raw_value", "expected_type"),
    [
        (0, DeviceType.MR_PURE),
        (1, DeviceType.INVER_CLEAR),
        (6, DeviceType.MR_PURE_PRO),
    ],
)
async def test_chlorinator_reads_known_device_types(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_type: DeviceType,
) -> None:
    """Input register 15 decodes into the corresponding DeviceType enumeration."""
    unit = mock_unit.for_unit(8)
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = raw_value

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()

    assert chlorinator.model.device_type is expected_type


async def test_chlorinator_update_cycle(mock_unit: MockModbusConnection) -> None:
    """Updating readings and settings refreshes sub-systems."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 65370  # -166 mV
    unit.input[1] = 720  # 7.2 pH
    unit.input[2] = 3200  # 3200 ppm
    unit.input[3] = 285  # 28.5 °C
    unit.input[4] = 450  # 45.0 °C
    unit.input[5] = 80  # 80%
    unit.input[6] = 2  # PERFECT
    unit.input[7] = 15  # 15 g
    unit.input[8] = 1650  # 1650 mV
    unit.input[9] = 2048  # 2048
    unit.input[10] = 1024  # 1024
    unit.input[11] = 500  # 5.0 A
    unit.input[12] = 1200  # 12.0 V
    unit.input[13] = 2
    unit.input[14] = 0x0103  # 259 -> minor 1, patch 3
    unit.input[15] = 1
    unit.discrete[0] = False
    unit.discrete[1] = False
    unit.discrete[2] = True
    unit.discrete[3] = True
    unit.discrete[4] = False
    unit.discrete[5] = True
    unit.discrete[6] = False
    unit.discrete[7] = True
    unit.discrete[8] = False
    unit.discrete[9] = True
    unit.discrete[48] = True
    unit.discrete[49] = False
    unit.discrete[50] = True
    unit.discrete[51] = False
    unit.discrete[52] = True

    chlorinator = Chlorinator(unit)
    assert isinstance(chlorinator.readings, Readings)
    assert isinstance(chlorinator.status, Status)
    await chlorinator.async_ensure_setup()

    readings_report = await chlorinator.async_update_readings()
    assert "readings" in readings_report.updated
    assert "status" in readings_report.updated
    assert readings_report.complete
    assert chlorinator.readings.orp == -166
    assert chlorinator.readings.ph == 7.2
    assert chlorinator.readings.electrical_conductivity == 3200
    assert chlorinator.readings.pool_temperature == 28.5
    assert chlorinator.readings.controller_temperature == 45.0
    assert chlorinator.readings.chlorine_production == 80
    assert chlorinator.readings.water_quality is WaterQuality.PERFECT
    assert chlorinator.readings.electrolytic_plate_specifications == 15
    assert chlorinator.readings.sj == 1650
    assert chlorinator.readings.si == 2048
    assert chlorinator.readings.sv == 1024
    assert chlorinator.readings.electrolytic_current == 5.0
    assert chlorinator.readings.electrolytic_voltage == 12.0
    assert chlorinator.status.power_fault is False
    assert chlorinator.status.ph_regulation_fault is False
    assert chlorinator.status.orp_regulation_fault is True
    assert chlorinator.status.controller_over_temperature_protection is True
    assert chlorinator.status.electrolytic_cell_low_temperature_protection is False
    assert chlorinator.status.wifi_connection_failure is True
    assert chlorinator.status.ph_sensor_data_failed_to_read is False
    assert chlorinator.status.orp_sensor_data_failed_to_read is True
    assert chlorinator.status.power_module_data_failed_to_read is False
    assert chlorinator.status.external_rs485_communication_failure is True
    assert chlorinator.status.calibration_required is True
    assert chlorinator.status.probes_need_replacement is False
    assert chlorinator.status.flow_switch is True
    assert chlorinator.status.need_to_add_acid is False
    assert chlorinator.status.need_to_add_salt is True
    assert chlorinator.model.version == Version(2, 1, 3)
    assert chlorinator.model.device_type is DeviceType.INVER_CLEAR

    settings_report = await chlorinator.async_update_settings()
    assert settings_report.updated == set()
    assert settings_report.complete

    full_report = await chlorinator.async_update()
    assert "readings" in full_report.updated
    assert "status" in full_report.updated
    assert full_report.complete


@pytest.mark.parametrize(
    ("raw_value", "expected_orp"),
    [
        (0, 0),
        (650, 650),
        (2000, 2000),
        (65370, -166),
        (63536, -2000),
    ],
)
async def test_chlorinator_reads_orp_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_orp: int,
) -> None:
    """Input register 0 decodes into signed ORP millivolt values."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = raw_value
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = 1
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.orp == expected_orp


@pytest.mark.parametrize(
    ("raw_value", "expected_ph"),
    [
        (0, 0.0),
        (700, 7.0),
        (720, 7.2),
        (1400, 14.0),
    ],
)
async def test_chlorinator_reads_ph_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_ph: float,
) -> None:
    """Input register 1 decodes into scaled pH values."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = raw_value
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = 1
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.ph == expected_ph


@pytest.mark.parametrize(
    ("raw_value", "expected_ec"),
    [
        (0, 0),
        (1200, 1200),
        (3500, 3500),
        (9999, 9999),
    ],
)
async def test_chlorinator_reads_electrical_conductivity_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_ec: int,
) -> None:
    """Input register 2 decodes into electrical conductivity in ppm."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = raw_value
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = 1
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.electrical_conductivity == expected_ec


@pytest.mark.parametrize(
    ("raw_value", "expected_temperature"),
    [
        (0x7FFF, None),
        (0, 0.0),
        (250, 25.0),
        (1000, 100.0),
        (65436, -10.0),
        (64536, -100.0),
    ],
)
async def test_chlorinator_reads_pool_temperature_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_temperature: float | None,
) -> None:
    """Input register 3 decodes into signed pool water temperature in °C."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = raw_value
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = 1
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.pool_temperature == expected_temperature


@pytest.mark.parametrize(
    ("raw_value", "expected_temperature"),
    [
        (0x7FFF, None),
        (0, 0.0),
        (185, 18.5),
        (450, 45.0),
        (1000, 100.0),
        (65436, -10.0),
        (64536, -100.0),
    ],
)
async def test_chlorinator_reads_controller_temperature_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_temperature: float | None,
) -> None:
    """Input register 4 decodes into signed controller temperature in °C."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = raw_value
    unit.input[5] = 50
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.controller_temperature == expected_temperature


@pytest.mark.parametrize(
    ("raw_value", "expected_production"),
    [
        (0, 0),
        (50, 50),
        (100, 100),
        (120, 120),
    ],
)
async def test_chlorinator_reads_chlorine_production_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_production: int,
) -> None:
    """Input register 5 decodes into unsigned chlorine production in %."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.chlorine_production == expected_production


@pytest.mark.parametrize(
    ("raw_value", "expected_quality"),
    [
        (0, WaterQuality.POOR),
        (1, WaterQuality.GOOD),
        (2, WaterQuality.PERFECT),
    ],
)
async def test_chlorinator_reads_water_quality_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_quality: WaterQuality,
) -> None:
    """Input register 6 decodes into the corresponding WaterQuality enumeration."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.water_quality is expected_quality


@pytest.mark.parametrize(
    ("raw_value", "expected_specs"),
    [
        (13, 13),
        (15, 15),
        (25, 25),
    ],
)
async def test_chlorinator_reads_electrolytic_plate_specifications_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_specs: int,
) -> None:
    """Input register 7 decodes into electrolytic plate specifications in grams (g)."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = 1
    unit.input[7] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.electrolytic_plate_specifications == expected_specs


@pytest.mark.parametrize(
    ("raw_value", "expected_sj"),
    [
        (0, 0),
        (1650, 1650),
        (3300, 3300),
    ],
)
async def test_chlorinator_reads_sj_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_sj: int,
) -> None:
    """Input register 8 decodes into unsigned SJ reading in millivolts (mV)."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = 1
    unit.input[7] = 15
    unit.input[8] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.sj == expected_sj


@pytest.mark.parametrize(
    ("raw_value", "expected_si"),
    [
        (0, 0),
        (2048, 2048),
        (4095, 4095),
    ],
)
async def test_chlorinator_reads_si_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_si: int,
) -> None:
    """Input register 9 decodes into unsigned SI reading."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = 1
    unit.input[7] = 15
    unit.input[8] = 1000
    unit.input[9] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.si == expected_si


@pytest.mark.parametrize(
    ("raw_value", "expected_sv"),
    [
        (0, 0),
        (1024, 1024),
        (4095, 4095),
    ],
)
async def test_chlorinator_reads_sv_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_sv: int,
) -> None:
    """Input register 10 decodes into unsigned SV reading."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = 1
    unit.input[7] = 15
    unit.input[8] = 1000
    unit.input[9] = 2000
    unit.input[10] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.sv == expected_sv


@pytest.mark.parametrize(
    ("raw_value", "expected_current"),
    [
        (0, 0.0),
        (500, 5.0),
        (1000, 10.0),
    ],
)
async def test_chlorinator_reads_electrolytic_current_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_current: float,
) -> None:
    """Input register 11 decodes into scaled electrolytic current in amperes (A)."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = 1
    unit.input[7] = 15
    unit.input[8] = 1000
    unit.input[9] = 2000
    unit.input[10] = 1000
    unit.input[11] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.electrolytic_current == expected_current


@pytest.mark.parametrize(
    ("raw_value", "expected_voltage"),
    [
        (0, 0.0),
        (1200, 12.0),
        (2400, 24.0),
    ],
)
async def test_chlorinator_reads_electrolytic_voltage_values(
    mock_unit: MockModbusConnection,
    raw_value: int,
    expected_voltage: float,
) -> None:
    """Input register 12 decodes into scaled electrolytic voltage in volts (V)."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 0
    unit.input[1] = 700
    unit.input[2] = 1000
    unit.input[3] = 250
    unit.input[4] = 200
    unit.input[5] = 50
    unit.input[6] = 1
    unit.input[7] = 15
    unit.input[8] = 1000
    unit.input[9] = 2000
    unit.input[10] = 1000
    unit.input[11] = 500
    unit.input[12] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.electrolytic_voltage == expected_voltage


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_power_fault_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 0 decodes into power fault boolean flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[0] = raw_value
    unit.discrete[1] = False
    unit.discrete[2] = False
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.power_fault is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_ph_regulation_fault_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 1 decodes into pH regulation fault boolean flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[0] = False
    unit.discrete[1] = raw_value
    unit.discrete[2] = False
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.ph_regulation_fault is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_orp_regulation_fault_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 2 decodes into ORP regulation fault boolean flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[0] = False
    unit.discrete[1] = False
    unit.discrete[2] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.orp_regulation_fault is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_controller_over_temperature_protection_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 3 decodes into controller over-temperature protection flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[3] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.controller_over_temperature_protection is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_electrolytic_cell_low_temperature_protection_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 4 decodes into cell low-temperature protection flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[4] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.electrolytic_cell_low_temperature_protection is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_wifi_connection_failure_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 5 decodes into Wi-Fi connection failure boolean flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[5] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.wifi_connection_failure is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_ph_sensor_data_failed_to_read_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 6 decodes into pH sensor data read failure flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[6] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.ph_sensor_data_failed_to_read is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_orp_sensor_data_failed_to_read_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 7 decodes into ORP sensor data read failure flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[7] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.orp_sensor_data_failed_to_read is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_power_module_data_failed_to_read_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 8 decodes into power module data read failure flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[8] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.power_module_data_failed_to_read is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_external_rs485_communication_failure_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 9 decodes into external RS485 communication failure flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[9] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.external_rs485_communication_failure is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_calibration_required_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 48 decodes into calibration required boolean flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[48] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.calibration_required is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_probes_need_replacement_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 49 decodes into probes need replacement boolean flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[49] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.probes_need_replacement is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_flow_switch_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 50 decodes into flow switch boolean flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[50] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.flow_switch is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_need_to_add_acid_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 51 decodes into need to add acid boolean flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[51] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.need_to_add_acid is raw_value


@pytest.mark.parametrize(
    "raw_value",
    [True, False],
)
async def test_chlorinator_reads_need_to_add_salt_values(
    mock_unit: MockModbusConnection,
    raw_value: bool,
) -> None:
    """Discrete input 52 decodes into need to add salt boolean flag."""
    unit = mock_unit.for_unit(8)
    unit.discrete[52] = raw_value
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.status.need_to_add_salt is raw_value


async def test_chlorinator_read_raw(mock_unit: MockModbusConnection) -> None:
    """Raw register reads return undecoded register contents for diagnostics."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 65370
    unit.input[1] = 1400
    unit.input[2] = 3200
    unit.input[3] = 32767
    unit.input[4] = 185
    unit.input[5] = 100
    unit.input[6] = 2
    unit.input[7] = 15
    unit.input[8] = 1650
    unit.input[9] = 2048
    unit.input[10] = 167
    unit.input[11] = 500
    unit.input[12] = 1200
    unit.input[13] = 1
    unit.input[14] = 513
    unit.input[15] = 6
    unit.discrete[0] = False
    unit.discrete[1] = True
    unit.discrete[2] = False
    unit.discrete[3] = True
    unit.discrete[4] = False
    unit.discrete[5] = True
    unit.discrete[6] = False
    unit.discrete[7] = True
    unit.discrete[8] = False
    unit.discrete[9] = True
    unit.discrete[48] = False
    unit.discrete[49] = True
    unit.discrete[50] = False
    unit.discrete[51] = True
    unit.discrete[52] = False

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()

    raw = await chlorinator.async_read_raw()
    assert raw["input"][0] == 65370
    assert raw["input"][1] == 1400
    assert raw["input"][2] == 3200
    assert raw["input"][3] == 32767
    assert raw["input"][4] == 185
    assert raw["input"][5] == 100
    assert raw["input"][6] == 2
    assert raw["input"][7] == 15
    assert raw["input"][8] == 1650
    assert raw["input"][9] == 2048
    assert raw["input"][10] == 167
    assert raw["input"][11] == 500
    assert raw["input"][12] == 1200
    assert raw["input"][13] == 1
    assert raw["input"][14] == 513
    assert raw["input"][15] == 6
    assert raw["discrete"][0] is False
    assert raw["discrete"][1] is True
    assert raw["discrete"][2] is False
    assert raw["discrete"][3] is True
    assert raw["discrete"][4] is False
    assert raw["discrete"][5] is True
    assert raw["discrete"][6] is False
    assert raw["discrete"][7] is True
    assert raw["discrete"][8] is False
    assert raw["discrete"][9] is True
    assert raw["discrete"][48] is False
    assert raw["discrete"][49] is True
    assert raw["discrete"][50] is False
    assert raw["discrete"][51] is True
    assert raw["discrete"][52] is False
