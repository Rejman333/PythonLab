import tkinter as tk
from tkinter import filedialog
from PIL import Image

from py_vizbug.components.footer import Footer
from py_vizbug.components.menu_bar import MenuBar
from py_vizbug.components.main_screen import MainImageDisplay


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
        self.menu_bar = MenuBar(self, on_open=self.set_img)
        # --- Image display area ---
        self.image_display = MainImageDisplay(self, self.set_color, self.set_position)
        self.image_display.grid(row=0, column=0, sticky="nsew")

        # --- Footer ---
        self.footer = Footer(self)
        self.footer.frame.grid(row=1, column=0, sticky="ew")

        self.footer.set_position(120, 240)
        self.footer.set_color((255, 200, 150))

        # --- Internal state ---
        self.img = None

    def set_img(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.img = Image.open(file_path)
        self.footer.set_file(file_path)
        self.image_display.update_image(self.img)

    def on_move(self, x, y):
        self.footer.set_position(x)

    def set_position(self, x, y):
        self.footer.set_position(x, y)

    def set_color(self, color):
        self.footer.set_color(color)


if __name__ == "__main__":
    app = App()
    app.mainloop()
