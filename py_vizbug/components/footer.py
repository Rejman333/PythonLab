import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class Footer:
    def __init__(self, root, on_prev_callback, on_post_callback):
        self.frame = ttk.Frame(root)
        self.frame.grid(row=1, column=0, sticky="ew")

        # Configure layout
        root.grid_columnconfigure(0, weight=1)
        for i in range(6):
            self.frame.columnconfigure(i, weight=0)

        self.frame.columnconfigure(0, weight=1)  # file label
        self.frame.columnconfigure(1, weight=1)  # position
        self.frame.columnconfigure(2, weight=1)  # color
        self.frame.columnconfigure(3, minsize=30)  # color canvas
        self.frame.columnconfigure(4, minsize=40)  # ◀ button
        self.frame.columnconfigure(5, minsize=40)  # ▶ button

        # UI elements
        self.file_label = ttk.Label(self.frame, text="File: None", anchor="w")
        self.pos_label = ttk.Label(self.frame, text="X: -, Y: -", anchor="center")
        self.color_label = ttk.Label(self.frame, text="Color: -, -, -", anchor="e")

        self.color_canvas = tk.Canvas(self.frame, width=20, height=20, highlightthickness=1,
                                      highlightbackground="black")
        self.color_rect = self.color_canvas.create_rectangle(0, 0, 20, 20, fill="#000000")

        self.prev_button = ttk.Button(self.frame, text="◀", command=self.on_prev, state="disabled")
        self.next_button = ttk.Button(self.frame, text="▶", command=self.on_next, state="disabled")

        # Place in grid
        self.file_label.grid(row=0, column=0, sticky="w", padx=10)
        self.pos_label.grid(row=0, column=1, sticky="n", padx=10)
        self.color_label.grid(row=0, column=2, sticky="e", padx=(10, 2))
        self.color_canvas.grid(row=0, column=3, padx=(0, 10))
        self.prev_button.grid(row=0, column=4, padx=(5, 2))
        self.next_button.grid(row=0, column=5, padx=(2, 10))

        # Callback holders
        self.on_prev_callback = on_prev_callback
        self.on_next_callback = on_post_callback

    def set_file(self, filename: str):
        self.file_label.config(text=f"File: {filename}")

    def set_position(self, x: int, y: int):
        self.pos_label.config(text=f"X: {x}, Y: {y}")

    def set_color(self, rgba: tuple):
        r, g, b = rgba[:3]
        self.color_label.config(text=f"Color: {r}, {g}, {b}")
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        self.color_canvas.itemconfig(self.color_rect, fill=hex_color)

    def set_navigation_callbacks(self, on_prev: Callable[[], None], on_next: Callable[[], None]):
        self.on_prev_callback = on_prev
        self.on_next_callback = on_next

    def on_prev(self):
        if self.on_prev_callback:
            self.on_prev_callback()

    def on_next(self):
        if self.on_next_callback:
            self.on_next_callback()

    def update_navigation_state_left(self, has_prev: bool):
        self.prev_button.config(state="normal" if has_prev else "disabled")

    def update_navigation_state_right(self, has_next: bool):
        self.next_button.config(state="normal" if has_next else "disabled")
