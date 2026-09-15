from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget, QLabel, QMainWindow, QPushButton, QTabWidget, QToolBar

from hotwire_desktop.services.job_service import JobService
from hotwire_desktop.services.machine_service import MachineService
from hotwire_desktop.services.preview_service import PreviewService
from hotwire_desktop.services.serial_service import SerialService
from hotwire_desktop.ui.geometry_panel import GeometryPanel
from hotwire_desktop.ui.machine_panel import MachinePanel
from hotwire_desktop.ui.preview_canvas import PreviewCanvas
from hotwire_desktop.ui.project_panel import ProjectPanel
from hotwire_desktop.ui.status_panel import StatusPanel
from hotwire_desktop.ui.toolpath_panel import ToolpathPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EFS Hotwire Cutter")
        self.resize(1400, 900)

        # Services
        self.job_service = JobService(self)
        self.serial_service = SerialService(self)
        self.machine_service = MachineService(self.serial_service, self)
        self.preview_service = PreviewService(self.job_service, self)

        # Central preview
        self.preview_canvas = PreviewCanvas(self)
        self.setCentralWidget(self.preview_canvas)
        self.preview_service.preview_ready.connect(self.preview_canvas.show_preview)
        self.preview_service.preview_fit_requested.connect(self.preview_canvas.fit_geometry)
        self.job_service.project_changed.connect(self._sync_preview_machine_limits)
        self.preview_canvas.set_machine_limits(self.job_service.job.limits)

        preview_toolbar = QToolBar("Preview", self)
        preview_toolbar.setMovable(False)
        for label, handler in (
            ("Fit Geometry", self.preview_canvas.fit_geometry),
            ("Fit Machine", self.preview_canvas.fit_machine),
            ("Reset View", self.preview_canvas.reset_view),
        ):
            button = QPushButton(label, preview_toolbar)
            button.clicked.connect(handler)
            preview_toolbar.addWidget(button)
        preview_toolbar.addSeparator()
        legend = QLabel(
            '<span style="color:#29b6f6">● Root</span>&nbsp;&nbsp;'
            '<span style="color:#66bb6a">● Tip</span>',
            preview_toolbar,
        )
        preview_toolbar.addWidget(legend)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, preview_toolbar)

        # Left dock: setup panels as tabs
        setup_tabs = QTabWidget()
        setup_tabs.addTab(ProjectPanel(self.job_service), "Project")
        setup_tabs.addTab(GeometryPanel(self.job_service), "Geometry")
        setup_tabs.addTab(ToolpathPanel(self.job_service), "Toolpath")
        setup_dock = QDockWidget("Setup", self)
        setup_dock.setWidget(setup_tabs)
        setup_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, setup_dock)

        # Right dock: machine control
        machine_dock = QDockWidget("Machine", self)
        machine_dock.setWidget(
            MachinePanel(self.serial_service, self.machine_service, self.job_service)
        )
        machine_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, machine_dock)

        # Bottom dock: status
        self.status_panel = StatusPanel(self.serial_service, self.machine_service)
        status_dock = QDockWidget("Status", self)
        status_dock.setWidget(self.status_panel)
        status_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, status_dock)

        # Error surfacing
        self.job_service.error.connect(self._show_error)
        self.serial_service.error.connect(self._show_error)
        self.machine_service.message.connect(
            lambda msg: self.statusBar().showMessage(msg, 5000)
        )
        self.statusBar().showMessage("Ready")

    def _show_error(self, message: str) -> None:
        self.statusBar().showMessage(message, 8000)
        self.status_panel.append_message(message)

    def _sync_preview_machine_limits(self) -> None:
        self.preview_canvas.set_machine_limits(self.job_service.job.limits)
