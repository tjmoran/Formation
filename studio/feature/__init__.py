import logging
from tkinter import StringVar, BooleanVar

from hoverset.ui.icons import get_icon, get_icon_image
from hoverset.ui.widgets import Frame, Button, Label, MenuButton
from studio.ui.geometry import absolute_position

logging.basicConfig(level=logging.DEBUG)


class BaseFeature(Frame):
    name = "Feature"
    side = "left"
    pane = None
    bar = None
    icon = "blank"
    _view_mode = None
    _transparency_flag = None
    rec = (20, 20, 300, 300)  # Default window mode position

    def __init__(self, master, studio=None,  **cnf):
        super().__init__(master, **cnf)
        if not self.__class__._view_mode:
            self.__class__._view_mode = StringVar(None, "docked")
            self.__class__._transparency_flag = BooleanVar(None, False)
        self.studio = studio
        self._header = Frame(self, **self.style.dark, **self.style.dark_highlight_dim, height=30)
        self._header.pack(side="top", fill="x")
        self._header.pack_propagate(0)
        self._header.allow_drag = True
        Label(self._header, **self.style.dark_text_passive, text=self.name).pack(side="left")
        self._min = Button(self._header, text=get_icon("close"), **self.style.dark_button, width=25, height=25)
        self._min.pack(side="right")
        self._min.on_click(self.minimize)
        self._pref = MenuButton(self._header, text=get_icon("settings"), **self.style.dark_button)
        self._pref.pack(side="right")
        menu = self.make_menu((
            ("cascade", "View Mode", None, None, {"menu": (
                ("radiobutton", "Docked", None, self.open_as_docked, {"variable": self._view_mode, "value": "docked"}),
                ("radiobutton", "Window", None, self.open_as_window, {"variable": self._view_mode, "value": "window"}),
            )}),
            ("cascade", "Position", None, None, {"menu": (
                ("command", "Left", None, lambda: self.reposition("left"), {}),
                ("command", "Right", None, lambda: self.reposition("right"), {}),
            )}),
            ("checkbutton", "Transparent when inactive", None, None, {"variable": self._transparency_flag}),
            ("command", "Close", get_icon_image("close", 14, 14), self.minimize, {}),
            ("separator",),
            *self.create_menu()
        ), self._pref)
        self._pref.config(menu=menu)
        # self._pref.on_click(self.minimize)
        self.config(**self.style.dark)
        self.is_visible = True
        self.indicator = None
        self.window_handle = None
        self.on_focus(self._on_focus_get)
        self.on_focus_lost(self._on_focus_release)
        self.on_close(self.close_window)

    def on_select(self, widget):
        pass

    def on_widget_change(self, old_widget, new_widget=None):
        pass

    def on_widget_layout_change(self, widget):
        pass

    def on_widget_add(self, widget, parent):
        pass

    def on_widget_delete(self, widget):
        pass

    def on_widget_restore(self, widget):
        pass

    def minimize(self, *_):
        if self.window_handle:
            self.close_window()
        self.studio.minimize(self)
        self.is_visible = False

    def maximize(self):
        if self._view_mode.get() == "window":
            self.open_as_window()
            self.bar.select(self)
        else:
            self.studio.maximize(self)
        self.is_visible = True

    def reposition(self, side):
        if self.window_handle:
            return
        if side == self.side:
            return
        self.__class__.side = side
        self.studio.uninstall(self)
        self.studio.install(self.__class__)

    def toggle(self):
        if self.is_visible:
            self.minimize()
        else:
            self.maximize()

    def create_menu(self):
        """
        Override this method to provide additional menu options
        :return: tuple of menu templates i.e. (type, label, image, callback, **additional_config)
        """
        # return an empty tuple as default
        return ()

    def _on_focus_release(self):
        if self._transparency_flag.get() and self.window_handle:
            if self.window_handle:
                self.window_handle.wm_attributes('-alpha', 0.3)

    def _on_focus_get(self):
        if self.window_handle:
            self.window_handle.wm_attributes('-alpha', 1.0)

    def open_as_docked(self):
        self._view_mode.set("docked")
        if self.window_handle:
            self.master.window.wm_forget(self)
            self.window_handle = None
            self.maximize()

    def open_as_window(self):
        self.master.window.wm_forget(self)
        rec = absolute_position(self) if self.winfo_ismapped() else self.__class__.rec
        self.window.wm_manage(self)
        # Allow us to create a hook in the close method of the window manager
        self.bind_close()
        self.wm_attributes('-toolwindow', True)
        self.transient(self.master.window)
        self.geometry('{}x{}+{}+{}'.format(rec[2], rec[3], rec[0], rec[1]))
        self.update_idletasks()
        self.window_handle = self
        self._view_mode.set("window")

    def close_window(self):
        if self.window_handle:
            # Store the current position of our window handle to used when it is reopened
            self.__class__.rec = absolute_position(self)
            self.master.window.wm_forget(self)
            self.window_handle = None
            self.is_visible = False
