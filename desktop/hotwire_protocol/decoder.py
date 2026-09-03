from __future__ import annotations

from hotwire_protocol.commands import (
    Ack,
    Invalid,
    MachineState,
    Ok,
    Response,
    StatusReport,
    UnknownLine,
)


def _parse_status(body: str) -> Response:
    fields: dict[str, str] = {}
    for token in body.split():
        key, sep, value = token.partition("=")
        if not sep or not value:
            return UnknownLine(raw=f"STATUS {body}")
        fields[key] = value

    try:
        return StatusReport(
            state=MachineState(fields["STATE"]),
            zeroed=fields["ZEROED"] == "1",
            xl_mm=float(fields["XL"]),
            yl_mm=float(fields["YL"]),
            xr_mm=float(fields["XR"]),
            yr_mm=float(fields["YR"]),
            buffer_free=int(fields["BUFFER_FREE"]),
            buffer_used=int(fields["BUFFER_USED"]),
        )
    except (KeyError, ValueError):
        return UnknownLine(raw=f"STATUS {body}")


def decode_line(line: str) -> Response:
    """Decode one stripped response line from the firmware."""
    line = line.strip()

    if line == "ACK":
        return Ack()

    if line == "INVALID":
        return Invalid()

    if line.startswith("OK CMD="):
        name = line[len("OK CMD="):].split()[0] if line[len("OK CMD="):] else ""
        if name:
            return Ok(command_name=name)
        return UnknownLine(raw=line)

    if line.startswith("STATUS "):
        return _parse_status(line[len("STATUS "):])

    return UnknownLine(raw=line)
