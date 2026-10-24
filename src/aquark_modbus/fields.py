from datetime import time as dt_time

from modbus_connection.model import RegisterField
from semver import Version


def _decode_version(words: list[int]) -> Version:
    """Decode two registers as a semver Version object (major.minor.patch)."""
    major = words[0]
    minor = (words[1] >> 8) & 0xFF
    patch = words[1] & 0xFF
    return Version(major, minor, patch)


class VersionField(RegisterField[Version]):
    """A software version (major.minor.patch) over two registers (read-only)."""

    def __init__(self, address: int, *, stride: int = 0) -> None:
        super().__init__(address, count=2, stride=stride)

    def decode(self, words: list[int], scale_exponent: int | None = None) -> Version:
        return _decode_version(words)


def version(address: int, *, stride: int = 0) -> VersionField:
    """A software version (major.minor.patch) over two registers (read-only)."""
    return VersionField(address, stride=stride)


def _decode_time(words: list[int]) -> dt_time:
    """Decode a register as a datetime.time object (hour:minute)."""
    hour = (words[0] >> 8) & 0xFF
    minute = words[0] & 0xFF
    return dt_time(hour, minute)


class TimeField(RegisterField[dt_time]):
    """A time of day (hour:minute) in a single register (read-only)."""

    def __init__(self, address: int, *, stride: int = 0) -> None:
        super().__init__(address, count=1, stride=stride)

    def decode(self, words: list[int], scale_exponent: int | None = None) -> dt_time:
        return _decode_time(words)


def time(address: int, *, stride: int = 0) -> TimeField:
    """A time of day (hour:minute) in a single register (read-only)."""
    return TimeField(address, stride=stride)
