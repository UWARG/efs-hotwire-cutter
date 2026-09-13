from __future__ import annotations

import math

from hotwire_core.models import Airfoil, Point2D


def polyline_length(points: list[Point2D]) -> float:
    return sum(
        math.hypot(b.x - a.x, b.y - a.y) for a, b in zip(points, points[1:])
    )


def normalize_airfoil(airfoil: Airfoil) -> Airfoil:
    raise NotImplementedError


def resample_airfoil(airfoil: Airfoil, point_count: int) -> Airfoil:
    raise NotImplementedError


def find_leading_edge_index(airfoil: Airfoil) -> int:
    raise NotImplementedError


def scale_and_place(
    airfoil: Airfoil,
    chord_mm: float,
    sweep_offset_mm: float,
) -> Airfoil:
    raise NotImplementedError
