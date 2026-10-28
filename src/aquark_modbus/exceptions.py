"""Exceptions raised by the Aquark Modbus client."""


class AquarkError(Exception):
    """Base error for the library: a bad value or undecodable data."""


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
