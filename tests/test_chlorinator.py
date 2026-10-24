"""Tests for the Chlorinator device model."""

import pytest
from modbus_connection.mock import MockModbusConnection
from semver import Version

from aquark_modbus.chlorinator import Chlorinator
from aquark_modbus.const import DeviceType


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
    unit.input[13] = 2
    unit.input[14] = 0x0103  # 259 -> minor 1, patch 3
    unit.input[15] = 1

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()

    readings_report = await chlorinator.async_update_readings()
    assert "model" in readings_report.updated
    assert readings_report.complete
    assert chlorinator.model.version == Version(2, 1, 3)
    assert chlorinator.model.device_type is DeviceType.INVER_CLEAR

    settings_report = await chlorinator.async_update_settings()
    assert settings_report.updated == set()
    assert settings_report.complete

    full_report = await chlorinator.async_update()
    assert "model" in full_report.updated
    assert full_report.complete


async def test_chlorinator_read_raw(mock_unit: MockModbusConnection) -> None:
    """Raw register reads return undecoded register contents for diagnostics."""
    unit = mock_unit.for_unit(8)
    unit.input[13] = 1
    unit.input[14] = 513
    unit.input[15] = 6

    chlorinator = Chlorinator(unit)
    await chlorinator.async_ensure_setup()

    raw = await chlorinator.async_read_raw()
    assert raw["input"][13] == 1
    assert raw["input"][14] == 513
    assert raw["input"][15] == 6
