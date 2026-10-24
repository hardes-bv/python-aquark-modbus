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

    print("Readings:")
    print(f"  - ORP: {chlorinator.readings.orp} mV")
    print(f"  - pH: {chlorinator.readings.ph}")
    ec = chlorinator.readings.electrical_conductivity
    print(f"  - Electrical Conductivity: {ec} ppm")
    temp = chlorinator.readings.pool_temperature
    print(f"  - Pool Temperature: {temp} °C")
    ctrl_temp = chlorinator.readings.controller_temperature
    print(f"  - Controller Temperature: {ctrl_temp} °C")
    chlorine_prod = chlorinator.readings.chlorine_production
    print(f"  - Chlorine Production: {chlorine_prod} %")
    water_quality = chlorinator.readings.water_quality
    print(f"  - Water Quality: {water_quality}")
    plate_specs = chlorinator.readings.electrolytic_plate_specifications
    print(f"  - Electrolytic Plate Specifications: {plate_specs} g")
    sj = chlorinator.readings.sj
    print(f"  - SJ: {sj} mV")
    si = chlorinator.readings.si
    print(f"  - SI: {si}")
    sv = chlorinator.readings.sv
    print(f"  - SV: {sv}")
    current = chlorinator.readings.electrolytic_current
    print(f"  - Electrolytic Current: {current} A")
    voltage = chlorinator.readings.electrolytic_voltage
    print(f"  - Electrolytic Voltage: {voltage} V")

    await conn.close()


asyncio.run(test_live())
