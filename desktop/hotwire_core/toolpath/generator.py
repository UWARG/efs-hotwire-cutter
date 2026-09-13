

from __future__ import annotations

from hotwire_core.models import JobSettings, Toolpath


class ToolpathError(ValueError):
    """no valid path"""


def generate_toolpath(job: JobSettings) -> Toolpath:
    raise NotImplementedError
