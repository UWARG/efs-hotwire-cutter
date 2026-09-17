from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from hotwire_protocol.commands import Axis


class MachinePanel(QWidget):
    def __init__(self, serial_service, machine_service, job_service,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self._serial = serial_service
        self._machine = machine_service
        self._job = job_service

        layout = QVBoxLayout(self)
        layout.addWidget(self._build_connection_box())
        layout.addWidget(self._build_jog_box())
        layout.addWidget(self._build_job_box())
        layout.addStretch(1)

        self._serial.connected.connect(lambda _d: self._set_connected(True))
        self._serial.disconnected.connect(lambda: self._set_connected(False))
        self._set_connected(False)
        self._refresh_ports()

    # connection

    def _build_connection_box(self) -> QGroupBox:
        box = QGroupBox("Connection")
        row = QHBoxLayout(box)
        self._port_combo = QComboBox()
        self._refresh_button = QPushButton("⟳")
        self._refresh_button.setFixedWidth(32)
        self._connect_button = QPushButton("Connect")
        row.addWidget(self._port_combo, 1)
        row.addWidget(self._refresh_button)
        row.addWidget(self._connect_button)

        self._refresh_button.clicked.connect(self._refresh_ports)
        self._connect_button.clicked.connect(self._on_connect_clicked)
        return box

    def _refresh_ports(self) -> None:
        current = self._port_combo.currentData()
        self._port_combo.clear()
        for port in self._serial.available_ports():
            self._port_combo.addItem(f"{port.device} — {port.description}", port.device)
        if current is not None:
            index = self._port_combo.findData(current)
            if index >= 0:
                self._port_combo.setCurrentIndex(index)

    def _on_connect_clicked(self) -> None:
        if self._serial.is_connected:
            self._serial.disconnect_port()
        elif self._port_combo.currentData() is not None:
            self._serial.connect_port(self._port_combo.currentData())

    # jog

    def _build_jog_box(self) -> QGroupBox:
        box = QGroupBox("Jog")
        grid = QGridLayout(box)

        self._jog_step = QComboBox()
        for step in (0.1, 1.0, 10.0, 50.0):
            self._jog_step.addItem(f"{step:g} mm", step)
        self._jog_step.setCurrentIndex(1)

        self._jog_feed = QDoubleSpinBox()
        self._jog_feed.setRange(1.0, 3000.0)
        self._jog_feed.setValue(300.0)
        self._jog_feed.setSuffix(" mm/min")

        self._jog_mode = QComboBox()
        self._jog_mode.addItem("Independent axes", "independent")
        self._jog_mode.addItem("Both gantries", "coordinated")

        grid.addWidget(self._jog_step, 0, 0, 1, 2)
        grid.addWidget(self._jog_feed, 0, 2, 1, 2)
        grid.addWidget(self._jog_mode, 1, 0, 1, 4)

        # Left gantry cross | Right gantry cross
        for column_offset, (x_axis, y_axis, title) in enumerate(
            ((Axis.XL, Axis.YL, "Left"), (Axis.XR, Axis.YR, "Right"))
        ):
            base_col = column_offset * 2
            up = QPushButton(f"{y_axis.value} +")
            down = QPushButton(f"{y_axis.value} −")
            left = QPushButton(f"{x_axis.value} −")
            right = QPushButton(f"{x_axis.value} +")
            grid.addWidget(up, 2, base_col, 1, 2)
            grid.addWidget(left, 3, base_col)
            grid.addWidget(right, 3, base_col + 1)
            grid.addWidget(down, 4, base_col, 1, 2)
            up.clicked.connect(lambda _=False, a=y_axis: self._jog(a, +1))
            down.clicked.connect(lambda _=False, a=y_axis: self._jog(a, -1))
            left.clicked.connect(lambda _=False, a=x_axis: self._jog(a, -1))
            right.clicked.connect(lambda _=False, a=x_axis: self._jog(a, +1))

        self._zero_button = QPushButton("Set Zero")
        grid.addWidget(self._zero_button, 5, 0, 1, 4)
        self._zero_button.clicked.connect(self._machine.set_zero)
        return box

    def _jog(self, axis: Axis, sign: int) -> None:
        distance = self._jog_step.currentData() * sign
        if self._jog_mode.currentData() == "coordinated":
            dx = distance if axis in (Axis.XL, Axis.XR) else 0.0
            dy = distance if axis in (Axis.YL, Axis.YR) else 0.0
            self._machine.jog_coordinated(dx, dy, self._jog_feed.value())
        else:
            self._machine.jog(axis, distance, self._jog_feed.value())

    # job

    def _build_job_box(self) -> QGroupBox:
        box = QGroupBox("Job")
        grid = QGridLayout(box)
        self._start_button = QPushButton("Start")
        self._stop_button = QPushButton("Stop")
        self._estop_button = QPushButton("EMERGENCY STOP")
        self._estop_button.setStyleSheet(
            "QPushButton { background-color: #c62828; color: white; font-weight: bold;"
            " padding: 10px; }"
        )
        grid.addWidget(self._start_button, 0, 0)
        grid.addWidget(self._stop_button, 0, 1)
        grid.addWidget(self._estop_button, 1, 0, 1, 2)

        self._start_button.clicked.connect(lambda: self._machine.run_job(self._job.toolpath))
        self._stop_button.clicked.connect(self._machine.stop_job)
        self._estop_button.clicked.connect(self._machine.emergency_stop)
        return box

    # state

    def _set_connected(self, connected: bool) -> None:
        self._connect_button.setText("Disconnect" if connected else "Connect")
        self._port_combo.setEnabled(not connected)
        self._refresh_button.setEnabled(not connected)
        for button in (
            self._start_button,
            self._stop_button,
            self._estop_button,
            self._zero_button,
        ):
            button.setEnabled(connected)
