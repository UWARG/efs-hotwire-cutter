from __future__ import annotations

from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from hotwire_protocol.commands import StatusReport


class StatusPanel(QWidget):
    def __init__(self, serial_service, machine_service,
                 parent: QWidget | None = None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        state_box = QGroupBox("Machine")
        state_grid = QGridLayout(state_box)
        self._connection_label = QLabel("Disconnected")
        self._state_label = QLabel("—")
        self._zeroed_label = QLabel("—")
        self._heat_label = QLabel("0 %")
        state_grid.addWidget(QLabel("Connection:"), 0, 0)
        state_grid.addWidget(self._connection_label, 0, 1)
        state_grid.addWidget(QLabel("State:"), 1, 0)
        state_grid.addWidget(self._state_label, 1, 1)
        state_grid.addWidget(QLabel("Zeroed:"), 2, 0)
        state_grid.addWidget(self._zeroed_label, 2, 1)
        state_grid.addWidget(QLabel("Heat:"), 3, 0)
        state_grid.addWidget(self._heat_label, 3, 1)
        layout.addWidget(state_box)

        position_box = QGroupBox("Position (mm)")
        position_grid = QGridLayout(position_box)
        self._axis_labels: dict[str, QLabel] = {}
        for row, axis in enumerate(("XL", "YL", "XR", "YR")):
            label = QLabel("0.000")
            self._axis_labels[axis] = label
            position_grid.addWidget(QLabel(axis), row, 0)
            position_grid.addWidget(label, row, 1)
        layout.addWidget(position_box)

        progress_box = QGroupBox("Job")
        progress_layout = QVBoxLayout(progress_box)
        self._buffer_bar = QProgressBar()
        self._buffer_bar.setFormat("Buffer %v/%m")
        self._progress_bar = QProgressBar()
        self._progress_bar.setFormat("Progress %p%")
        progress_layout.addWidget(QLabel("Firmware buffer"))
        progress_layout.addWidget(self._buffer_bar)
        progress_layout.addWidget(QLabel("Job progress"))
        progress_layout.addWidget(self._progress_bar)
        layout.addWidget(progress_box)

        log_box = QGroupBox("Messages")
        log_layout = QVBoxLayout(log_box)
        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(500)
        log_layout.addWidget(self._log)
        layout.addWidget(log_box, 1)

        serial_service.connected.connect(self._on_connected)
        serial_service.disconnected.connect(self._on_disconnected)
        serial_service.error.connect(lambda msg: self.append_message(f"[serial] {msg}"))
        machine_service.status_updated.connect(self._on_status)
        machine_service.job_progress.connect(self._on_progress)
        machine_service.fault.connect(lambda msg: self.append_message(f"[FAULT] {msg}"))
        machine_service.message.connect(self.append_message)

    def append_message(self, message: str) -> None:
        self._log.appendPlainText(message)

    def _on_connected(self, device: str) -> None:
        self._connection_label.setText(f"Connected ({device})")

    def _on_disconnected(self) -> None:
        self._connection_label.setText("Disconnected")
        self._state_label.setText("—")
        self._zeroed_label.setText("—")

    def _on_status(self, report: StatusReport) -> None:
        self._state_label.setText(report.state.value)
        self._zeroed_label.setText("yes" if report.zeroed else "no")
        for axis, value in (
            ("XL", report.xl_mm),
            ("YL", report.yl_mm),
            ("XR", report.xr_mm),
            ("YR", report.yr_mm),
        ):
            self._axis_labels[axis].setText(f"{value:.3f}")
        total = report.buffer_free + report.buffer_used
        self._buffer_bar.setMaximum(max(total, 1))
        self._buffer_bar.setValue(report.buffer_used)

    def _on_progress(self, sent: int, total: int) -> None:
        self._progress_bar.setMaximum(max(total, 1))
        self._progress_bar.setValue(sent)
