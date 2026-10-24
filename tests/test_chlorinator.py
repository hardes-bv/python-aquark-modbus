"""Tests for the Chlorinator device model."""

import pytest
from modbus_connection.mock import MockModbusConnection
from semver import Version

from aquark_modbus.chlorinator import Chlorinator
from aquark_modbus.const import DeviceType
from aquark_modbus.readings import Readings


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
    unit.input[13] = 2
    unit.input[14] = 0x0103  # 259 -> minor 1, patch 3
    unit.input[15] = 1

    chlorinator = Chlorinator(unit)
    assert isinstance(chlorinator.readings, Readings)
    await chlorinator.async_ensure_setup()

    readings_report = await chlorinator.async_update_readings()
    assert "readings" in readings_report.updated
    assert readings_report.complete
    assert chlorinator.readings.orp == -166
    assert chlorinator.model.version == Version(2, 1, 3)
    assert chlorinator.model.device_type is DeviceType.INVER_CLEAR

    settings_report = await chlorinator.async_update_settings()
    assert settings_report.updated == set()
    assert settings_report.complete

    full_report = await chlorinator.async_update()
    assert "readings" in full_report.updated
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
    unit.input[13] = 1
    unit.input[14] = 0x0100
    unit.input[15] = 0

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()
    await chlorinator.async_update_readings()

    assert chlorinator.readings.orp == expected_orp


async def test_chlorinator_read_raw(mock_unit: MockModbusConnection) -> None:
    """Raw register reads return undecoded register contents for diagnostics."""
    unit = mock_unit.for_unit(8)
    unit.input[0] = 65370
    unit.input[13] = 1
    unit.input[14] = 513
    unit.input[15] = 6

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()

    raw = await chlorinator.async_read_raw()
    assert raw["input"][0] == 65370
    assert raw["input"][13] == 1
    assert raw["input"][14] == 513
    assert raw["input"][15] == 6
