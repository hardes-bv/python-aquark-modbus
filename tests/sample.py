# Sample Python file testing a connection to a real device

import asyncio

from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

from aquark_modbus.chlorinator import Chlorinator


async def test_live():
    conn = ModbusConnection(ModbusTcpParams(host="172.16.25.30", port=502))
    unit = conn.for_unit(8)
    chlorinator = Chlorinator(unit)

    await chlorinator.async_ensure_setup()
    print("Chlorinator setup succeeded.")
    print(f"Device type: {chlorinator.model.device_type}")
    print(f"Model version: {chlorinator.model.version}")
    print(
        f"Major: {chlorinator.model.version.major}, "
        f"Minor: {chlorinator.model.version.minor}, "
        f"Patch: {chlorinator.model.version.patch}"
    )

    report = await chlorinator.async_update_readings()
    print("Readings update report:", report)
    print(f"Model version after poll: {chlorinator.model.version}")

    await conn.close()


asyncio.run(test_live())
