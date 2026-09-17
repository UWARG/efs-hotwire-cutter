from __future__ import annotations

from enum import Enum
from typing import Callable

from hotwire_core.models import Toolpath
from hotwire_protocol import commands as cmd
from hotwire_protocol.encoder import encode


class SenderState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPING = "stopping"


class StreamingSender:
    def __init__(
        self,
        send_line: Callable[[str], None],
        on_progress: Callable[[int, int], None] | None = None,
    ):
        self._send_line = send_line
        self._on_progress = on_progress
        self._state = SenderState.IDLE
        self._moves = []
        self._next = 0
        self._in_flight = 0
        self._buffer_free: int | None = None
        self._run_started = False

    def start(self, toolpath: Toolpath) -> None:
        if self._state != SenderState.IDLE:
            raise RuntimeError("sender is busy")
        if not toolpath.moves:
            raise ValueError("toolpath has no moves")
        self._moves = list(toolpath.moves)
        self._next = 0
        self._in_flight = 0
        self._buffer_free = None
        self._run_started = False
        self._state = SenderState.RUNNING
        self._send(cmd.RunBegin())

    def stop(self) -> None:
        if self._state == SenderState.STOPPING:
            return
        self._state = SenderState.STOPPING
        self._send(cmd.Stop())

    def handle(self, response: cmd.Response) -> str | None:
        if isinstance(response, cmd.Invalid):
            self.reset()
            return "Firmware rejected command"
        if isinstance(response, cmd.StatusReport):
            if self._state == SenderState.RUNNING and self._run_started:
                self._buffer_free = response.buffer_free
                self._pump()
            return None
        if not isinstance(response, cmd.Ok):
            return None

        if self._state == SenderState.STOPPING and response.command_name == "STOP":
            self.reset()
            return None
        if self._state != SenderState.RUNNING:
            return None

        if response.command_name == "RUN_BEGIN" and not self._run_started:
            if response.buffer_free is None:
                self.reset()
                return "RUN_BEGIN response missing BUFFER_FREE"
            self._run_started = True
            self._buffer_free = response.buffer_free
            self._pump()
        elif response.command_name == "MOVE4" and self._in_flight:
            self._in_flight -= 1
            if response.buffer_free is not None:
                self._buffer_free = response.buffer_free
            if self._on_progress is not None:
                self._on_progress(self._next - self._in_flight, len(self._moves))
            self._pump()
        elif response.command_name == "RUN_END":
            self.reset()
        return None

    def reset(self) -> None:
        self._state = SenderState.IDLE

    def _pump(self) -> None:
        if self._state != SenderState.RUNNING or self._buffer_free is None:
            return
        available = max(0, self._buffer_free - self._in_flight)
        while available and self._next < len(self._moves):
            move = self._moves[self._next]
            self._send(cmd.Move4(move.xl, move.yl, move.xr, move.yr, move.feedrate_mm_min))
            self._next += 1
            self._in_flight += 1
            available -= 1
        if self._next == len(self._moves) and not self._in_flight:
            self._run_started = False
            self._send(cmd.RunEnd())

    def _send(self, command: cmd.Command) -> None:
        self._send_line(encode(command))
