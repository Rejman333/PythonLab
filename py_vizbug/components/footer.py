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

        self.file_label = ttk.Label(self.frame, text="File: None", anchor="w")
        self.pos_label = ttk.Label(self.frame, text="X: -, Y: -", anchor="center")
        self.color_label = ttk.Label(self.frame, text="Color: -, -, -", anchor="e")

        # Place each label in one of the 3 columns
        self.file_label.grid(row=0, column=0, sticky="w", padx=10)
        self.pos_label.grid(row=0, column=1, sticky="n", padx=10)
        self.color_label.grid(row=0, column=2, sticky="e", padx=10)

    def set_file(self, filename: str):
        self.file_label.config(text=f"File: {filename}")

    def set_position(self, x: int, y: int):
        self.pos_label.config(text=f"X: {x}, Y: {y}")

    def set_color(self, rgb: tuple):
        r, g, b = rgb
        self.color_label.config(text=f"Color: {r}, {g}, {b}")
