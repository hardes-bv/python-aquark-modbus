# AGENTS.md

Guidance for AI coding agents (and humans) working in this repository. This file
follows the [agents.md](https://agents.md) convention. `CLAUDE.md` is a symlink
to this file, so Claude-compatible tooling reads the same guidance.

## What this project is

python-aquark-modbus is an asynchronous Python client for Aquark inverter
pumps, heat pumps and water treatment devices over
Modbus. It decodes the SunSpec information model and Aquark's proprietary
register blocks (inverter, heat pump, water treatment) into
typed values, and can write the control registers. It is pure Python built on
[`modbus-connection`][modbus-connection], which owns the transport and the field
decoding; this library declares the register layout and detects the device.

The consumer owns the connection: it hands the library a `ModbusUnit`
(`connection.for_unit(id)`), and one `Aquark` instance maps to one unit.

## Project layout

| Path                 | Purpose                                            |
|----------------------|----------------------------------------------------|
| `src/aquark_modbus/` | The package                                        |
| `  aquark.py`        | The `Aquark` client: probe, update, detection      |
| `  const.py`         | Addresses and enums                                |
| `  exceptions.py`    | `AquarkError` and `AquarkConnectionError`          |
| `  model.py`         | Register field declarations per block, and writes  |
| `  readings.py`      | Telemetry readings component                       |
| `  settings.py`      | Settings and configuration component               |
| `  status.py`        | Status and fault flags component                   |
| `tests/`             | pytest suite; each test has a one-line docstring   |
| `examples/`          | Runnable examples, exercised by `test_examples.py` |

## Commands

This is a [uv][uv] project.

During iteration, running a single tool directly is fine and faster:
`poetry run pytest -k ...`, `poetry run ruff check .`, `poetry run ty check src`.
The fuzz tests run more examples under `HYPOTHESIS_PROFILE=ci`.

## Conventions

- The library never leaks a raw exception: reads and writes surface as
  `AquarkConnectionError` (transport) or `AquarkError` (bad value or
  undecodable data). Keep that contract when adding code.
- A point the device does not implement decodes to `None`. Do not turn a genuine
  reading into `None`, and do not let a read failure masquerade as one.
- Coverage is enforced at 100% on the package. New code needs tests.
- Every test carries a one-line docstring describing what it verifies.
- Comments explain the why, not the what. Clarity over cleverness, clear names,
  and blank lines between logical steps.

## Writing and voice

English for all public artifacts (commits, PRs, issues). Held to a high bar:
clear, honest, no filler. Avoid:

- AI cheerleading and marketing speak (leverage, synergize, delight).
- Em-dashes and en-dashes anywhere. Use a period, colon, comma, or parentheses;
  hyphen only for compound words. Restructure a sentence rather than reach for one.
- "e.g.", "i.e.", "etc."; write "like", "for example", "such as".
- CAPS for emphasis (use italics); "click" as a verb (use "select").
- "HA"/"HASS"; write "Home Assistant" in full, and never frame it as fragile.
- "master/slave"; use "client/server", "leader/follower", "main/replica".

See [AI_POLICY.md](AI_POLICY.md) for the contribution policy around AI tooling.

## Gotchas

- Word order differs by block. The SunSpec inverter and meter blocks are
  big-endian. Sentinels are per type (`0x8000` int16,
  `0xFFFF` uint16, `0xFFFFFFFF` uint32, IEEE-754 NaN, +/-FLT_MAX "no limit").
- Writable control fields carry validators, and a successful write caches the
  value the device would report back (`decode(encode(value))`), not the raw input.
- `test_sunspec_conformance.py` checks the register map against the vendored
  SunSpec model definitions. If you move an address or scale reference, it will
  tell you whether it still matches the spec.

## Where to read next

- `README.md`: install, usage, and the development setup.
- `tests/test_sunspec_conformance.py` and `tests/test_community_dumps.py`: how
  the register map is validated against the spec and against real devices.

[modbus-connection]: https://github.com/home-assistant-libs/modbus-connection
[uv]: https://docs.astral.sh/uv/
