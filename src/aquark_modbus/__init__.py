"""Asynchronous Modbus client for Aquark chlorinator devices."""

from importlib.metadata import version

from aquark_modbus.chlorinator import Chlorinator
from aquark_modbus.const import DeviceType, WaterQuality
from aquark_modbus.exceptions import AquarkConnectionError, AquarkError

# The release workflow stamps the version into pyproject.toml from the git
# tag, so the installed distribution metadata is the single source of truth.
__version__ = version("aquark-modbus")

__all__ = [
    "AquarkConnectionError",
    "AquarkError",
    "Chlorinator",
    "DeviceType",
    "WaterQuality",
    "__version__",
]
