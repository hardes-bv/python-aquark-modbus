"""Exceptions raised by the Aquark Modbus client."""

from modbus_connection import ModbusError


class AquarkError(ModbusError):
    """Base error for the library: a bad value or undecodable data.

    Every exception this library raises derives from it. It in turn derives
    from ``modbus_connection.ModbusError``, so ``except ModbusError`` is a
    safe catch-all: it matches both the raw errors a poll raises and the
    translated errors ``async_validate`` and ``async_ensure_setup`` raise.
    """


class AquarkConnectionError(AquarkError):
    """The Modbus transport failed while talking to the device."""


class AquarkTimeoutError(AquarkConnectionError):
    """The link is up, but the device behind it did not answer.

    An RS485 gateway keeps its socket open while the device behind it is
    silent.
    """


class AquarkRefusedError(AquarkError):
    """The device answered, but refused the request.

    Some boards refuse a value the register table documents, such as a working
    mode the model does not have.
    """


class NotAnAquarkDeviceError(AquarkError):
    """The device answers Modbus, but not like the expected Aquark device."""
