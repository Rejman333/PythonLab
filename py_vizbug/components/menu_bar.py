from tkinter import Menu
from .components_helper import do_nothing


class MenuBar:
    def __init__(self, root, on_open=None, on_bounding=None, on_watch = None, on_exit=None, on_about=None):
        self.root = root
        self.on_open = on_open or do_nothing
        self.on_bounding = on_bounding or do_nothing
        self.on_watch = on_watch or do_nothing
        self.on_exit = on_exit or self._default_exit
        self.on_about = on_about or do_nothing

        self._create_menu_bar()

    def _create_menu_bar(self):
        menu_bar = Menu(self.root)

        # File Menu
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.on_open)
        file_menu.add_command(label="Import Bounding Boxes", command=self.on_bounding)
        file_menu.add_separator()
        file_menu.add_command(label="Monitor Folder", command=self.on_watch)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Help Menu
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About...", command=self.on_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def _default_exit(self):
        self.root.quit()
