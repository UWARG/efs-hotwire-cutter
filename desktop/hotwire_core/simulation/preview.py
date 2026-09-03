

from __future__ import annotations

from dataclasses import dataclass, field

from hotwire_core.models import JobSettings, Point2D, Toolpath


@dataclass(frozen=True)
class PreviewPolyline:
    """drawable polyline with semantic meaning embedded in colour or design
    ex red for an error or warning
    ."""

    role: str
    # root_profile, tip_profile, cut_path_root, cut_path_tip, foam_outline, lead, warning
    points: list[Point2D]


@dataclass
class PreviewData:
    polylines: list[PreviewPolyline] = field(default_factory=list)
    wire_start_root: Point2D | None = None
    wire_start_tip: Point2D | None = None
    warnings: list[str] = field(default_factory=list)


def build_preview(job: JobSettings, toolpath: Toolpath | None) -> PreviewData:
    """Build drawable preview state.
    this can work with profile alone and no toolpth and just produce profile polylines
    toolpath warnings should get copied through and probably highlight those lines
    """


    raise NotImplementedError
