import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800


class Visualizer2:
    def __init__(self, root):
        self.is_drawing = False
        self.root = root
        self.canvas = tk.Canvas(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, background="black")
        self.canvas.pack()
        self.canvas.focus_set()

        self.img_original = None
        self.img_tk = None
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.start_drag = None

        self.was_resized = True
        self.img_center = None

        self.crop_rectangle_top_left = None
        self.crop_rectangle_bottom_right = None

        self.canvas.bind("<ButtonPress-1>", self.handle_left_click)
        self.canvas.bind("<B1-Motion>", self.movement)
        self.canvas.bind("<MouseWheel>", self.zoom)  # Windows
        # self.canvas.bind("<Button-4>", self.do_zoom)  # Linux scroll up
        # self.canvas.bind("<Button-5>", self.do_zoom)  # Linux scroll down
        # self.canvas.bind("<Button-3>", self.reset_view)

        self.load_image()
        self.draw_frame()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.img_original = Image.open(file_path)
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.img_top_left = (
            (self.img_original.width) // 2,
            (self.img_original.height // 2))

    def handle_left_click(self, event):
        if self.crop_rectangle_top_left:
            if (self.crop_rectangle_top_left[0] >= event.x >= self.crop_rectangle_bottom_right[0] and
                    self.crop_rectangle_top_left[1] >= event.y >= self.crop_rectangle_bottom_right[1]):

                print("Click inside rectangle")
            else:
                print("Click outside rectangle")
                self.crop_rectangle_bottom_right = None
                self.crop_rectangle_top_left = None

        elif self.crop_rectangle_top_left:
            self.crop_rectangle_bottom_right = (event.x, event.y)
            print(f"Ended rectangle on {event.x, event.y}")

        else:
            self.crop_rectangle_top_left = (event.x, event.y)
            print(f"Started rectangle on {event.x, event.y}")

    def clamp_offset(self):
        disp_w, disp_h = self.start_drag
        max_x = max(0, (disp_w - WINDOW_WIDTH) // 2)
        max_y = max(0, (disp_h - WINDOW_HEIGHT) // 2)
        self.offset_x = max(-max_x, min(self.offset_x, max_x))
        self.offset_y = max(-max_y, min(self.offset_y, max_y))

    def movement(self, event):
        if self.crop_rectangle_top_left and not self.crop_rectangle_bottom_right:
            self.draw_frame()

    def zoom(self, event):
        factor = 1.1 if event.delta > 0 else 0.9

        self.zoom_factor *= factor
        self.zoom_factor = max(0.1, min(20.0, self.zoom_factor))
        self.was_resized = True
        self.draw_frame()

    def draw_frame(self):
        if not self.img_original:
            return

        w, h = self.img_original.size
        zoomed_w = int(w * self.zoom_factor)
        zoomed_h = int(h * self.zoom_factor)

        # crop_w = int(self.canvas.winfo_width() / self.zoom_factor)
        # crop_h = int(self.canvas.winfo_height() / self.zoom_factor)
        right = min(self.img_top_left[0] + self.canvas.winfo_width(), self.img_original.width)
        lower = min(self.img_top_left[1] + self.canvas.winfo_height(), self.img_original.height)

        # cropped = self.img_original.crop((self.img_top_left[0], self.img_top_left[1], right, lower))
        # resized = cropped.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.NEAREST)
        self.img_tk = ImageTk.PhotoImage(self.img_original)

        self.canvas.delete("all")

        self.canvas.create_image(0, 0, anchor="nw",
                                 image=self.img_tk)


        self.last_img_x = self.offset_x
        self.last_img_y = self.offset_y


class Visualizer:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, background="black")
        self.canvas.pack()
        self.canvas.focus_set()

        self.img_original = None
        self.img_tk = None
        self.zoom_factor = 1.0
        self.last_zoom_time = 0
        self.offset_x = 0
        self.offset_y = 0

        self.last_frame_time = time.time()
        self.frame_count = 0
        self.fps = 0

        self.resize_needed = True

        self.fps_label = tk.Label(self.root, fg="white", bg="black")
        self.fps_label.place(x=10, y=10)

        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.do_pan)
        self.canvas.bind("<MouseWheel>", self.do_zoom)  # Windows
        # self.canvas.bind("<Button-4>", self.do_zoom)  # Linux scroll up
        # self.canvas.bind("<Button-5>", self.do_zoom)  # Linux scroll down
        # self.canvas.bind("<Button-3>", self.reset_view)

        self.load_image()

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.img_original = Image.open(file_path)
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.update_image()

    def update_image(self):
        now = time.time()
        dt = now - self.last_frame_time
        self.last_frame_time = now

        if dt > 0:
            self.fps = 1.0 / dt
            self.fps_label.config(text=f"FPS: {self.fps:.2f}")

        if not self.img_original:
            return

        w, h = self.img_original.size
        zoomed_w = int(w * self.zoom_factor)
        zoomed_h = int(h * self.zoom_factor)

        resized = self.img_original.resize((zoomed_w, zoomed_h), Image.NEAREST)
        print("I am resizing!")

        self.img_tk = ImageTk.PhotoImage(resized)
        self.canvas.delete("all")

        x = (WINDOW_WIDTH - zoomed_w) // 2 + self.offset_x
        y = (WINDOW_HEIGHT - zoomed_h) // 2 + self.offset_y
        self.canvas.create_image(x, y, anchor="nw", image=self.img_tk)

        self.last_img_x = x
        self.last_img_y = y
        self.img_disp_size = (zoomed_w, zoomed_h)

    def start_pan(self, event):
        self.start_drag = (event.x, event.y)

    def do_pan(self, event):
        if self.start_drag:
            dx = event.x - self.start_drag[0]
            dy = event.y - self.start_drag[1]
            self.offset_x += dx
            self.offset_y += dy
            self.start_drag = (event.x, event.y)
            self.clamp_offset()
            self.update_image()

    def clamp_offset(self):
        # Prevent moving too far out of bounds
        disp_w, disp_h = self.img_disp_size
        max_x = max(0, (disp_w - WINDOW_WIDTH) // 2)
        max_y = max(0, (disp_h - WINDOW_HEIGHT) // 2)
        self.offset_x = max(-max_x, min(self.offset_x, max_x))
        self.offset_y = max(-max_y, min(self.offset_y, max_y))

    def do_zoom(self, event):
        if time.time() - self.last_zoom_time < 0.05:
            return

        if not self.img_original:
            return

        # Get zoom direction
        delta = 1 if event.delta > 0 or event.num == 4 else -1
        factor = 1.1 if delta > 0 else 0.9

        # Save current mouse pos in image coords
        canvas_mouse_x = event.x
        canvas_mouse_y = event.y

        img_x = (canvas_mouse_x - self.last_img_x) / self.zoom_factor
        img_y = (canvas_mouse_y - self.last_img_y) / self.zoom_factor

        # Update zoom
        self.zoom_factor *= factor
        self.zoom_factor = max(0.1, min(20, self.zoom_factor))

        # Adjust offset to zoom into the point under the cursor
        new_w = self.img_original.width * self.zoom_factor
        new_h = self.img_original.height * self.zoom_factor
        self.offset_x = int(canvas_mouse_x - img_x * self.zoom_factor - (WINDOW_WIDTH - new_w) / 2)
        self.offset_y = int(canvas_mouse_y - img_y * self.zoom_factor - (WINDOW_HEIGHT - new_h) / 2)

        self.clamp_offset()
        self.update_image()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("IrfanView-Like Image Viewer")
    app = Visualizer2(root)
    root.mainloop()
