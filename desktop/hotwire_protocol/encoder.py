from __future__ import annotations

from hotwire_protocol import commands as cmd
from hotwire_protocol.commands import Command


class EncodeError(ValueError):
    """Raised for commands the firmware does not support yet."""


_BARE_COMMANDS: dict[type, str] = {
    cmd.Hello: "HELLO",
    cmd.StatusRequest: "STATUS?",
    cmd.SetZero: "SET_ZERO",
    cmd.RunBegin: "RUN_BEGIN",
    cmd.RunEnd: "RUN_END",
    cmd.Stop: "STOP",
}


def _num(value: float) -> str:
    return f"{value:.3f}"


def encode(command: Command) -> str:
    """Encode a command to one protocol line WITHOUT the trailing newline."""
    bare = _BARE_COMMANDS.get(type(command))
    if bare is not None:
        return bare

    if isinstance(command, cmd.Jog):
        return (
            f"JOG AXIS={command.axis.value}"
            f" DIST={_num(command.distance_mm)}"
            f" F={_num(command.feedrate_mm_min)}"
        )

    if isinstance(command, cmd.Move4):
        return (
            f"MOVE4 XL={_num(command.xl_mm)}"
            f" YL={_num(command.yl_mm)}"
            f" XR={_num(command.xr_mm)}"
            f" YR={_num(command.yr_mm)}"
            f" F={_num(command.feedrate_mm_min)}"
        )

    raise EncodeError(f"Command not supported by firmware: {type(command).__name__}")
