from tkinter import Menu
from .components_helper import do_nothing


class MenuBar:
    """
       A menu bar component for a Tkinter GUI application.

       Includes a "File" menu with options to open files, import bounding boxes,
       monitor a folder, and exit the application. Also includes a "Help" menu
       with an "About" dialog.

       Parameters
       ----------
       root : tk.Tk or tk.Toplevel
           The root window to which the menu bar will be attached.
       on_open : Callable, optional
           Callback for the "Open" menu item. Defaults to a no-op.
       on_bounding : Callable, optional
           Callback for the "Import Bounding Boxes" menu item. Defaults to a no-op.
       on_watch : Callable, optional
           Callback for the "Monitor Folder" menu item. Defaults to a no-op.
       on_exit : Callable, optional
           Callback for the "Exit" menu item. Defaults to closing the window.
       on_about : Callable, optional
           Callback for the "About..." menu item. Defaults to a no-op.
       """
    def __init__(self, root, on_open=None, on_bounding=None, on_watch = None, on_exit=None, on_about=None):
        self.root = root
        self.on_open = on_open or do_nothing
        self.on_bounding = on_bounding or do_nothing
        self.on_watch = on_watch or do_nothing
        self.on_exit = on_exit or self._default_exit
        self.on_about = on_about or do_nothing

        self._create_menu_bar()

    def _create_menu_bar(self):
        """
        Internal method to construct and attach the menu bar to the root window.

        Creates two menus: "File" and "Help", and binds each menu item to its
        corresponding callback.
        """

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
        """
        Default action for the "Exit" menu item.

        Terminates the application by calling `root.quit()`.
        """
        self.root.quit()
