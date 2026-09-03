from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union


class Axis(Enum):
    XL = "XL"
    YL = "YL"
    XR = "XR"
    YR = "YR"


class MachineState(Enum):
    NEED_ZERO = "NEED_ZERO"
    IDLE = "IDLE"
    RUNNING = "RUNNING"


# --- Commands (host -> firmware) -------------------------------------------


@dataclass(frozen=True)
class Hello:
    pass


@dataclass(frozen=True)
class StatusRequest:
    pass


@dataclass(frozen=True)
class SetZero:
    pass


@dataclass(frozen=True)
class Jog:
    axis: Axis
    distance_mm: float
    feedrate_mm_min: float


@dataclass(frozen=True)
class Move4:
    xl_mm: float
    yl_mm: float
    xr_mm: float
    yr_mm: float
    feedrate_mm_min: float


@dataclass(frozen=True)
class RunBegin:
    pass


@dataclass(frozen=True)
class RunEnd:
    pass


@dataclass(frozen=True)
class Stop:
    pass


Command = Union[Hello, StatusRequest, SetZero, Jog, Move4, RunBegin, RunEnd, Stop]

# Not in the firmware yet: PAUSE, RESUME, CUT4, HEAT, CLEAR_FAULT.


# --- Responses (firmware -> host) -------------------------------------------


@dataclass(frozen=True)
class Ack:
    pass


@dataclass(frozen=True)
class Ok:
    command_name: str


@dataclass(frozen=True)
class StatusReport:
    state: MachineState
    zeroed: bool
    xl_mm: float
    yl_mm: float
    xr_mm: float
    yr_mm: float
    buffer_free: int
    buffer_used: int


@dataclass(frozen=True)
class Invalid:
    pass


@dataclass(frozen=True)
class UnknownLine:
    raw: str


Response = Union[Ack, Ok, StatusReport, Invalid, UnknownLine]
