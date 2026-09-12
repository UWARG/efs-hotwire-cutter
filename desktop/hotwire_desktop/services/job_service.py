from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from hotwire_core.io.dat_reader import DatFormatError, load_dat
from hotwire_core.models import (
    Airfoil,
    CutSettings,
    FoamBlock,
    JobSettings,
    MachineLimits,
    Toolpath,
    WingDefinition,
)
from hotwire_core.toolpath.generator import ToolpathError, generate_toolpath


class JobService(QObject):
    project_changed = Signal()  # any settings mutation; panels re-read
    airfoil_loaded = Signal(str, object)  # slot ("root"/"tip"), Airfoil
    toolpath_generated = Signal(object)  # Toolpath
    error = Signal(str)

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.job = JobSettings()
        self.root_airfoil: Airfoil | None = None
        self.tip_airfoil: Airfoil | None = None
        self.toolpath: Toolpath | None = None
        # Settings staged by panels before a WingDefinition can be assembled.
        self.root_chord_mm: float = 200.0
        self.tip_chord_mm: float = 150.0
        self.span_mm: float = 400.0
        self.sweep_mm: float = 0.0

    def new_project(self) -> None:
        self.job = JobSettings()
        self.root_airfoil = None
        self.tip_airfoil = None
        self.toolpath = None
        self.project_changed.emit()

    def import_airfoil(self, slot: str, path: Path) -> None:
        """Load a .dat file into the "root" or "tip" slot."""
        try:
            airfoil = load_dat(path)
        except NotImplementedError:
            self.error.emit(".dat import not implemented yet")
            return
        except (OSError, DatFormatError) as exc:
            self.error.emit(f"Could not load airfoil: {exc}")
            return
        if slot == "root":
            self.root_airfoil = airfoil
        else:
            self.tip_airfoil = airfoil
        self.airfoil_loaded.emit(slot, airfoil)
        self.project_changed.emit()

    def update_wing_settings(self, **kwargs: float) -> None:
        """Stage wing numbers (root_chord_mm, tip_chord_mm, span_mm, sweep_mm)."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.project_changed.emit()

    def update_cut_settings(self, cut: CutSettings) -> None:
        self.job.cut = cut
        self.project_changed.emit()

    def update_foam_block(self, foam: FoamBlock) -> None:
        self.job.foam = foam
        self.project_changed.emit()

    def update_machine_limits(self, limits: MachineLimits) -> None:
        self.job.limits = limits
        self.project_changed.emit()

    def generate(self) -> None:
        if self.root_airfoil is None or self.tip_airfoil is None:
            self.error.emit("need root and tip airfoils")
            return
        self.job.wing = WingDefinition(
            root=self.root_airfoil,
            tip=self.tip_airfoil,
            root_chord_mm=self.root_chord_mm,
            tip_chord_mm=self.tip_chord_mm,
            span_mm=self.span_mm,
            sweep_mm=self.sweep_mm,
        )
        try:
            self.toolpath = generate_toolpath(self.job)
        except NotImplementedError:
            self.error.emit("Toolpath gen not implemented")
            return
        except ToolpathError as exc:
            self.error.emit(f"Toolpath gen failed: {exc}")
            return
        self.toolpath_generated.emit(self.toolpath)
