import os
import tkinter as tk

class TkFolderWatcher:
    def __init__(self, app: tk.Tk, folder_path: str, callback, delay_ms=1000):
        self.app = app
        self.folder_path = folder_path
        self.callback = callback
        self.delay_ms = delay_ms
        self._known_files = set()
        self._running = False

    def start(self):
        if not os.path.isdir(self.folder_path):
            print("❌ Folder does not exist:", self.folder_path)
            return
        self._known_files = set(os.listdir(self.folder_path))
        self._running = True
        self._poll()

    def stop(self):
        self._running = False

    def _poll(self):
        if not self._running:
            return

        current_files = set(os.listdir(self.folder_path))
        new_files = current_files - self._known_files

        for file in new_files:
            full_path = os.path.join(self.folder_path, file)
            if os.path.isfile(full_path):
                self.callback(full_path)

        self._known_files = current_files
        self.app.after(self.delay_ms, self._poll)
