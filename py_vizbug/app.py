import tkinter as tk
from tkinter import filedialog
from PIL import Image

from py_vizbug.components.footer import Footer
from py_vizbug.components.menu_bar import MenuBar
from py_vizbug.components.main_screen import MainImageDisplay

from typing import List, Tuple

import json
import csv

ClusterType = Tuple[Tuple[int, int], Tuple[int, int], int]


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.title("Simple App")
        self.geometry("800x600")

        # --- Configure grid layout for main window ---
        self.grid_rowconfigure(0, weight=1)  # Image display expands
        self.grid_rowconfigure(1, weight=0)  # Footer fixed height
        self.grid_columnconfigure(0, weight=1)

        # --- Menu bar ---
        self.menu_bar = MenuBar(self, on_open=self.set_img, on_bounding=self.set_clusters)
        # --- Image display area ---
        self.image_display = MainImageDisplay(self, self.set_color, self.set_position)
        self.image_display.grid(row=0, column=0, sticky="nsew")

        # --- Footer ---
        self.footer = Footer(self, self.active_image_move_left, self.active_image_move_right)
        self.footer.frame.grid(row=1, column=0, sticky="ew")

        self.footer.set_position(120, 240)
        self.footer.set_color((255, 200, 150))

        # --- Internal state ---
        self.img = []
        self.active_img_id = None

    def set_img(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.img.append([file_path, Image.open(file_path).copy(), None])
        self.footer.set_file(file_path)
        self.active_img_id = len(self.img) - 1
        self._lock_unlock_button()
        self.image_display.init_img(self.img[self.active_img_id][1])

    # noinspection PyUnreachableCode
    def set_clusters(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        if self.active_img_id is None:
            return

        clusters: List[ClusterType] = []

        if file_path.lower().endswith('.json'):
            with open(file_path, 'r') as file:
                data = json.load(file)
                for entry in data:
                    min_x = entry['min_x']
                    min_y = entry['min_y']
                    max_x = entry['max_x']
                    max_y = entry['max_y']
                    pixel_count = entry['pixel_count']
                    clusters.append(((min_x, min_y), (max_x, max_y), pixel_count))

        elif file_path.lower().endswith('.csv'):
            with open(file_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    min_x = int(row['min_x'])
                    min_y = int(row['min_y'])
                    max_x = int(row['max_x'])
                    max_y = int(row['max_y'])
                    pixel_count = int(row['pixel_count'])
                    clusters.append(((min_x, min_y), (max_x, max_y), pixel_count))
        else:
            print("Unsupported file type. Use .csv or .json.")
            return

        self.img[self.active_img_id][2] =  clusters
        print(f"✔ Loaded {len(clusters)} clusters from: {file_path}")

    def on_move(self, x, y):
        self.footer.set_position(x,y)

    def set_position(self, x, y):
        self.footer.set_position(x, y)

    def set_color(self, color):
        self.footer.set_color(color)

    def active_image_move_left(self):
        if self.active_img_id > 0:
            self.active_img_id -= 1
            self._lock_unlock_button()
            self.footer.set_file(self.img[self.active_img_id][0])
            self.image_display.init_img(self.img[self.active_img_id][1])

    def active_image_move_right(self):
        if self.active_img_id < len(self.img):
            self.active_img_id += 1
            self._lock_unlock_button()
            self.footer.set_file(self.img[self.active_img_id][0])
            self.image_display.init_img(self.img[self.active_img_id][1])

    def _lock_unlock_button(self):

        if self.active_img_id < len(self.img) - 1:
            self.footer.update_navigation_state_right(has_next=True)

        if self.active_img_id > 0:
            self.footer.update_navigation_state_left(has_prev=True)

        if self.active_img_id == 0:
            self.footer.update_navigation_state_left(has_prev=False)

        if self.active_img_id == len(self.img):
            self.footer.update_navigation_state_right(has_next=False)


if __name__ == "__main__":
    app = App()
    app.mainloop()
