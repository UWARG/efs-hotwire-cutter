from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Signal

from hotwire_protocol.commands import Hello
from hotwire_protocol.decoder import decode_line
from hotwire_protocol.encoder import encode
from hotwire_protocol.transport import PortInfo, SerialTransport, TransportError, list_ports


class SerialService(QObject):
    connected = Signal(str)  # port device name
    disconnected = Signal()
    response_received = Signal(object)  # decoded Response
    raw_line = Signal(str, str)  # direction ("tx"/"rx"), line — for the console
    error = Signal(str)  # user-facing message

    _connection_lost = Signal(str)  

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._transport: SerialTransport | None = None
        self._reader: threading.Thread | None = None
        self._stop_reading = threading.Event()
        self._connection_lost.connect(self._on_connection_lost)


    def available_ports(self) -> list[PortInfo]:
        try:
            return list_ports()
        except Exception as exc:  # pyserial missing or platform failure
            self.error.emit(f"Port scan failed: {exc}")
            return []

    # connection lifecycle 

    @property
    def is_connected(self) -> bool:
        return self._transport is not None

    def connect_port(self, device: str) -> None:
        """Open the port, start the reader thread, send HELLO."""
        if self._transport is not None:
            self.error.emit("Already connected")
            return
        transport = SerialTransport(device)
        try:
            transport.open()
        except TransportError as exc:
            self.error.emit(str(exc))
            return

        self._transport = transport
        self._stop_reading.clear()
        self._reader = threading.Thread(
            target=self._read_loop, args=(transport,), name="serial-reader", daemon=True
        )
        self._reader.start()
        self.connected.emit(device)
        self.send_line(encode(Hello()))

    def disconnect_port(self) -> None:
        """Stop the reader thread and close the port."""
        transport, self._transport = self._transport, None
        if transport is None:
            return
        self._stop_reading.set()
        transport.close()  # breaks the read loop
        reader, self._reader = self._reader, None
        if reader is not None and reader is not threading.current_thread():
            reader.join(timeout=3.0)
        self.disconnected.emit()

    # outbound 

    def send_line(self, line: str) -> None:
        """Send one already-encoded line."""
        transport = self._transport
        if transport is None:
            self.error.emit("Not connected")
            return
        try:
            transport.write_line(line)
            self.raw_line.emit("tx", line)
        except TransportError as exc:
            self.error.emit(f"Write failed: {exc}")
            self.disconnect_port()

    # reader thread 

    def _read_loop(self, transport: SerialTransport) -> None:
        while not self._stop_reading.is_set():
            try:
                line = transport.read_line()
            except TransportError as exc:
                if not self._stop_reading.is_set():
                    self._connection_lost.emit(str(exc))
                return
            if line:
                self.raw_line.emit("rx", line)
                self.response_received.emit(decode_line(line))

    def _on_connection_lost(self, message: str) -> None:
        self.error.emit(f"Serial connection lost: {message}")
        self.disconnect_port()
