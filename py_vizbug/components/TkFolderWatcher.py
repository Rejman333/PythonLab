import os
import tkinter as tk
import csv
from typing import Callable, List, Tuple

ClusterType = Tuple[Tuple[int, int], Tuple[int, int], int]

class TkFolderWatcher:
    def __init__(self, app: tk.Tk, folder_path: str, callback: Callable[[str, List[ClusterType]], None], delay_ms=1000):
        self.app = app
        self.folder_path = folder_path
        self.callback = callback
        self.delay_ms = delay_ms
        self._known_dirs = set()
        self._running = False

    def start(self):
        if not os.path.isdir(self.folder_path):
            print("❌ Folder does not exist:", self.folder_path)
            return
        self._known_dirs = set(next(os.walk(self.folder_path))[1])  # only subdirs
        self._running = True
        self._poll()

    def stop(self):
        self._running = False

    def _poll(self):
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
