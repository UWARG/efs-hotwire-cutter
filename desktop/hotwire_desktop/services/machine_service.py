from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from hotwire_protocol import commands as cmd
from hotwire_protocol.encoder import EncodeError, encode


class MachineService(QObject):
    status_updated = Signal(object)  # cmd.StatusReport
    job_progress = Signal(int, int)  # sent, total
    fault = Signal(str)
    message = Signal(str)  # user-facing notices

    def __init__(self, serial_service, parent: QObject | None = None):
        super().__init__(parent)
        self._serial = serial_service
        self._serial.response_received.connect(self._on_response)

    # -- manual control ----------------------------------------------------

    def jog(self, axis: cmd.Axis, distance_mm: float, feedrate_mm_min: float) -> None:
        self._send(cmd.Jog(axis, distance_mm, feedrate_mm_min))

    def jog_coordinated(self, dx_mm: float, dy_mm: float, feedrate_mm_min: float) -> None:
        self.message.emit("Coordinated jog not impl")

    def set_zero(self) -> None:
        self._send(cmd.SetZero())

    def set_heat(self, heat_percent: float) -> None:
        self.message.emit("Heat control not done yet")

    def request_status(self) -> None:
        self._send(cmd.StatusRequest())

    # -- job control ---------------------------------------------------------

    def run_job(self, toolpath) -> None:
        if toolpath is None or not toolpath.moves:
            self.message.emit("No toolpath")
            return

        total = len(toolpath.moves)
        self._send(cmd.RunBegin())
        for sent, move in enumerate(toolpath.moves, 1):
            self._send(
                cmd.Move4(
                    xl_mm=move.xl,
                    yl_mm=move.yl,
                    xr_mm=move.xr,
                    yr_mm=move.yr,
                    feedrate_mm_min=move.feedrate_mm_min,
                )
            )
            self.job_progress.emit(sent, total)
        self._send(cmd.RunEnd())

    def stop_job(self) -> None:
        self._send(cmd.Stop())

    def emergency_stop(self) -> None:
        self._send(cmd.Stop())

    # -- internals ---------------------------------------------------------

    def _send(self, command: cmd.Command) -> None:
        try:
            self._serial.send_line(encode(command))
        except NotImplementedError:
            self.message.emit(" encoder not implemented")
        except EncodeError as exc:
            self.message.emit(str(exc))

    def _on_response(self, response) -> None:
        if isinstance(response, cmd.StatusReport):
            self.status_updated.emit(response)
        elif isinstance(response, cmd.Invalid):
            self.fault.emit("Firmware rejected command")
