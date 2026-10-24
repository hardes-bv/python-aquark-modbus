# Sample Python file testing a connection to a real device

import asyncio

from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

from aquark_modbus.chlorinator import Chlorinator


async def test_live():
    conn = ModbusConnection(ModbusTcpParams(host="172.16.25.30", port=502))
    unit = conn.for_unit(8)
    chlorinator = Chlorinator(unit)

    report = await chlorinator.async_update()
    print("Chlorinator setup succeeded.")
    print(f"Readings update report: {report}")
    print("")

    print(f"Device type: {chlorinator.model.device_type}")
    print(f"Model version: {chlorinator.model.version}")
    print("")

    print(f"Model version after poll: {chlorinator.model.version}")
    print("Readings:")
    print(f"  - ORP: {chlorinator.readings.orp} mV")

    await conn.close()


asyncio.run(test_live())
