from __future__ import annotations

import math
from bisect import bisect_right

from hotwire_core.models import Airfoil, Point2D


def polyline_length(points: list[Point2D]) -> float:
    return sum(
        math.hypot(b.x - a.x, b.y - a.y) for a, b in zip(points, points[1:])
    )


def normalize_airfoil(airfoil: Airfoil) -> Airfoil:
    _validate_points(airfoil)
    min_x = min(point.x for point in airfoil.points)
    chord = max(point.x for point in airfoil.points) - min_x

    return Airfoil(
        name=airfoil.name,
        points=[
            Point2D((point.x - min_x) / chord, point.y / chord)
            for point in airfoil.points
        ],
    )

# btw this is crude and just linearly interpolates, ima return to this later and think harder
def resample_airfoil(airfoil: Airfoil, point_count: int) -> Airfoil:
    _validate_points(airfoil)
    if point_count < 2:
        raise ValueError("not enough points")

    segments: list[tuple[Point2D, Point2D, float]] = []
    cumulative = [0.0]
    #generate a prefix sum of distances around the polyline
    for start, end in zip(airfoil.points, airfoil.points[1:]):
        length = math.hypot(end.x - start.x, end.y - start.y)
        if length > 0.0:
            segments.append((start, end, length))
            cumulative.append(cumulative[-1] + length)

    total_length = cumulative[-1]

    #split up evenly and then find where that point is along the old polyline by
    #linearly interpolating
    #first and last point are preserved
    points: list[Point2D] = []
    for index in range(point_count):
        distance = total_length * index / (point_count - 1)
        segment_index = min(bisect_right(cumulative, distance) - 1, len(segments) - 1)
        start, end, length = segments[segment_index]
        fraction = (distance - cumulative[segment_index]) / length
        points.append(
            Point2D(
                start.x + fraction * (end.x - start.x),
                start.y + fraction * (end.y - start.y),
            )
        )
    return Airfoil(name=airfoil.name, points=points)


def find_leading_edge_index(airfoil: Airfoil) -> int:
    _validate_points(airfoil)
    return min(range(len(airfoil.points)), key=lambda index: airfoil.points[index].x)

#turns abstract airfoil to the actual size
def scale_and_place(
    airfoil: Airfoil,
    chord_mm: float,
    sweep_offset_mm: float,
) -> Airfoil:
    _validate_points(airfoil)
    if not math.isfinite(chord_mm) or chord_mm <= 0.0:
        raise ValueError("chord_mm must be positive and finite")
    if not math.isfinite(sweep_offset_mm):
        raise ValueError("sweep_offset_mm must be finite")

    return Airfoil(
        name=airfoil.name,
        points=[
            Point2D(
                point.x * chord_mm + sweep_offset_mm,
                point.y * chord_mm,
            )
            for point in airfoil.points
        ],
    )


def offset_airfoil(airfoil: Airfoil, kerf_mm: float) -> Airfoil:
    # Offset a profile by half the total wire width using local normals

    _validate_points(airfoil)
    if not math.isfinite(kerf_mm) or kerf_mm < 0.0:
        raise ValueError("check kerf value")
    if kerf_mm == 0.0:
        return Airfoil(name=airfoil.name, points=list(airfoil.points))

    signed_area = _signed_area(airfoil.points)
    if signed_area == 0.0:
        raise ValueError("can determine point ordering")

    # CCW profiles have their interior on the left, 
    # thus outward normal is right hand normal
    #you can flip for the CW profiles
    outward_sign = 1.0 if signed_area > 0.0 else -1.0
    distance = kerf_mm / 2.0
    offset_points: list[Point2D] = []
    last_index = len(airfoil.points) - 1
    for index, point in enumerate(airfoil.points):
        if index == 0:
            previous, following = point, airfoil.points[1]
        elif index == last_index:
            previous, following = airfoil.points[-2], point
        else:
            previous, following = airfoil.points[index - 1], airfoil.points[index + 1]

        tangent_x = following.x - previous.x
        tangent_y = following.y - previous.y
        tangent_length = math.hypot(tangent_x, tangent_y)
        

        normal_x = outward_sign * tangent_y / tangent_length
        normal_y = -outward_sign * tangent_x / tangent_length
        offset_points.append(
            Point2D(
                point.x + distance * normal_x,
                point.y + distance * normal_y,
            )
        )

    return Airfoil(name=airfoil.name, points=offset_points)


#shoelace theoreom (ball knowledge)
def _signed_area(points: list[Point2D]) -> float:
    return 0.5 * sum(
        point.x * following.y - following.x * point.y
        for point, following in zip(points, points[1:] + points[:1])
    )


def _validate_points(airfoil: Airfoil) -> None:
    if len(airfoil.points) < 2:
        raise ValueError(">= two points")
    
