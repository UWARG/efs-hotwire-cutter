from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from hotwire_core.simulation.preview import PreviewData, build_preview


class PreviewService(QObject):
    preview_ready = Signal(object)  # PreviewData for the canvas to render
    preview_fit_requested = Signal()

    def __init__(self, job_service, parent: QObject | None = None):
        super().__init__(parent)
        self._job = job_service
        self._job.project_changed.connect(self.refresh)
        self._job.airfoil_loaded.connect(lambda *_args: self.refresh(refit=True))
        self._job.toolpath_generated.connect(lambda _tp: self.refresh(refit=True))

    def refresh(self, refit: bool = False) -> None:
        try:
            data = build_preview(self._job.job, self._job.toolpath)
        except NotImplementedError:
            data = PreviewData()
        self.preview_ready.emit(data)
        if refit:
            self.preview_fit_requested.emit()
