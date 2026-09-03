

from __future__ import annotations

from hotwire_core.models import JobSettings, Toolpath


class ToolpathError(ValueError):
    """no valid path"""


def generate_toolpath(job: JobSettings) -> Toolpath:
    """Generate the cut path for a job"""
    raise NotImplementedError
