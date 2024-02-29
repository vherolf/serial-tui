from rich.text import Text
from textual import work, on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Footer, Button, RichLog
from textual.worker import Worker, get_current_worker
from textual.validation import Integer,Regex
from textual.binding import Binding

import serial
import time

class SerialApp(App):
    """Serial monitor App"""
    BINDINGS = [Binding(key="q", action="quit", description="Quit the app"),]
    CSS_PATH = "serial-worker-tui.tcss"

    device = '/dev/ttyACM0'
    baudrate = 115200
    ser = serial.Serial(device, baudrate)
    sending = False
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            #yield Input(placeholder=f"Send Serial on {self.device}", validators=[Integer(),Regex("[0123456789]*"),],validate_on=["submitted"])
            yield Input(placeholder=f"Send Serial on {self.device}")
        with Vertical(id="serial-output-container"):
            yield RichLog()
        yield Footer()

    async def on_mount(self) -> None:
        self.serial_read()
        
    @on(Input.Submitted)
    async def input_changed(self, message: Input.Changed) -> None:
        await self.serial_write(message.value)
        
    async def serial_write(self, data) -> None:
            self.sending = True # kills the serial reader worker
            data = data + '\n'
            self.ser.write(data.encode())
            self.sending = False
            self.serial_read()

    @work(exclusive=True, thread=True)
    def serial_read(self) -> None:
        worker = get_current_worker()
        while True:
            # this is for killing the worker
            if self.sending == True:
                break
            if self.ser.in_waiting > 0:
                self.incoming = self.ser.readline().decode("utf-8")
                self.call_from_thread(self.query_one(RichLog).write, f"{self.incoming.strip()}")

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        self.log(event)

if __name__ == "__main__":
    app = SerialApp()
    app.run()