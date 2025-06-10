import tkinter as tk
from tkinter import filedialog
from PIL import Image

from py_g_debug.components.TkFolderWatcher import TkFolderWatcher
from py_g_debug.components.footer import Footer
from py_g_debug.components.menu_bar import MenuBar
from py_g_debug.components.main_screen import MainImageDisplay
from py_g_debug.components.custom_types import ClusterType

from typing import List

import json
import csv

APPLICATION_TITLE = "Simple App"
APPLICATION_STARTING_GEOMETRY = "800x600"


class App(tk.Tk):
    """
    Main application class for a simple image viewer with cluster overlay and folder watching.

    Features:
    - Loading and displaying images.
    - Displaying cluster bounding boxes from JSON or CSV.
    - Zoom and pan functionality.
    - Navigation between multiple loaded images.
    - Real-time folder monitoring for new image+data folders.

    Inherits
    --------
    tk.Tk : Base Tkinter application window.
    """

    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.title(APPLICATION_TITLE)
        self.geometry(APPLICATION_STARTING_GEOMETRY)

        # --- Configure grid layout for main window ---
        self.grid_rowconfigure(0, weight=1)  # Image display expands
        self.grid_rowconfigure(1, weight=0)  # Footer fixed height
        self.grid_columnconfigure(0, weight=1)

        # --- Menu bar ---
        self.menu_bar = MenuBar(self, on_open=self.set_img, on_bounding=self.set_clusters, on_watch=self.watch_folder)
        # --- Image display area ---
        self.image_display = MainImageDisplay(self, self.set_color, self.set_position)
        self.image_display.grid(row=0, column=0, sticky="nsew")

        # --- Footer ---
        self.footer = Footer(self, self.active_image_move_left, self.active_image_move_right)
        self.footer.frame.grid(row=1, column=0, sticky="ew")

        self.footer.set_position(0, 0)
        self.footer.set_color((255, 255, 255))

        # --- Folder watcher ---
        self.folder_watcher = None

        # --- Internal state ---
        self.img = []
        self.active_img_id = None

    # --Footer Functions--
    def set_img(self, file_path = None, is_from_watcher = False):
        """
        Loads and displays an image from the specified file path.

        Parameters
        ----------
        file_path : str, optional
            Path to the image file. If None, a file dialog is shown.
        is_from_watcher : bool, optional
            Indicates whether the image comes from the folder watcher. If False,
            clears previous images and disables folder watching.
        """
        if is_from_watcher is False and self.folder_watcher:
            self.folder_watcher.stop()
            self.folder_watcher = None
            self.img = []
            self.active_img_id = None

        if file_path is None: file_path = filedialog.askopenfilename()

        if not file_path:
            return

        self.img.append([file_path, Image.open(file_path).copy(), None])
        self.footer.set_file(file_path)
        self.active_img_id = len(self.img) - 1
        self._lock_unlock_button()
        self.image_display.init_img(self.img[self.active_img_id][1],self.img[self.active_img_id][2])

    def set_clusters(self):
        """
        Loads cluster bounding boxes from a JSON or CSV file and applies them
        to the currently active image.
        """

        if self.active_img_id is None:
            return

        file_path = filedialog.askopenfilename()
        if not file_path:
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

        # noinspection PyUnreachableCode
        print(f"✔ Loaded {len(clusters)} clusters from: {file_path}")
        self.img[self.active_img_id][2] = clusters
        self.image_display.init_img(self.img[self.active_img_id][1], self.img[self.active_img_id][2])

    def watch_folder(self):
        """
        Opens a folder selection dialog and starts monitoring the selected directory
        for new subfolders containing image and cluster data.
        """
        file_path = filedialog.askdirectory()
        if not file_path:
            return
        self.folder_watcher = TkFolderWatcher(self, file_path, self.on_new_folder_detected)
        self.folder_watcher.start()

    def on_move(self, x, y):
        """
        (Alias) Updates position info in the footer. Calls `set_position`.

        Parameters
        ----------
        x : int
            X-coordinate.
        y : int
            Y-coordinate.
        """
        self.footer.set_position(x, y)

    def set_position(self, x, y):
        """
        Updates the footer with the current cursor position.

        Parameters
        ----------
        x : int
            X-coordinate on the image.
        y : int
            Y-coordinate on the image.
        """
        self.footer.set_position(x, y)

    def set_color(self, color):
        """
        Updates the footer with the color at the current cursor position.

        Parameters
        ----------
        color : tuple
            RGB color tuple.
        """
        self.footer.set_color(color)

    def active_image_move_left(self):
        """
        Navigates to the previous image in the list, if available.
        Updates display and footer accordingly.
        """

        if self.active_img_id > 0:
            self.active_img_id -= 1
            self._lock_unlock_button()
            self.footer.set_file(self.img[self.active_img_id][0])
            self.image_display.init_img(self.img[self.active_img_id][1], self.img[self.active_img_id][2])

    def active_image_move_right(self):
        """
        Navigates to the next image in the list, if available.
        Updates display and footer accordingly.
        """

        if self.active_img_id < len(self.img) - 1:
            self.active_img_id += 1
            self._lock_unlock_button()
            self.footer.set_file(self.img[self.active_img_id][0])
            self.image_display.init_img(self.img[self.active_img_id][1], self.img[self.active_img_id][2])

    def _lock_unlock_button(self):
        """
        Enables or disables navigation buttons based on the current image index.
        """
        if self.active_img_id < len(self.img) - 1:
            self.footer.update_navigation_state_right(has_next=True)

        if self.active_img_id > 0:
            self.footer.update_navigation_state_left(has_prev=True)

        if self.active_img_id == 0:
            self.footer.update_navigation_state_left(has_prev=False)

        if self.active_img_id == len(self.img) -1:
            self.footer.update_navigation_state_right(has_next=False)

    # -- Finished Footer --

    def stop_watch_folder(self):
        """
        Stops the active folder watcher, if running.
        """

        self.folder_watcher.stop()
        self.folder_watcher = None

    def on_new_folder_detected(self, image_path: str, clusters: List[ClusterType]):
        """
        Callback executed when a new folder with an image and cluster data is detected.

        Parameters
        ----------
        image_path : str
            Path to the new image file.
        clusters : List[ClusterType]
            List of cluster bounding boxes in the format ((min_x, min_y), (max_x, max_y), pixel_count).
        """
        self.img.append([image_path, Image.open(image_path).copy(), clusters])
        self.active_img_id = len(self.img) - 1
        self.footer.set_file(image_path)
        self._lock_unlock_button()

        self.image_display.init_img(self.img[self.active_img_id][1], self.img[self.active_img_id][2])


if __name__ == "__main__":
    app = App()
    app.mainloop()
