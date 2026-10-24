from modbus_connection.model import Component, enum
from semver import Version

from aquark_modbus.const import DeviceType
from aquark_modbus.fields import version


class Model(Component):
    """Reading information about the chlorinator model."""

    register_space = "input"

    register_ranges = (
        (13, 15),  # Model and firmware information
    )

    # Read both version registers into a custom-written `VersionField` type
    # 0x000D (13) - Software master version number (for example, 2 in V2.1.3)
    # 0x000E (14) - Software sub-version number (in V2.1.3:
    # lower 8 bits: 3, higher 8 bits: 1)
    _version = version(13)

    # 0x000F (15) - Product type / Device type
    _device_type = enum(15, DeviceType)

    @property
    def version(self) -> Version | None:
        return self._version

    @property
    def device_type(self) -> DeviceType | None:
        return self._device_type
