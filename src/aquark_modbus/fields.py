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
