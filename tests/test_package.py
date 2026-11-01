"""Tests for the package surface and its exception hierarchy."""

import pytest
from modbus_connection import ModbusError

import aquark_modbus
from aquark_modbus import (
    AquarkConnectionError,
    AquarkError,
    AquarkRefusedError,
    AquarkTimeoutError,
    NotAnAquarkDeviceError,
)


def test_version_is_a_string() -> None:
    """The package exposes a non-empty version string."""
    assert isinstance(aquark_modbus.__version__, str)
    assert aquark_modbus.__version__


def test_public_names_are_exported() -> None:
    """Every name listed in __all__ is an attribute of the package."""
    for name in aquark_modbus.__all__:
        assert hasattr(aquark_modbus, name)


def test_connection_error_is_a_aquark_error() -> None:
    """A transport failure can be caught as the library's base error."""
    with pytest.raises(AquarkError):
        raise AquarkConnectionError("device unreachable")


def test_aquark_error_is_an_exception() -> None:
    """The base error derives from Exception and keeps its message."""
    error = AquarkError("bad value")

    assert isinstance(error, Exception)
    assert str(error) == "bad value"


def test_aquark_error_is_a_modbus_error() -> None:
    """The base error derives from ModbusError, the shared catch-all."""
    assert issubclass(AquarkError, ModbusError)


def test_every_public_exception_is_a_modbus_error() -> None:
    """Every public exception is catchable with a single except ModbusError."""
    for error in (
        AquarkConnectionError,
        AquarkRefusedError,
        AquarkTimeoutError,
        NotAnAquarkDeviceError,
    ):
        assert issubclass(error, AquarkError)
        assert issubclass(error, ModbusError)


def test_modbus_error_catches_a_library_exception() -> None:
    """A catch-all except ModbusError matches the library's own exceptions."""
    with pytest.raises(ModbusError):
        raise NotAnAquarkDeviceError("not this board")
