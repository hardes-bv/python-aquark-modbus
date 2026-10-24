"""Tests for custom register fields."""

from datetime import time as dt_time

from semver import Version

from aquark_modbus.fields import TimeField, VersionField, time, version


def test_version_field_decoding() -> None:
    """A VersionField decodes two 16-bit register words into a semver Version."""
    field = VersionField(13)
    assert field.count == 2
    # Register 13 = 1, Register 14 = 0x0201 (minor=2, patch=1)
    decoded = field.decode([1, 0x0201])
    assert decoded == Version(1, 2, 1)


def test_version_helper_function() -> None:
    """The version helper creates a VersionField with the specified address."""
    field = version(13, stride=2)
    assert isinstance(field, VersionField)
    assert field.address == 13
    assert field.stride == 2


def test_time_field_decoding() -> None:
    """A TimeField decodes a 16-bit register word into a datetime.time object."""
    field = TimeField(6)
    assert field.count == 1
    # Register 6 = (8 << 8) | 30 (0x081E -> 08:30)
    decoded = field.decode([(8 << 8) | 30])
    assert decoded == dt_time(8, 30)


def test_time_helper_function() -> None:
    """The time helper creates a TimeField with the specified address."""
    field = time(6, stride=1)
    assert isinstance(field, TimeField)
    assert field.address == 6
    assert field.stride == 1
