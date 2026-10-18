import tkinter as tk
from tkinter import ttk
import random
import math
from collections import deque

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class WirelessHandoverSimulator:

    def __init__(self, root):
        self.root = root
        self.root.title("Wireless Network Handover Simulator")
        self.root.geometry("1050x760")
        self.root.configure(bg="#eef3f8")

        # Simulation settings
        self.running = False
        self.after_id = None
        self.position = 0
        self.current_ap = "AP1"
        self.handover_count = 0
        self.time_step = 0

        self.aps = ["AP1", "AP2", "AP3"]
        self.colors = {
            "AP1": "blue",
            "AP2": "green",
            "AP3": "red"
        }

        self.history = {
            "AP1": deque(maxlen=60),
            "AP2": deque(maxlen=60),
            "AP3": deque(maxlen=60)
        }

        self.time_history = deque(maxlen=60)

        self.signal_values = {
            "AP1": 0,
            "AP2": 0,
            "AP3": 0
        }

        self.create_interface()
        self.update_display()

    def create_interface(self):

        title = tk.Label(
            self.root,
            text="WIRELESS NETWORK HANDOVER SIMULATOR",
            font=("Arial", 20, "bold"),
            bg="#17365d",
            fg="white",
            pady=15
        )
        title.pack(fill="x")

        subtitle = tk.Label(
            self.root,
            text="Simulation of Mobile Connectivity Between Wireless Access Points",
            font=("Arial", 11),
            bg="#eef3f8"
        )
        subtitle.pack(pady=8)

        # Connection information
        info_frame = tk.Frame(self.root, bg="#eef3f8")
        info_frame.pack(pady=10)

        self.connection_label = tk.Label(
            info_frame,
            text="Connected Access Point: AP1",
            font=("Arial", 14, "bold"),
            fg="green",
            bg="#eef3f8"
        )
        self.connection_label.grid(row=0, column=0, padx=20)

        self.handover_label = tk.Label(
            info_frame,
            text="Total Handovers: 0",
            font=("Arial", 14, "bold"),
            fg="#17365d",
            bg="#eef3f8"
        )
        self.handover_label.grid(row=0, column=1, padx=20)

        self.position_label = tk.Label(
            self.root,
            text="Mobile Position: 0",
            font=("Arial", 12),
            bg="#eef3f8"
        )
        self.position_label.pack(pady=5)

        # Access point signal bars
        signal_frame = tk.LabelFrame(
            self.root,
            text="Access Point Signal Strength",
            font=("Arial", 12, "bold"),
            bg="#eef3f8",
            padx=15,
            pady=10
        )
        signal_frame.pack(fill="x", padx=30, pady=10)

        self.signal_bars = {}
        self.signal_labels = {}

        for index, ap in enumerate(self.aps):

            tk.Label(
                signal_frame,
                text=ap,
                font=("Arial", 12, "bold"),
                bg="#eef3f8"
            ).grid(row=index, column=0, padx=10, pady=8)

            bar = ttk.Progressbar(
                signal_frame,
                length=400,
                maximum=100,
                mode="determinate"
            )
            bar.grid(row=index, column=1, padx=10, pady=8)

            label = tk.Label(
                signal_frame,
                text="0%",
                font=("Arial", 11),
                bg="#eef3f8"
            )
            label.grid(row=index, column=2, padx=10)

            self.signal_bars[ap] = bar
            self.signal_labels[ap] = label

        # Mobile movement representation
        movement_frame = tk.LabelFrame(
            self.root,
            text="Mobile Movement",
            font=("Arial", 12, "bold"),
            bg="#eef3f8",
            padx=10,
            pady=10
        )
        movement_frame.pack(fill="x", padx=30, pady=5)

        self.movement_canvas = tk.Canvas(
            movement_frame,
            width=900,
            height=100,
            bg="white",
            highlightthickness=1
        )
        self.movement_canvas.pack()

        # Graph
        graph_frame = tk.Frame(self.root, bg="#eef3f8")
        graph_frame.pack(fill="both", expand=True, padx=25, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(8, 3.0))

        self.fig.tight_layout()

        self.chart = FigureCanvasTkAgg(
            self.fig,
            master=graph_frame
        )
        self.chart.get_tk_widget().pack(fill="both", expand=True)

        # Buttons
        button_frame = tk.Frame(self.root, bg="#eef3f8")
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="START SIMULATION",
            command=self.start,
            bg="#198754",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=12
        ).grid(row=0, column=0, padx=8)

        tk.Button(
            button_frame,
            text="PAUSE",
            command=self.pause,
            bg="#ffc107",
            font=("Arial", 11, "bold"),
            padx=15
        ).grid(row=0, column=1, padx=8)

        tk.Button(
            button_frame,
            text="RESET",
            command=self.reset,
            bg="#dc3545",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15
        ).grid(row=0, column=2, padx=8)

        # Event log
        log_frame = tk.LabelFrame(
            self.root,
            text="Handover Event Log",
            font=("Arial", 12, "bold"),
            bg="#eef3f8",
            padx=10,
            pady=5
        )
        log_frame.pack(fill="x", padx=30, pady=5)

        self.log_box = tk.Text(
            log_frame,
            height=4,
            font=("Consolas", 10),
            state="disabled"
        )
        self.log_box.pack(fill="x")

        self.add_log("Simulation ready. Mobile connected to AP1.")

    def calculate_signals(self):

        # Each access point has a different ideal position.
        # Signal decreases as the mobile moves away.

        centers = {
            "AP1": 15,
            "AP2": 50,
            "AP3": 85
        }

        for ap in self.aps:

            distance = abs(self.position - centers[ap])

            signal = 100 * math.exp(
                -(distance ** 2) / (2 * 18 ** 2)
            )

            # Small variation to imitate signal fluctuation
            signal += random.uniform(-3, 3)

            self.signal_values[ap] = max(
                0,
                min(100, int(signal))
            )

    def start(self):

        if not self.running:
            self.running = True
            self.simulate()

    def pause(self):

        self.running = False

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.add_log("Simulation paused.")

    def reset(self):

        self.pause()

        self.position = 0
        self.current_ap = "AP1"
        self.handover_count = 0
        self.time_step = 0

        self.time_history.clear()

        for ap in self.aps:
            self.history[ap].clear()

        self.add_log("Simulation reset.")

        self.update_display()

    def simulate(self):

        if not self.running:
            return

        # Move the mobile device across the simulated area
        self.position += 1

        if self.position > 100:
            self.position = 0

        self.time_step += 1

        self.calculate_signals()

        # Find the access point with the strongest signal
        strongest_ap = max(
            self.aps,
            key=lambda ap: self.signal_values[ap]
        )

        # Handover decision with a small signal margin
        current_signal = self.signal_values[self.current_ap]
        strongest_signal = self.signal_values[strongest_ap]

        if (
            strongest_ap != self.current_ap
            and strongest_signal >= current_signal + 5
        ):

            previous_ap = self.current_ap
            self.current_ap = strongest_ap
            self.handover_count += 1

            self.add_log(
                f"HANDOVER: {previous_ap} -> {self.current_ap} "
                f"| Signal: {strongest_signal}%"
            )

        self.time_history.append(self.time_step)

        for ap in self.aps:
            self.history[ap].append(
                self.signal_values[ap]
            )

        self.update_display()

        self.after_id = self.root.after(
            500,
            self.simulate
        )

    def update_display(self):

        self.calculate_signals()

        self.connection_label.config(
            text=f"Connected Access Point: {self.current_ap}"
        )

        self.handover_label.config(
            text=f"Total Handovers: {self.handover_count}"
        )

        self.position_label.config(
            text=f"Mobile Position: {self.position}"
        )

        for ap in self.aps:

            signal = self.signal_values[ap]

            self.signal_bars[ap]["value"] = signal

            self.signal_labels[ap].config(
                text=f"{signal}%"
            )

        self.draw_movement()
        self.draw_graph()

    def draw_movement(self):

        canvas = self.movement_canvas
        canvas.delete("all")

        width = 900

        # Draw the three access point locations
        locations = {
            "AP1": 135,
            "AP2": 450,
            "AP3": 765
        }

        for ap, x in locations.items():

            canvas.create_oval(
                x - 20, 15, x + 20, 55,
                fill=self.colors[ap]
            )

            canvas.create_text(
                x, 5,
                text=ap,
                anchor="s",
                font=("Arial", 10, "bold")
            )

        # Draw the mobile position
        mobile_x = 50 + int(self.position * 8)

        canvas.create_line(
            50, 75, 850, 75,
            fill="gray",
            width=3
        )

        canvas.create_oval(
            mobile_x - 12, 63,
            mobile_x + 12, 87,
            fill="orange"
        )

        canvas.create_text(
            mobile_x,
            95,
            text="Mobile",
            font=("Arial", 9)
        )

    def draw_graph(self):

        self.ax.clear()

        for ap in self.aps:

            values = list(self.history[ap])

            if values:
                self.ax.plot(
                    range(len(values)),
                    values,
                    label=ap,
                    color=self.colors[ap],
                    linewidth=2
                )

        self.ax.set_title("Wireless Signal Strength")
        self.ax.set_xlabel("Simulation Steps")
        self.ax.set_ylabel("Signal Strength (%)")
        self.ax.set_ylim(0, 105)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper right")

        self.fig.tight_layout()
        self.chart.draw()

    def add_log(self, message):

        self.log_box.config(state="normal")

        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

        self.log_box.config(state="disabled")


if __name__ == "__main__":

    root = tk.Tk()

    app = WirelessHandoverSimulator(root)

    root.mainloop()