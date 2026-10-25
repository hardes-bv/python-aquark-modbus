# aquark-modbus

A typed, async Python model of an Aquark chlorinator unit's Modbus registers. 
Backend-neutral: built on [`modbus-connection`](https://home-assistant-libs.github.io/modbus-connection/),
so it runs over `pymodbus`, `tmodbus`, or an in-memory mock. 

No [Home Assistant](https://www.home-assistant.io/) dependency. A Home Assistant integration 
that consumes this library lives in a separate repository.
