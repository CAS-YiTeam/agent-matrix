import time
from rich.live import Live
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

# Create a layout with two columns
layout = Layout()

# Divide the layout into two columns
layout.split_row(
    Layout(name="left" ),
    Layout(name="right"),
)
T1 = Text("", overflow='fold')
T2 = Text("", overflow='fold')
P1 = Panel(T1, title="Left")
P2 = Panel(T2, title="Left")
layout["left"].update(P1)
layout["right"].update(P2)

# Create a console instance with the layout
console = Console()


# Start the live display with the initial layout
with Live(layout, console=console, auto_refresh=True):
    for i in range(1000):
        time.sleep(0.2)
        T1.append(f"{i}: Hello, World!\n")
        T2.append(f"{i}: Hello, World!\n")
        T2.append(f"{i}: Hello, World!\n")