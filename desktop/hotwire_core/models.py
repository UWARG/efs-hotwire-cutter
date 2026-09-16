from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass(frozen=True)
class Point2D:
    x: float
    y: float


@dataclass
class Airfoil:

    name: str
    points: list[Point2D]


class AlignmentMode(Enum):

    LEADING_EDGE = "leading_edge"  # front edge
    QUARTER_CHORD = "quarter_chord" # point 25% back from leading edge
    TRAILING_EDGE = "trailing_edge" # back edge


#im tryna think of the best way to do this i think its better
#to store gaps from left side and right side
@dataclass(frozen=True)
class FoamBlock:
    length_mm: float
    height_mm: float
    width_mm: float


@dataclass(frozen=True)
class WingDefinition:
    root: Airfoil
    tip: Airfoil
    root_chord_mm: float #length of wing at the root
    tip_chord_mm: float #length of the wing at the tip
    span_mm: float #distance between the root and the tip
    sweep_mm: float = 0.0 #angle of the wing
    alignment: AlignmentMode = AlignmentMode.LEADING_EDGE


@dataclass(frozen=True)
class MachineLimits:
    x_min_mm: float
    x_max_mm: float
    y_min_mm: float
    y_max_mm: float
    gantry_spacing_mm: float #distance between gantry planes on machine


@dataclass(frozen=True)
class CutSettings:
    feedrate_mm_min: float
    kerf_mm: float = 0.0
    leadin_mm: float = 0.0
    leadout_mm: float = 0.0
    interpolation_mm: float = 1.0


@dataclass
class JobSettings:
    wing: WingDefinition | None = None
    limits: MachineLimits | None = None
    cut: CutSettings | None = None
    foam: FoamBlock | None = None


@dataclass(frozen=True)
class Segment4:
    """the desktop-side twin of MOVE4/CUT4."""

    xl: float
    yl: float
    xr: float
    yr: float
    feedrate_mm_min: float
    heat_percent: float = 0.0
    cutting: bool = False


@dataclass
class Toolpath:
    moves: list[Segment4]
    warnings: list[str] = field(default_factory=list)

    def bounds(self) -> tuple[Point2D, Point2D]:
        if not self.moves:
            raise ValueError("cant do it")
        xs = [v for m in self.moves for v in (m.xl, m.xr)]
        ys = [v for m in self.moves for v in (m.yl, m.yr)]
        return Point2D(min(xs), min(ys)), Point2D(max(xs), max(ys))
