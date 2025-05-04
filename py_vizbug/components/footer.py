import tkinter as tk
from tkinter import ttk


class Footer:
    def __init__(self, root):
        self.frame = ttk.Frame(root)
        self.frame.grid(row=1, column=0, sticky="ew")  # Full width across row

        # Make the frame expand horizontally with the window
        root.grid_columnconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.columnconfigure(2, weight=1)
        self.frame.columnconfigure(3, minsize=30)

        self.file_label = ttk.Label(self.frame, text="File: None", anchor="w")
        self.pos_label = ttk.Label(self.frame, text="X: -, Y: -", anchor="center")
        self.color_label = ttk.Label(self.frame, text="Color: -, -, -", anchor="e")

        # Color preview rectangle
        self.color_canvas = tk.Canvas(self.frame, width=20, height=20, highlightthickness=1, highlightbackground="black")
        self.color_rect = self.color_canvas.create_rectangle(0, 0, 20, 20, fill="#000000")

        # Grid placement
        self.file_label.grid(row=0, column=0, sticky="w", padx=10)
        self.pos_label.grid(row=0, column=1, sticky="n", padx=10)
        self.color_label.grid(row=0, column=2, sticky="e", padx=(10, 2))
        self.color_canvas.grid(row=0, column=3, padx=(0, 10))

    def set_file(self, filename: str):
        self.file_label.config(text=f"File: {filename}")

    def set_position(self, x: int, y: int):
        self.pos_label.config(text=f"X: {x}, Y: {y}")

    def set_color(self, rgba: tuple):
        r, g, b = rgba[:3]
        self.color_label.config(text=f"Color: {r}, {g}, {b}")
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.color_canvas.itemconfig(self.color_rect, fill=hex_color)
