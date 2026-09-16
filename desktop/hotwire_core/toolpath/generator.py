from __future__ import annotations

import math

from hotwire_core.geometry.airfoil import (
    normalize_airfoil,
    offset_airfoil,
    resample_airfoil,
    scale_and_place,
)
from hotwire_core.models import Airfoil, JobSettings, Segment4, Toolpath


class ToolpathError(ValueError):
    """no path"""


def arc_length(airfoil: Airfoil) -> float:
    return sum(
        math.hypot(end.x - start.x, end.y - start.y)
        for start, end in zip(airfoil.points, airfoil.points[1:])
    )


# TODO: alignment, projection, limits, foam placement
def generate_toolpath(job: JobSettings) -> Toolpath:
    if job.wing is None or job.cut is None:
        raise ToolpathError("fill in the settings brah")

    wing = job.wing
    cut = job.cut
    root = normalize_airfoil(wing.root)
    tip = normalize_airfoil(wing.tip)
    # add samples until the meets the req spacing.
    point_count = max(
        min(len(root.points), len(tip.points)),
        math.ceil(
            max(
                arc_length(root) * wing.root_chord_mm,
                arc_length(tip) * wing.tip_chord_mm,
            )
            / cut.interpolation_mm
        )
        + 1,
    )
    root = scale_and_place(resample_airfoil(root, point_count), wing.root_chord_mm, 0.0)
    tip = scale_and_place(
        resample_airfoil(tip, point_count), wing.tip_chord_mm, wing.sweep_mm
    )
    try:
        root = offset_airfoil(root, cut.kerf_mm)
        tip = offset_airfoil(tip, cut.kerf_mm)
    except ValueError as exc:
        raise ToolpathError(f"cannot apply kerf offset: {exc}") from exc

    first_root, first_tip = root.points[0], tip.points[0]
    last_root, last_tip = root.points[-1], tip.points[-1]
    lead_in = []
    if cut.leadin_mm:
        lead_in.append(
            Segment4(
                xl=first_root.x + cut.leadin_mm,
                yl=first_root.y,
                xr=first_tip.x + cut.leadin_mm,
                yr=first_tip.y,
                feedrate_mm_min=cut.feedrate_mm_min,
            )
        )

    profile = [
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
    lead_out = []
    if cut.leadout_mm:
        lead_out.append(
            Segment4(
                xl=last_root.x + cut.leadout_mm,
                yl=last_root.y,
                xr=last_tip.x + cut.leadout_mm,
                yr=last_tip.y,
                feedrate_mm_min=cut.feedrate_mm_min,
            )
        )

    moves = lead_in + profile + lead_out
    return Toolpath(moves=moves)
