from rich.text import Text
from textual import work, on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Footer, Button, RichLog
from textual.worker import Worker, get_current_worker
from textual.validation import Integer,Regex
from textual.binding import Binding

import queue
import serial
import time
import datetime

class SerialConsoleApp(App):
    """A simple Serial Console App for sending and receiving serial data"""
    BINDINGS = [Binding(key="q", action="quit_serial_console", description="Quit App"),
                Binding(key="c", action="clear_serial_console", description="Clear Console"),]
    CSS_PATH = "serial-console-tui.tcss"

    device = '/dev/ttyACM0'
    baudrate = 115200
    ser = serial.Serial(device, baudrate, timeout=2)
    writeQueue = queue.Queue()

    def compose(self) -> ComposeResult:
        with Horizontal():
            #yield Input(placeholder=f"Send Serial on {self.device}", validators=[Integer(),Regex("[0123456789]*"),],validate_on=["submitted"])
            yield Input(placeholder=f"Send Serial on {self.device}")
        with Vertical(id="serial-output-container"):
            yield RichLog()
        yield Footer()

    async def on_mount(self) -> None:
        self.serial_read_write()
        
    @on(Input.Submitted)
    async def input_changed(self, message: Input.Changed) -> None:
        await self.serial_write(message.value)
        
    async def serial_write(self, data) -> None:
        self.writeQueue.put(data)

    @work(exclusive=True, thread=True)
    def serial_read_write(self) -> None:
        worker = get_current_worker()
        while True:
            if self.ser.in_waiting > 0 and self.writeQueue.empty():
                self.incoming = self.ser.readline().decode("utf-8")
                self.call_from_thread(self.query_one(RichLog).write,  f"{datetime.datetime.now().strftime('%H:%M:%S')} {self.incoming.strip()}")
            elif self.writeQueue.qsize() > 0:
                data = self.writeQueue.get()
                data = data + '\n'
                self.ser.write(data.encode())

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        self.log(event)

    def action_clear_serial_console(self) -> None:
        self.query_one(RichLog).clear()

    def action_quit_serial_console(self) -> None:
        self.ser.close()
        self.app.exit()

if __name__ == "__main__":
    app = SerialConsoleApp()
    app.run()