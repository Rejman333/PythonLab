import tkinter as tk
from PIL import Image, ImageTk, ImageDraw

from .components_helper import do_nothing


class MainImageDisplay(tk.Frame):
    def __init__(self, root, set_color=None, set_position=None):
        super().__init__(root)

        self.set_color = set_color or do_nothing()
        self.set_position = set_position or do_nothing()

        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.pack(fill="both", expand=True)

        self.original = None
        self.original_with_bb = None
        self.tk_image = None

        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.image_id = None

        self.x_anchor = 0
        self.y_anchor = 0

        self.viewport_size_width = self.canvas.winfo_width()
        self.viewport_size_height = self.canvas.winfo_height()

        self.canvas.bind("<Motion>", self.mouse_move)
        self.canvas.bind("<MouseWheel>", self.zoom_event)
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.do_pan)
        self.canvas.bind("<Configure>", self.do_resize)
        self.canvas.bind_all("<Escape>", self.reset_view)

    def init_img(self, image, bounding_boxes=None):
        self.original = image.convert("RGB")
        self.original_with_bb = image.copy()
        if bounding_boxes:
            draw = ImageDraw.Draw(self.original_with_bb)
            for (min_i, min_j), (max_i, max_j), _ in bounding_boxes:
                draw.rectangle([(min_j, min_i), (max_j, max_i)], outline="red", width=2)

        self.draw_image()

    def draw_image(self):
        viewport_w = self.canvas.winfo_width()
        viewport_h = self.canvas.winfo_height()

        zoom_w = int(viewport_w / self.zoom)
        zoom_h = int(viewport_h / self.zoom)

        left = int(self.offset_x)
        top = int(self.offset_y)
        box = (left, top, left + zoom_w, top + zoom_h)

        cropped = self.original_with_bb.crop(box)
        resized = cropped.resize((viewport_w, viewport_h), Image.NEAREST)
        self.tk_image = ImageTk.PhotoImage(resized)

        # Wycentrowanie obrazu (jeśli canvas większy niż obraz)

        self.x_anchor = max((viewport_w - self.original.width * self.zoom) // 2, 0)
        self.y_anchor = max((viewport_h - self.original.height * self.zoom) // 2, 0)

        if self.image_id:
            self.canvas.itemconfig(self.image_id, image=self.tk_image)
            self.canvas.coords(self.image_id, self.x_anchor, self.y_anchor)  # ← kluczowe!
        else:
            self.image_id = self.canvas.create_image(self.x_anchor, self.y_anchor, anchor="nw", image=self.tk_image)

    def zoom_event(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        old_zoom = self.zoom
        self.zoom *= factor
        # Zoom center: keep mouse position fixed relative to image
        mx, my = event.x, event.y
        ox = self.offset_x + mx / old_zoom
        oy = self.offset_y + my / old_zoom
        self.offset_x = ox - mx / self.zoom
        self.offset_y = oy - my / self.zoom
        self.clamp_offset()
        self.draw_image()

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def do_pan(self, event):
        dx = (event.x - self.pan_start[0]) / self.zoom
        dy = (event.y - self.pan_start[1]) / self.zoom
        self.offset_x -= dx
        self.offset_y -= dy
        self.pan_start = (event.x, event.y)
        self.clamp_offset()
        self.draw_image()

    def mouse_move(self, event):
        if not self.tk_image or not self.original:
            return

        # Local cursor position relative to image on canvas
        local_x = event.x - self.x_anchor
        local_y = event.y - self.y_anchor

        canvas_w = self.tk_image.width()
        canvas_h = self.tk_image.height()

        crop_w = canvas_w / self.zoom
        crop_h = canvas_h / self.zoom

        pixel_w = canvas_w / crop_w  # czyli = self.zoom
        pixel_h = canvas_h / crop_h  # czyli = self.zoom

        # Map canvas pos to original image
        ox = int(self.offset_x + local_x // pixel_w)
        oy = int(self.offset_y + local_y // pixel_h)

        if 0 <= ox < self.original.width and 0 <= oy < self.original.height:
            rgb = self.original.getpixel((ox, oy))
            self.set_position(ox, oy)
            self.set_color(rgb)

    def clamp_offset(self):
        viewport_w = self.canvas.winfo_width()
        viewport_h = self.canvas.winfo_height()

        max_offset_x = max(0, self.original.width - viewport_w / self.zoom)
        max_offset_y = max(0, self.original.height - viewport_h / self.zoom)

        self.offset_x = max(0, min(self.offset_x, max_offset_x))
        self.offset_y = max(0, min(self.offset_y, max_offset_y))

    def do_resize(self, event):
        if self.tk_image:
            self.viewport_size_width = self.canvas.winfo_width()
            self.viewport_size_height = self.canvas.winfo_height()
            self.draw_image()

    def reset_view(self, event=None):
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.draw_image()
