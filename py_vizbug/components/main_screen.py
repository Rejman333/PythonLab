import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

from .components_helper import do_nothing


class MainImageDisplay(tk.Frame):
    def __init__(self, root, set_color=None, set_position=None):
        super().__init__(root)

        self.set_color = set_color or do_nothing()
        self.set_position = set_position or do_nothing()

        self.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.do_pan)
        self.canvas.bind("<ButtonPress-1>", self.start_zoom)
        self.canvas.bind("<B1-Motion>", self.do_zoom)
        self.canvas.bind("<ButtonRelease-1>", self.end_zoom)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        self.original_image = None
        self.image = None
        self.tk_img = None
        self.canvas_img_id = None

        self.start_drag = None
        self.offset = (0, 0)

        self.start_rectangle = None
        self.end_rectangle = None
        self.rectangle_id = None
        self.is_rectangle_finished = False

    def on_mouse_move(self, event):
        if self.canvas_img_id is None:
            return

        x, y = self._get_mouse_on_img((event.x, event.y))
        self.set_position(x, y)
        self.set_color(self.image.getpixel((x, y)))

        if self.rectangle_id and self.is_rectangle_finished:
            if (self.start_rectangle[0] <= event.x - self.offset[0] <= self.end_rectangle[0] and
                    self.start_rectangle[1] <= event.y - self.offset[1] <= self.end_rectangle[1]):
                self.canvas.config(cursor="plus")
            else:
                self.canvas.config(cursor="arrow")

    def start_zoom(self, event):
        if self.canvas_img_id is None:
            return

        if not self.is_rectangle_finished:
            self.canvas.config(cursor="cross")
            self.start_rectangle = (event.x - self.offset[0], event.y - self.offset[1])
            self.end_rectangle = (event.x - self.offset[0], event.y - self.offset[1])

            self.rectangle_id = self.canvas.create_rectangle(
                event.x + self.offset[0], event.y + self.offset[1], event.x + self.offset[0], event.y + self.offset[1],
                outline="red", width=1
            )

        else:
            if (self.start_rectangle[0] <= event.x - self.offset[0] <= self.end_rectangle[0] and
                    self.start_rectangle[1] <= event.y - self.offset[1] <= self.end_rectangle[1]):
                self.canvas.config(cursor="arrow")
                print("Zoom")

                region = self.image.crop((self.start_rectangle[0], self.start_rectangle[1],
                                          self.end_rectangle[0], self.end_rectangle[1]))
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                zoomed = region.resize((canvas_width, canvas_height), resample=Image.NEAREST)

                self.tk_img = ImageTk.PhotoImage(zoomed)

                self.canvas.delete("all")  # Clear previous image
                self.canvas_img_id = self.canvas.create_image(
                    self.canvas.winfo_width() // 2 + self.offset[0],
                    self.canvas.winfo_height() // 2 + self.offset[1],
                    image=self.tk_img,
                    anchor="center"
                )


            else:
                print("Destroy")

            self.is_rectangle_finished = False
            self.start_rectangle = None
            self.end_rectangle = None
            self.canvas.delete(self.rectangle_id)
            self.rectangle_id = None
            return

    def do_zoom(self, event):
        if self.canvas_img_id is None:
            return

        if self.rectangle_id is not None and self.start_rectangle:
            # Update the rectangle's coordinates
            self.end_rectangle = (event.x - self.offset[0], event.y - self.offset[1])

            self.canvas.coords(
                self.rectangle_id,
                self.start_rectangle[0] + self.offset[0],
                self.start_rectangle[1] + self.offset[1],
                self.end_rectangle[0] + self.offset[0],
                self.end_rectangle[1] + self.offset[1],
            )

    def end_zoom(self, event):
        if self.canvas_img_id is None:
            return

        if self.rectangle_id is not None and self.start_rectangle:
            self.canvas.config(cursor="arrow")
            self.end_rectangle = (event.x - self.offset[0], event.y - self.offset[1])
            self.is_rectangle_finished = True

    def update_image(self, image: Image.Image):
        self.original_image = image
        self.image = image
        self.tk_img = ImageTk.PhotoImage(self.image)

        self.canvas.delete("all")  # Clear previous image
        self.canvas_img_id = self.canvas.create_image(
            self.canvas.winfo_width() // 2 + self.offset[0],
            self.canvas.winfo_height() // 2 + self.offset[1],
            image=self.tk_img,
            anchor="center"
        )

    def _on_canvas_resize(self, event):
        if self.tk_img and self.canvas_img_id:
            self.canvas.coords(
                self.canvas_img_id,
                event.width // 2 + self.offset[0],
                event.height // 2 + self.offset[1]
            )
        if self.rectangle_id and self.start_rectangle and self.end_rectangle:
            self.canvas.coords(
                self.rectangle_id,
                self.start_rectangle[0] + self.offset[0],
                self.start_rectangle[1] + self.offset[1],
                self.end_rectangle[0] + self.offset[0],
                self.end_rectangle[1] + self.offset[1],
            )

    def on_pen(self):
        if self.tk_img and self.canvas_img_id:
            # Reposition image to new center
            self.canvas.coords(
                self.canvas_img_id,
                self.canvas.winfo_width() // 2 + self.offset[0],
                self.canvas.winfo_height() // 2 + self.offset[1]
            )
            if self.rectangle_id:
                self.canvas.coords(
                    self.rectangle_id,
                    self.start_rectangle[0] + self.offset[0],
                    self.start_rectangle[1] + self.offset[1],
                    self.end_rectangle[0] + self.offset[0],
                    self.end_rectangle[1] + self.offset[1],
                )

    def start_pan(self, event):
        if self.tk_img:
            self.start_drag = (event.x, event.y)

    def do_pan(self, event):
        if self.tk_img and self.start_drag:
            dx = event.x - self.start_drag[0]
            dy = event.y - self.start_drag[1]
            self.offset = (self.offset[0] + dx, self.offset[1] + dy)
            self.start_drag = (event.x, event.y)
            self.clamp_offset()
            self.on_pen()

    def clamp_offset(self):
        # Prevent moving too far out of bounds
        max_x = max(0, (self.tk_img.width() - self.canvas.winfo_width()) // 2)
        max_y = max(0, (self.tk_img.height() - self.canvas.winfo_height()) // 2)
        self.offset = (max(-max_x, min(self.offset[0], max_x)), max(-max_y, min(self.offset[1], max_y)))

    def _get_mouse_on_img(self, mouse):
        new_mouse_position = (
            max(min(mouse[0] - max((self.canvas.winfo_width() - self.image.width) // 2, 0), self.image.width - 1), 0) -
            self.canvas.winfo_width() // 2 + self.offset[0],
            max(min(mouse[1] - max((self.canvas.winfo_height() - self.image.height) // 2, 0), self.image.height - 1),
                0) - self.canvas.winfo_height() // 2 + self.offset[1]
        )
        return new_mouse_position
