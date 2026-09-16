from __future__ import annotations

from math import ceil, floor

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QWidget

from hotwire_core.models import MachineLimits
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
_GEOMETRY_PADDING = 0.125


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
        self._preview = PreviewData()
        self._visible = {"root": True, "tip": True}
        self._path_items = {"root": [], "tip": []}
        self._start_markers = {"root": [], "tip": []}
        self._machine_rect = QRectF(
            -_GRID_EXTENT_MM,
            -_GRID_EXTENT_MM,
            2 * _GRID_EXTENT_MM,
            2 * _GRID_EXTENT_MM,
        )
        self._draw_grid()

    # data in

    def set_machine_limits(self, limits: MachineLimits | None) -> None:
        if limits is None:
            self._machine_rect = QRectF(
                -_GRID_EXTENT_MM,
                -_GRID_EXTENT_MM,
                2 * _GRID_EXTENT_MM,
                2 * _GRID_EXTENT_MM,
            )
            return
        self._machine_rect = QRectF(
            limits.x_min_mm,
            limits.y_min_mm,
            max(limits.x_max_mm - limits.x_min_mm, 1.0),
            max(limits.y_max_mm - limits.y_min_mm, 1.0),
        )

    def show_preview(self, data: PreviewData) -> None:
        self._preview = data
        self._scene.clear()
        self._draw_grid()
        self._path_items = {"root": [], "tip": []}
        self._start_markers = {"root": [], "tip": []}
        for polyline in data.polylines:
            if len(polyline.points) < 2:
                continue
            color, width, style = _ROLE_PENS.get(polyline.role, _DEFAULT_PEN)
            pen = QPen(color, width, style)
            pen.setCosmetic(True)
            path = QPainterPath()
            path.moveTo(polyline.points[0].x, polyline.points[0].y)
            for point in polyline.points[1:]:
                path.lineTo(point.x, point.y)
            path_item = self._scene.addPath(path, pen)
            path_item.setPen(pen)
            side = (
                "root"
                if polyline.role.endswith("_root")
                else "tip"
                if polyline.role.endswith("_tip")
                else None
            )
            if side is not None:
                self._path_items[side].append(path_item)
                path_item.setVisible(self._visible[side])
        for side, start in (
            ("root", data.wire_start_root),
            ("tip", data.wire_start_tip),
        ):
            if start is not None:
                marker_pen = QPen(QColor("#ffee58"), 0.0)
                marker_pen.setCosmetic(True)
                marker = self._scene.addEllipse(
                    start.x - 2, start.y - 2, 4, 4, marker_pen
                )
                self._start_markers[side].append(marker)
                marker.setVisible(self._visible[side])

    def set_root_visible(self, visible: bool) -> None:
        self._set_visible("root", visible)

    def set_tip_visible(self, visible: bool) -> None:
        self._set_visible("tip", visible)

    def fit_geometry(self) -> None:
        bounds = self._geometry_bounds()
        if bounds is None:
            return
        pad_x = max(bounds.width() * _GEOMETRY_PADDING, 1.0)
        pad_y = max(bounds.height() * _GEOMETRY_PADDING, 1.0)
        self.fitInView(
            bounds.adjusted(-pad_x, -pad_y, pad_x, pad_y),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def fit_machine(self) -> None:
        self.fitInView(self._machine_rect, Qt.AspectRatioMode.KeepAspectRatio)

    def reset_view(self) -> None:
        self.resetTransform()
        self.scale(1.0, -1.0)
        if self._geometry_bounds() is not None:
            self.fit_geometry()
        else:
            self.fit_machine()

    # interaction

    def wheelEvent(self, event) -> None:  # zoom at cursor
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawForeground(painter, rect)
        painter.save()
        painter.resetTransform()
        painter.setPen(QColor("#9e9e9e"))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)

        viewport = self.viewport().rect()
        painter.drawText(12, viewport.height() - 10, "X (mm)")
        painter.drawText(12, 18, "Y (mm)")

        scene_rect = self.mapToScene(viewport).boundingRect()
        origin = self.mapFromScene(QPointF(0.0, 0.0))
        step = _GRID_SPACING_MM
        while scene_rect.width() / step > 20.0:
            step *= 2.0

        if 0 <= origin.y() <= viewport.height():
            for index in range(floor(scene_rect.left() / step), ceil(scene_rect.right() / step) + 1):
                point = self.mapFromScene(QPointF(index * step, 0.0))
                if 0 <= point.x() <= viewport.width():
                    painter.drawText(point.x() + 3, point.y() - 5, f"{index * step:g}")

        if 0 <= origin.x() <= viewport.width():
            for index in range(floor(scene_rect.top() / step), ceil(scene_rect.bottom() / step) + 1):
                point = self.mapFromScene(QPointF(0.0, index * step))
                if 0 <= point.y() <= viewport.height():
                    painter.drawText(point.x() + 4, point.y() - 4, f"{index * step:g}")
        painter.restore()

    # painting helpers

    def _set_visible(self, side: str, visible: bool) -> None:
        self._visible[side] = visible
        for item in self._path_items[side] + self._start_markers[side]:
            item.setVisible(visible)

    def _geometry_bounds(self) -> QRectF | None:
        points = [
            point for polyline in self._preview.polylines for point in polyline.points
        ]
        if not points:
            return None
        min_x = min(point.x for point in points)
        max_x = max(point.x for point in points)
        min_y = min(point.y for point in points)
        max_y = max(point.y for point in points)
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

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
