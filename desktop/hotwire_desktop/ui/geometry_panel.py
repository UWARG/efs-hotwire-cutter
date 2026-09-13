from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QVBoxLayout,
    QWidget,
)

from hotwire_core.models import AlignmentMode, FoamBlock, MachineLimits


def _mm_spin(value: float, maximum: float = 5000.0, minimum: float = 0.0) -> QDoubleSpinBox:
    spin = QDoubleSpinBox()
    spin.setRange(minimum, maximum)
    spin.setDecimals(1)
    spin.setSuffix(" mm")
    spin.setValue(value)
    return spin


class GeometryPanel(QWidget):
    def __init__(self, job_service, parent: QWidget | None = None):
        super().__init__(parent)
        self._job = job_service

        layout = QVBoxLayout(self)

        wing_box = QGroupBox("Wing")
        wing_form = QFormLayout(wing_box)
        self._root_chord = _mm_spin(self._job.root_chord_mm)
        self._tip_chord = _mm_spin(self._job.tip_chord_mm)
        self._span = _mm_spin(self._job.span_mm)
        self._sweep = _mm_spin(self._job.sweep_mm, minimum=-1000.0, maximum=1000.0)
        self._alignment = QComboBox()
        for mode in AlignmentMode:
            self._alignment.addItem(mode.value.replace("_", " ").title(), mode)
        wing_form.addRow("Root chord", self._root_chord)
        wing_form.addRow("Tip chord", self._tip_chord)
        wing_form.addRow("Span", self._span)
        wing_form.addRow("Sweep", self._sweep)
        wing_form.addRow("Alignment", self._alignment)
        layout.addWidget(wing_box)

        foam_box = QGroupBox("Foam Block")
        foam_form = QFormLayout(foam_box)
        self._foam_length = _mm_spin(600.0)
        self._foam_height = _mm_spin(100.0)
        self._foam_width = _mm_spin(450.0)
        foam_form.addRow("Length (x)", self._foam_length)
        foam_form.addRow("Height (y)", self._foam_height)
        foam_form.addRow("Width (span)", self._foam_width)
        layout.addWidget(foam_box)

        machine_box = QGroupBox("Machine")
        machine_form = QFormLayout(machine_box)
        self._x_travel = _mm_spin(700.0)
        self._y_travel = _mm_spin(300.0)
        self._gantry_spacing = _mm_spin(800.0)
        machine_form.addRow("X travel", self._x_travel)
        machine_form.addRow("Y travel", self._y_travel)
        machine_form.addRow("Gantry spacing", self._gantry_spacing)
        layout.addWidget(machine_box)
        layout.addStretch(1)

        for spin in (self._root_chord, self._tip_chord, self._span, self._sweep):
            spin.valueChanged.connect(self._push_wing)
        for spin in (self._foam_length, self._foam_height, self._foam_width):
            spin.valueChanged.connect(self._push_foam)
        for spin in (self._x_travel, self._y_travel, self._gantry_spacing):
            spin.valueChanged.connect(self._push_limits)

    def _push_wing(self) -> None:
        self._job.update_wing_settings(
            root_chord_mm=self._root_chord.value(),
            tip_chord_mm=self._tip_chord.value(),
            span_mm=self._span.value(),
            sweep_mm=self._sweep.value(),
        )

    def _push_foam(self) -> None:
        self._job.update_foam_block(
            FoamBlock(
                length_mm=self._foam_length.value(),
                height_mm=self._foam_height.value(),
                width_mm=self._foam_width.value(),
            )
        )

    def _push_limits(self) -> None:
        self._job.update_machine_limits(
            MachineLimits(
                x_min_mm=0.0,
                x_max_mm=self._x_travel.value(),
                y_min_mm=0.0,
                y_max_mm=self._y_travel.value(),
                gantry_spacing_mm=self._gantry_spacing.value(),
            )
        )
