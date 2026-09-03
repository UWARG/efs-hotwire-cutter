from __future__ import annotations

from enum import Enum
from typing import Callable

from hotwire_core.models import Toolpath
from hotwire_protocol.commands import StatusReport
from hotwire_protocol.transport import SerialTransport


class SenderState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    FAULTED = "faulted"
    COMPLETE = "complete"


class StreamingSender:
    def __init__(
        self,
        transport: SerialTransport,
        on_state_change: Callable[[SenderState], None] | None = None,
        on_progress: Callable[[int, int], None] | None = None,
    ):
        self._transport = transport
        self._on_state_change = on_state_change
        self._on_progress = on_progress
        self._state = SenderState.IDLE

    @property
    def state(self) -> SenderState:
        return self._state

    def load(self, toolpath: Toolpath) -> None:
        raise NotImplementedError

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

    def on_status(self, report: StatusReport) -> None:
        raise NotImplementedError

    def progress(self) -> tuple[int, int]:
        raise NotImplementedError
