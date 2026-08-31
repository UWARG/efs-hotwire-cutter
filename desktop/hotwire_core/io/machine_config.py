"""machine.toml loader."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from hotwire_core.models import MachineLimits


class MachineConfigError(ValueError):
    """machine toml malformed"""


@dataclass(frozen=True)
class AxisConfig:
    steps_per_mm: float


@dataclass(frozen=True)
class MachineConfig:
    name: str
    limits: MachineLimits
    axes: dict[str, AxisConfig]  # keys: "xl", "yl", "xr", "yr"
    max_feedrate_mm_min: float
    max_jog_feedrate_mm_min: float


def load_machine_config(path: Path | str) -> MachineConfig:
    """Load and validate machine toml."""
    path = Path(path)
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise MachineConfigError(f"{path.name}: invalid TOML: {exc}") from exc

    try:
        machine = data["machine"]
        travel = data["travel"]
        limits = MachineLimits(
            x_min_mm=float(travel["x_min_mm"]),
            x_max_mm=float(travel["x_max_mm"]),
            y_min_mm=float(travel["y_min_mm"]),
            y_max_mm=float(travel["y_max_mm"]),
            gantry_spacing_mm=float(machine["gantry_spacing_mm"]),
        )

        axes: dict[str, AxisConfig] = {}
        for axis in ("xl", "yl", "xr", "yr"):
            section = data["axes"][axis]
            axes[axis] = AxisConfig(
                steps_per_mm=float(section["steps_per_mm"]),
            )

        soft = data["limits"]
        return MachineConfig(
            name=str(machine.get("name", path.stem)),
            limits=limits,
            axes=axes,
            max_feedrate_mm_min=float(soft["max_feedrate_mm_min"]),
            max_jog_feedrate_mm_min=float(soft["max_jog_feedrate_mm_min"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise MachineConfigError(f"{path.name}: malformed machine config: {exc}") from exc
