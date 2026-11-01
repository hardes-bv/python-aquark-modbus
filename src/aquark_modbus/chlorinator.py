"""Mr Pure (Pro)

A chlorinator for pools.
"""

from collections.abc import Generator, Iterable
from contextlib import contextmanager

from modbus_connection import (
    GatewayPathUnavailableError,
    GatewayTargetError,
    ModbusError,
    ModbusExceptionError,
    ModbusTimeoutError,
    ModbusUnit,
)
from modbus_connection.model import (
    Device,
    Raw,
    UpdateReport,
)

from .exceptions import (
    AquarkConnectionError,
    AquarkError,
    AquarkRefusedError,
    AquarkTimeoutError,
    NotAnAquarkDeviceError,
)
from .model import Model
from .readings import Readings
from .settings import Settings
from .status import Status

# Attribute names of the sub-systems each update method reads.
READINGS = (
    "model",
    "readings",
    "status",
)
SETTINGS = ("settings",)
ALL = (*READINGS, *SETTINGS)

# A gateway in "Modbus TCP to RTU" mode answers with one of these when the
# board behind it stays silent: the chlorinator is off or unwired.
_SILENT_BEHIND_GATEWAY = (GatewayPathUnavailableError, GatewayTargetError)


@contextmanager
def _translated_errors() -> Generator[None]:
    """Turn transport and device errors into the library's own exceptions."""
    try:
        yield
    except _SILENT_BEHIND_GATEWAY as err:
        raise AquarkTimeoutError(f"the chlorinator does not answer: {err}") from err
    except ModbusExceptionError as err:
        raise AquarkRefusedError(f"the chlorinator refused the request: {err}") from err
    except ModbusTimeoutError as err:
        raise AquarkTimeoutError(f"the chlorinator does not answer: {err}") from err
    except ModbusError as err:
        raise AquarkConnectionError(f"cannot reach the chlorinator: {err}") from err
    except ValueError as err:
        raise AquarkError(str(err)) from err


class Chlorinator(Device):
    """A chlorinator reached through a ``ModbusUnit``.

    Every error this class raises is a ``ModbusError``, so that is the safe
    catch-all. Polls (``async_update*``) keep partial failures in the report
    they return, and raise a ``ModbusError`` subclass when the link dies or
    the device stays silent before anything answers. The one-time reads
    (``async_ensure_setup`` and ``async_validate``) translate those failures
    into the library's own exceptions.
    """

    def __init__(self, unit: ModbusUnit) -> None:
        super().__init__(unit)

        # Sub-systems, each a Component. Repeated ones take an index.
        self.model = Model(unit)
        self.readings = Readings(unit)
        self.status = Status(unit)
        self.settings = Settings(unit)

    async def _async_setup(self) -> None:
        """Read what never changes, and settle which sub-systems this model has.

        A one-shot identity read, like ``async_validate``: failures surface
        as the library's own exceptions, and a failed run is retried on the
        next call.
        """
        with _translated_errors():
            await self.model.async_update()  # identity: read once, never polled

    async def async_update_readings(self) -> UpdateReport:
        """Refresh what the controller measures.

        Partial failures land in the report; a dead link or total silence
        raises a ``ModbusError`` subclass.
        """
        return await self.async_poll(READINGS)

    async def async_update_settings(self) -> UpdateReport:
        """Refresh what the controller has been configured to do.

        Partial failures land in the report; a dead link or total silence
        raises a ``ModbusError`` subclass.
        """
        return await self.async_poll(SETTINGS)

    async def async_update(self) -> UpdateReport:
        """Refresh all components.

        Partial failures land in the report; a dead link or total silence
        raises a ``ModbusError`` subclass.
        """
        report = await self.async_poll(READINGS)
        return await self.async_poll(SETTINGS, report)

    async def async_read_raw(self, names: Iterable[str] = ALL) -> Raw:
        """Every register this device reads, undecoded, for diagnostics."""
        return await super().async_read_raw(names)

    async def async_validate(self) -> None:
        """Check the device answers like this board, or raise.

        Raises ``NotAnAquarkDeviceError`` when the device refuses the board's
        registers or its values make no sense for the board,
        ``AquarkTimeoutError`` when nothing answers behind a live link, and
        ``AquarkConnectionError`` when the link fails.
        """
        try:
            with _translated_errors():
                await self.readings.async_update(notify=False)
                await self.settings.async_update(notify=False)
        except AquarkRefusedError as err:
            # Another Aquark board, like the PC1004, answers every read of
            # this table with an exception response.
            raise NotAnAquarkDeviceError(
                f"the device refuses the registers of this board: {err}"
            ) from err

        # settings = self.settings
        # if settings.function is None or settings.working_mode is None:
        #     raise NotAmAquarkDeviceError("unexpected function or working mode")
