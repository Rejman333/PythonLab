import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

from .components_helper import do_nothing
from .zoom_rectangle import ZoomRectangle


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
        self.canvas.bind("<ButtonPress-1>", self.left_click)
        self.canvas.bind("<B1-Motion>", self.left_click_motion)
        self.canvas.bind("<ButtonRelease-1>", self.left_click_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        self.original_image = None
        self.image = None
        self.tk_img = None
        self.canvas_img_id = None

        self.start_drag = None
        self.offset = (0, 0)

        self.zoom_rectangle = ZoomRectangle()

    def zoom_img(self):
        scaled_start = self._get_mouse_on_img(self.zoom_rectangle.start_position, True)
        scaled_end = self._get_mouse_on_img(self.zoom_rectangle.end_position, True)

        crop_box = (scaled_start[0], scaled_start[1],
                    scaled_end[0], scaled_end[1])

        region = self.image.crop(crop_box)
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        zoomed = region.resize((canvas_w, canvas_h), Image.NEAREST)
        self.tk_img = ImageTk.PhotoImage(zoomed)
        self.canvas.delete("all")
        self.offset = (0, 0)

        self.canvas_img_id = self.canvas.create_image(self.offset[0], self.offset[1], image=self.tk_img, anchor="nw")

    def on_mouse_move(self, event):
        if self.canvas_img_id is None:
            return

        x, y = self._get_mouse_on_img(event)
        self.set_position(x + 1, y + 1)
        self.set_color(self.image.getpixel((x, y)))

    def left_click(self, event):
        if self.canvas_img_id is None:
            return
        if self.zoom_rectangle.is_rectangle_finished:
            if self.zoom_rectangle.is_clicked((event.x, event.y)):
                print("Zoom")
                self.zoom_img()
            self.zoom_rectangle.destroy(self.canvas)
            self.canvas.config(cursor="arrow")

        else:
            self.canvas.config(cursor="cross")
            self.zoom_rectangle.destroy(self.canvas)
            self.zoom_rectangle.create(self.canvas, (event.x, event.y))
            return

    def left_click_motion(self, event):
        if self.canvas_img_id is None:
            return

        if self.zoom_rectangle.start_position:
            self.zoom_rectangle.move(self.canvas, (event.x, event.y))

    def left_click_release(self, event):
        if self.canvas_img_id is None:
            return

        if self.zoom_rectangle.end_position:
            self.canvas.config(cursor="arrow")
            self.zoom_rectangle.finish()

    def update_image(self, image: Image.Image):
        self.original_image = image
        self.image = image
        self.tk_img = ImageTk.PhotoImage(self.image)
        self.canvas.delete("all")

        x, y = self._count_relative_xy()
        self.canvas_img_id = self.canvas.create_image(x, y, image=self.tk_img, anchor="nw")

    def on_pen(self):
        if self.tk_img and self.canvas_img_id:
            x, y = self._count_relative_xy()
            self.canvas.coords(self.canvas_img_id, x, y)

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

    def _get_mouse_on_img(self, mouse, special=False):
        x, y = self._count_relative_xy()
        if special:
            return min(max(mouse[0] - x, 0), self.image.width - 1), min(max(mouse[1] - y, 0), self.image.height - 1)
        return min(max(mouse.x - x, 0), self.image.width - 1), min(max(mouse.y - y, 0), self.image.height - 1)

    def _count_relative_xy(self):
        relative_x = (self.canvas.winfo_width() - self.image.width) // 2 + self.offset[0]
        relative_y = (self.canvas.winfo_height() - self.image.height) // 2 + self.offset[1]
        return relative_x, relative_y

    def _on_canvas_resize(self, event):
        if self.tk_img and self.canvas_img_id:
            x, y = self._count_relative_xy()
            self.canvas.coords(self.canvas_img_id, x, y)

    def _process_img(self):
        crop_box = (0, 0, self.original_image.width(), self.original_image.height())

        region = self.image.crop(crop_box)
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        zoomed = region
        self.tk_img = ImageTk.PhotoImage(zoomed)
        self.canvas.delete("all")
        self.offset = (0, 0)
        x, y = self._count_relative_xy()
        self.canvas_img_id = self.canvas.create_image(x, y, image=self.tk_img, anchor="nw")
