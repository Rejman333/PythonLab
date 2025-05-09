import tkinter as tk
from PIL import Image, ImageTk

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
        self.canvas.bind("<ButtonPress-3>", self.right_click)
        self.canvas.bind("<B3-Motion>", self.right_click_motion)
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
        self.zoom_offset = (0, 0)
        self.crop_box = None

    def init_img(self, image: Image.Image):
        self.original_image = image
        self.image = image
        self.offset = (0, 0)
        self.zoom_offset = (0, 0)
        self.zoom_rectangle.destroy(self.canvas)
        self.crop_box = (0, 0, self.original_image.width, self.original_image.height)

        self._process_img()

    def on_mouse_move(self, event):
        if self.canvas_img_id is None:
            return

        x, y = self._from_screen_to_img_point_convertion((event.x, event.y))
        # self.set_position(x + 1, y + 1)
        # self.set_color(self.image.getpixel((x, y)))

    def left_click(self, event):
        if self.canvas_img_id is None:
            return
        if self.zoom_rectangle.is_rectangle_finished:
            if self.zoom_rectangle.is_clicked((event.x, event.y)):
                print("Zoom")
                self._zoom_img()
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

    def right_click(self, event):
        if self.tk_img:
            self.start_drag = (event.x, event.y)

    def right_click_motion(self, event):
        if self.tk_img and self.start_drag:
            dx = event.x - self.start_drag[0]
            dy = event.y - self.start_drag[1]
            self.offset = (self.offset[0] + dx, self.offset[1] + dy)
            self.start_drag = (event.x, event.y)
            self.clamp_offset()
            x, y = self._count_relative_xy()
            self.canvas.coords(self.canvas_img_id, x, y)

    def clamp_offset(self):
        # Prevent moving too far out of bounds
        max_x = max(0, (self.tk_img.width() - self.canvas.winfo_width()) // 2)
        max_y = max(0, (self.tk_img.height() - self.canvas.winfo_height()) // 2)
        self.offset = (max(-max_x, min(self.offset[0], max_x)), max(-max_y, min(self.offset[1], max_y)))

    def _from_screen_to_img_point_convertion(self, point):
        x, y = self._count_relative_xy()
        return min(max(point[0] - x, 0), self.image.width - 1), min(max(point[1] - y, 0), self.image.height - 1)

    def _count_relative_xy(self):
        relative_x = (self.canvas.winfo_width() - self.image.width) // 2 + self.offset[0]
        relative_y = (self.canvas.winfo_height() - self.image.height) // 2 + self.offset[1]
        return relative_x, relative_y

    def _on_canvas_resize(self, event):
        if self.tk_img and self.canvas_img_id:
            x, y = self._count_relative_xy()
            self.canvas.coords(self.canvas_img_id, x, y)

    def _process_img(self):
        # Crop the selected region
        cropped = self.original_image.crop(self.crop_box)

        # Target size (canvas size)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Original cropped size
        img_width, img_height = cropped.size

        # Compute uniform scale factor (no distortion)
        scale = min(canvas_width // img_width, canvas_height // img_height)

        # Scaled size
        new_size = (img_width * scale, img_height * scale)

        # Resize using nearest-neighbor (no smoothing)
        if scale != 0:
            resized = cropped.resize(new_size, Image.NEAREST)
        else:
            resized = cropped

        # Store and display
        self.image = resized
        self.tk_img = ImageTk.PhotoImage(self.image)

        self.canvas.delete("all")

        # Center the image
        x, y = self._count_relative_xy()
        self.canvas_img_id = self.canvas.create_image(x, y, image=self.tk_img, anchor="nw")

    def _zoom_img(self):
        p1_after_convertion = self._from_screen_to_img_point_convertion(self.zoom_rectangle.start_position)
        p2_after_convertion = self._from_screen_to_img_point_convertion(self.zoom_rectangle.end_position)
        self.crop_box = (p1_after_convertion[0], p1_after_convertion[1],
                         p2_after_convertion[0], p2_after_convertion[1])
        print(self.crop_box)
        self._process_img()
