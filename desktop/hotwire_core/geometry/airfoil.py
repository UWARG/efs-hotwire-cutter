"""
Airfoil and polyline geometry utilities.
"""

from __future__ import annotations

import math

from hotwire_core.models import Airfoil, Point2D


def polyline_length(points: list[Point2D]) -> float:
    return sum(
        math.hypot(b.x - a.x, b.y - a.y) for a, b in zip(points, points[1:])
    )


def normalize_airfoil(airfoil: Airfoil) -> Airfoil:
    """Return a copy normalized to unit chord.
    Leading edge at (0, 0), trailing edge at (1, 0). points ordered
    (TE -> upper -> LE -> lower -> TE).
    """
    raise NotImplementedError


def resample_airfoil(airfoil: Airfoil, point_count: int) -> Airfoil:
    """Arc-length resample to point_count points
    keep endpoints for root and tip pairing"""
    raise NotImplementedError


def find_leading_edge_index(airfoil: Airfoil) -> int:
    """Index of the nose which is the point with minimum x"""
    raise NotImplementedError


def scale_and_place(
    airfoil: Airfoil,
    chord_mm: float,
    sweep_offset_mm: float,
) -> Airfoil:
    """Scale a normalized profile to a chord in mm and shift it along x axis"""
    raise NotImplementedError
