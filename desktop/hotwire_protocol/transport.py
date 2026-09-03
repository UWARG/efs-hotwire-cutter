from __future__ import annotations

from dataclasses import dataclass

from hotwire_protocol import DEFAULT_BAUD


@dataclass(frozen=True)
class PortInfo:
    device: str  # e.g. "COM8"
    description: str


class TransportError(Exception):
    """Open/read/write failures."""


def list_ports() -> list[PortInfo]:
    """Enumerate serial ports available on this machine."""
    from serial.tools import list_ports as _lp

    return [PortInfo(device=p.device, description=p.description) for p in _lp.comports()]


class SerialTransport:
    def __init__(self, port: str, baud: int = DEFAULT_BAUD, timeout_s: float = 2.0):
        self._port = port
        self._baud = baud
        self._timeout_s = timeout_s
        self._serial = None

    def open(self) -> None:
        import serial

        if self._serial is not None:
            raise TransportError(f"{self._port} is already open")
        try:
            self._serial = serial.Serial(self._port, self._baud, timeout=self._timeout_s)
        except (serial.SerialException, OSError, ValueError) as exc:
            raise TransportError(f"could not open {self._port}: {exc}") from exc

    def close(self) -> None:
        handle, self._serial = self._serial, None
        if handle is not None:
            try:
                handle.close()
            except Exception:
                pass

    @property
    def is_open(self) -> bool:
        return self._serial is not None and bool(self._serial.is_open)

    def write_line(self, line: str) -> None:
        import serial

        handle = self._serial
        if handle is None:
            raise TransportError("port is not open")
        try:
            handle.write((line + "\n").encode("ascii"))
            handle.flush()
        except (serial.SerialException, OSError) as exc:
            raise TransportError(f"write failed on {self._port}: {exc}") from exc

    def read_line(self) -> str | None:
        import serial

        handle = self._serial
        if handle is None:
            raise TransportError("port is not open")
        try:
            raw = handle.readline()
        except (serial.SerialException, OSError, TypeError) as exc:

            raise TransportError(f"read failed on {self._port}: {exc}") from exc
        if not raw:
            return None
        return raw.decode(errors="replace").strip()
