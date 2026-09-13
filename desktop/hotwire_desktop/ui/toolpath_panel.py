from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from hotwire_core.models import CutDirection, CutSettings


class ToolpathPanel(QWidget):
    def __init__(self, job_service, parent: QWidget | None = None):
        super().__init__(parent)
        self._job = job_service

        layout = QVBoxLayout(self)
        box = QGroupBox("Toolpath Settings")
        form = QFormLayout(box)

        self._feedrate = QDoubleSpinBox()
        self._feedrate.setRange(1.0, 3000.0)
        self._feedrate.setValue(250.0)
        self._feedrate.setSuffix(" mm/min")

        self._kerf = QDoubleSpinBox()
        self._kerf.setRange(0.0, 5.0)
        self._kerf.setDecimals(2)
        self._kerf.setSingleStep(0.05)
        self._kerf.setSuffix(" mm")

        self._leadin = QDoubleSpinBox()
        self._leadin.setRange(0.0, 200.0)
        self._leadin.setValue(10.0)
        self._leadin.setSuffix(" mm")

        self._leadout = QDoubleSpinBox()
        self._leadout.setRange(0.0, 200.0)
        self._leadout.setValue(10.0)
        self._leadout.setSuffix(" mm")

        self._direction = QComboBox()
        for direction in CutDirection:
            self._direction.addItem(direction.value.replace("_", " ").title(), direction)

        self._interpolation = QDoubleSpinBox()
        self._interpolation.setRange(0.1, 10.0)
        self._interpolation.setDecimals(2)
        self._interpolation.setValue(1.0)
        self._interpolation.setSuffix(" mm")

        self._tolerance = QDoubleSpinBox()
        self._tolerance.setRange(0.01, 1.0)
        self._tolerance.setDecimals(2)
        self._tolerance.setSingleStep(0.01)
        self._tolerance.setValue(0.05)
        self._tolerance.setSuffix(" mm")

        form.addRow("Feedrate", self._feedrate)
        form.addRow("Kerf", self._kerf)
        form.addRow("Lead-in", self._leadin)
        form.addRow("Lead-out", self._leadout)
        form.addRow("Cut direction", self._direction)
        form.addRow("Interpolation", self._interpolation)
        form.addRow("Segment tolerance", self._tolerance)
        layout.addWidget(box)

        self._generate_button = QPushButton("Generate Toolpath")
        layout.addWidget(self._generate_button)
        layout.addStretch(1)

        for widget in (
            self._feedrate,
            self._kerf,
            self._leadin,
            self._leadout,
            self._interpolation,
            self._tolerance,
        ):
            widget.valueChanged.connect(self._push_settings)
        self._direction.currentIndexChanged.connect(self._push_settings)
        self._generate_button.clicked.connect(self._on_generate)

        self._push_settings()

    def _current_settings(self) -> CutSettings:
        return CutSettings(
            feedrate_mm_min=self._feedrate.value(),
            kerf_mm=self._kerf.value(),
            leadin_mm=self._leadin.value(),
            leadout_mm=self._leadout.value(),
            interpolation_mm=self._interpolation.value(),
            segment_tolerance_mm=self._tolerance.value(),
            direction=self._direction.currentData(),
        )

    def _push_settings(self) -> None:
        self._job.update_cut_settings(self._current_settings())

    def _on_generate(self) -> None:
        self._push_settings()
        self._job.generate()
