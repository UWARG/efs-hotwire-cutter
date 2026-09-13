from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QWidget

from hotwire_core.simulation.preview import PreviewData

_ROLE_PENS: dict[str, tuple[QColor, float, Qt.PenStyle]] = {
    "root_profile": (QColor("#4fc3f7"), 0.0, Qt.PenStyle.SolidLine),
    "tip_profile": (QColor("#81c784"), 0.0, Qt.PenStyle.SolidLine),
    "cut_path_root": (QColor("#29b6f6"), 0.0, Qt.PenStyle.SolidLine),
    "cut_path_tip": (QColor("#66bb6a"), 0.0, Qt.PenStyle.SolidLine),
    "foam_outline": (QColor("#9e9e9e"), 0.0, Qt.PenStyle.DashLine),
    "lead": (QColor("#ffb74d"), 0.0, Qt.PenStyle.DotLine),
    "warning": (QColor("#ef5350"), 0.0, Qt.PenStyle.SolidLine),
}
_DEFAULT_PEN = (QColor("#e0e0e0"), 0.0, Qt.PenStyle.SolidLine)
_GRID_SPACING_MM = 50.0
_GRID_EXTENT_MM = 1000.0


class PreviewCanvas(QGraphicsView):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QColor("#1e1e1e"))
        # Machine Y grows up; Qt scene Y grows down.
        self.scale(1.0, -1.0)
        self._draw_grid()

    # -- data in ----------------------------------------------------------

    def show_preview(self, data: PreviewData) -> None:
        self._scene.clear()
        self._draw_grid()
        for polyline in data.polylines:
            if len(polyline.points) < 2:
                continue
            color, width, style = _ROLE_PENS.get(polyline.role, _DEFAULT_PEN)
            pen = QPen(color, width, style)
            pen.setCosmetic(True)
            polygon = QPolygonF([QPointF(p.x, p.y) for p in polyline.points])
            path_item = self._scene.addPolygon(polygon)
            path_item.setPen(pen)
        for start in (data.wire_start_root, data.wire_start_tip):
            if start is not None:
                marker_pen = QPen(QColor("#ffee58"), 0.0)
                marker_pen.setCosmetic(True)
                self._scene.addEllipse(start.x - 2, start.y - 2, 4, 4, marker_pen)
        if data.polylines:
            self.fitInView(
                self._scene.itemsBoundingRect().adjusted(-20, -20, 20, 20),
                Qt.AspectRatioMode.KeepAspectRatio,
            )

    # -- interaction ------------------------------------------------------

    def wheelEvent(self, event) -> None:  # zoom at cursor
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    # -- painting helpers --------------------------------------------------

    def _draw_grid(self) -> None:
        minor_pen = QPen(QColor("#2c2c2c"), 0.0)
        minor_pen.setCosmetic(True)
        axis_pen = QPen(QColor("#505050"), 0.0)
        axis_pen.setCosmetic(True)

        extent = _GRID_EXTENT_MM
        step = _GRID_SPACING_MM
        line = -extent
        while line <= extent:
            pen = axis_pen if line == 0 else minor_pen
            self._scene.addLine(line, -extent, line, extent, pen)
            self._scene.addLine(-extent, line, extent, line, pen)
            line += step
