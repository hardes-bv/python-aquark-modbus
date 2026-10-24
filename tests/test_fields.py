"""Tests for custom register fields."""

from semver import Version

from aquark_modbus.fields import VersionField, version


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
