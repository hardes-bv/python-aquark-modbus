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
    print("")

    print("Status:")
    print(f"  - Power Fault: {chlorinator.status.power_fault}")
    print(f"  - pH Regulation Fault: {chlorinator.status.ph_regulation_fault}")
    print(f"  - ORP Regulation Fault: {chlorinator.status.orp_regulation_fault}")
    ctrl_overtemp = chlorinator.status.controller_over_temperature_protection
    print(f"  - Controller Over Temperature Protection: {ctrl_overtemp}")
    cell_lowtemp = chlorinator.status.electrolytic_cell_low_temperature_protection
    print(f"  - Electrolytic Cell Low Temperature Protection: {cell_lowtemp}")
    print(f"  - WiFi Connection Failure: {chlorinator.status.wifi_connection_failure}")
    print(
        "  - pH Sensor Data Failed to Read:"
        f" {chlorinator.status.ph_sensor_data_failed_to_read}"
    )
    print(
        "  - ORP Sensor Data Failed to Read:"
        f" {chlorinator.status.orp_sensor_data_failed_to_read}"
    )
    print(
        "  - Power Module Data Failed to Read:"
        f" {chlorinator.status.power_module_data_failed_to_read}"
    )
    print(
        "  - External RS485 Communication Failure:"
        f" {chlorinator.status.external_rs485_communication_failure}"
    )
    print(f"  - Calibration Required: {chlorinator.status.calibration_required}")
    print(f"  - Probes Need Replacement: {chlorinator.status.probes_need_replacement}")
    print(f"  - Flow Switch: {chlorinator.status.flow_switch}")
    print(f"  - Need to Add Acid: {chlorinator.status.need_to_add_acid}")
    print(f"  - Need to Add Salt: {chlorinator.status.need_to_add_salt}")

    await conn.close()


asyncio.run(test_live())
