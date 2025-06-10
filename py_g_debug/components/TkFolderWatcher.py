import os
import tkinter as tk
import csv
from typing import Callable, List, Tuple

ClusterType = Tuple[Tuple[int, int], Tuple[int, int], int]

class TkFolderWatcher:
    """
    A simple folder watcher for Tkinter applications that polls a specified directory
    for newly created subdirectories containing image and CSV data.

    When a new folder with `image.png` is detected, optionally accompanied by `data.csv`,
    the provided callback is called with the image path and parsed data.

    Parameters
    ----------
    app : tk.Tk
        The Tkinter application instance used for scheduling periodic polling.
    folder_path : str
        The path to the directory to be monitored.
    callback : Callable[[str, List[ClusterType]], None]
        A function to call when a new folder is detected. Receives the path to the image
        and a list of bounding box data.
    delay_ms : int, optional
        Delay in milliseconds between each polling cycle. Default is 1000 ms.
    """

    def __init__(self, app: tk.Tk, folder_path: str, callback: Callable[[str, List[ClusterType]], None], delay_ms=1000):
        self.app = app
        self.folder_path = folder_path
        self.callback = callback
        self.delay_ms = delay_ms
        self._known_dirs = set()
        self._running = False

    def start(self):
        """
        Starts the folder watching process.

        Initializes the known set of subdirectories and begins polling.
        If the folder path is invalid, prints a warning and aborts.
        """
        if not os.path.isdir(self.folder_path):
            print("Folder does not exist:", self.folder_path)
            return
        self._known_dirs = set(next(os.walk(self.folder_path))[1])  # only subdirs
        self._running = True
        self._poll()

    def stop(self):
        """
        Stops the folder watching process.

        Prevents further polling cycles from being scheduled.
        """
        self._running = False

    def _poll(self):
        """
        Internal method that performs a polling cycle.

        Detects new subdirectories. If a subdirectory contains an `image.png` file,
        and optionally a `data.csv` file, parses the CSV data and calls the callback
        with the image path and list of clusters.
        Reschedules itself using `after` for continuous monitoring.
        """
        if not self._running:
            return

        current_dirs = set(next(os.walk(self.folder_path))[1])
        new_dirs = current_dirs - self._known_dirs

        for dirname in new_dirs:
            full_dir_path = os.path.join(self.folder_path, dirname)
            image_path = os.path.join(full_dir_path, "image.png")
            csv_path = os.path.join(full_dir_path, "data.csv")

            if os.path.isfile(image_path):
                print(f"📁 New folder with image: {image_path}")
                clusters = []

                if os.path.isfile(csv_path):
                    print(f"📄 Found data.csv in {dirname}")
                    try:
                        with open(csv_path, newline='') as csvfile:
                            reader = csv.DictReader(csvfile)
                            for row in reader:
                                min_x = int(row['min_x'])
                                min_y = int(row['min_y'])
                                max_x = int(row['max_x'])
                                max_y = int(row['max_y'])
                                pixel_count = int(row['pixel_count'])
                                clusters.append(((min_x, min_y), (max_x, max_y), pixel_count))
                    except Exception as e:
                        print(f"⚠️ Failed to read {csv_path}: {e}")

                # Trigger callback (e.g., self.set_img_and_clusters(image_path, clusters))
                self.callback(image_path, clusters)

        self._known_dirs = current_dirs
        self.app.after(self.delay_ms, self._poll)
