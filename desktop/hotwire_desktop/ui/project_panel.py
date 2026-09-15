from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ProjectPanel(QWidget):
    def __init__(self, job_service, parent: QWidget | None = None):
        super().__init__(parent)
        self._job = job_service

        layout = QVBoxLayout(self)

        actions = QHBoxLayout()
        self._new_button = QPushButton("Clear")
        actions.addWidget(self._new_button)
        actions.addStretch(1)
        layout.addLayout(actions)

        airfoil_box = QGroupBox("Airfoils")
        airfoil_grid = QGridLayout(airfoil_box)
        self._import_root_button = QPushButton("Import Root .dat…")
        self._import_tip_button = QPushButton("Import Tip .dat…")
        self._root_label = QLabel("Root: —")
        self._tip_label = QLabel("Tip: —")
        airfoil_grid.addWidget(self._import_root_button, 0, 0)
        airfoil_grid.addWidget(self._root_label, 0, 1)
        airfoil_grid.addWidget(self._import_tip_button, 1, 0)
        airfoil_grid.addWidget(self._tip_label, 1, 1)
        airfoil_grid.setColumnStretch(1, 1)
        layout.addWidget(airfoil_box)
        layout.addStretch(1)

        self._new_button.clicked.connect(self._job.new_project)
        self._import_root_button.clicked.connect(lambda: self._on_import("root"))
        self._import_tip_button.clicked.connect(lambda: self._on_import("tip"))
        self._job.project_changed.connect(self._refresh)
        self._job.airfoil_loaded.connect(self._on_airfoil_loaded)

        self._refresh()

    def _on_import(self, slot: str) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, f"Import {slot} airfoil", "", "Airfoil data (*.dat);;All files (*)"
        )
        if path:
            self._job.import_airfoil(slot, Path(path))

    def _on_airfoil_loaded(self, slot: str, airfoil) -> None:
        label = self._root_label if slot == "root" else self._tip_label
        label.setText(f"{slot.capitalize()}: {airfoil.name} ({len(airfoil.points)} pts)")

    def _refresh(self) -> None:
        if self._job.root_airfoil is None:
            self._root_label.setText("Root: —")
        else:
            airfoil = self._job.root_airfoil
            self._root_label.setText(f"Root: {airfoil.name} ({len(airfoil.points)} pts)")
        if self._job.tip_airfoil is None:
            self._tip_label.setText("Tip: —")
        else:
            airfoil = self._job.tip_airfoil
            self._tip_label.setText(f"Tip: {airfoil.name} ({len(airfoil.points)} pts)")
