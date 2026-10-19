"""Exceptions raised by the Aquark Modbus client."""


class AquarkError(Exception):
    """Base error for the library: a bad value or undecodable data."""


class AquarkConnectionError(AquarkError):
    """The Modbus transport failed while talking to the device."""
