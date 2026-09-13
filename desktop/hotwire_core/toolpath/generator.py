from __future__ import annotations

from hotwire_core.geometry.airfoil import (
    normalize_airfoil,
    resample_airfoil,
    scale_and_place,
)
from hotwire_core.models import JobSettings, Segment4, Toolpath


class ToolpathError(ValueError):
    """no path"""


# TODO: direction, interpolation, leads, kerf, alignment, projection, limits,
# foam placement
def generate_toolpath(job: JobSettings) -> Toolpath:
    if job.wing is None or job.cut is None:
        raise ToolpathError("fill in the settings brah")

    wing = job.wing
    cut = job.cut
    root = normalize_airfoil(wing.root)
    tip = normalize_airfoil(wing.tip)
    point_count = min(len(root.points), len(tip.points))
    root = scale_and_place(resample_airfoil(root, point_count), wing.root_chord_mm, 0.0)
    tip = scale_and_place(
        resample_airfoil(tip, point_count), wing.tip_chord_mm, wing.sweep_mm
    )

    #generate the actual moves
    moves = [
        Segment4(
            xl=root_point.x,
            yl=root_point.y,
            xr=tip_point.x,
            yr=tip_point.y,
            feedrate_mm_min=cut.feedrate_mm_min,
            cutting=True,
        )
        for root_point, tip_point in zip(root.points, tip.points)
    ]
    return Toolpath(moves=moves)
