import logging
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import ttkbootstrap as ttk
import chapters.ui.ch_icon as icon
from typing import List, Dict, TextIO

logger = logging.getLogger(__name__)


class ChaptersPanel(ttk.LabelFrame):
    def __init__(
        self,
        master: tk.Tk,
        chapters: List[str],
        chapters_selection_action_functs: List[callable],
    ):
        super().__init__(master, text="Chapters")
        self._chapters = chapters
        self._chapter_selection_action_functs = chapters_selection_action_functs
        lb_height = 11
        self._lb = tk.Listbox(
            self, listvariable=tk.StringVar(value=chapters), width=75, height=lb_height
        )
        self._chapters_lb = self._lb
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid(sticky="NWES")
        self._lb.grid(column=0, row=0, sticky="nesw")
        sv = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._lb.yview)
        sv.grid(column=1, row=0, sticky="ns")
        self._lb["yscrollcommand"] = sv.set
        sh = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._lb.xview)
        sh.grid(column=0, row=1, sticky="ew")
        self._lb["xscrollcommand"] = sh.set
        self._lb.bind("<Return>", self.lb_selection_handler)
        self._lb.bind("<Button-3>", self.lb_right_button_handler)
        self._lb.bind("<Button-3>", self.lb_selection_handler, add="+")
        self.grid(padx=2, sticky="nsew")

    def set_chapters(self, chapters: List[str]):
        self._chapters_lb.delete(0, tk.END)
        self._chapters_lb.insert(tk.END, *chapters)

    def bind_chapters_selection_commands(
        self, chapters_selection_action_functs: List[callable]
    ):
        self._chapter_selection_action_functs = chapters_selection_action_functs

    def lb_right_button_handler(self, event):
        self._lb.selection_clear(0, tk.END)
        self._lb.focus_set()
        self._lb.selection_set(self._lb.nearest(event.y))
        self._lb.activate(self._lb.nearest(event.y))

    def lb_selection_handler(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self._chapter_selection_action_functs[index]()


def ignore_arguments(func):
    """A decorator function that ignores all arguments and calls a function
    without any parameters. Useful in cases when a function is called via a
    callback that expects to call the function with one or more parameters
    that the pre-existing function does not require."""

    def decorator(self, *args, **kwargs):
        func()

    return decorator


class PlayerControlPanel(ttk.LabelFrame):
    def __init__(self, root: tk.Tk):
        self._default_title = "Player Controls"
        super().__init__(root, text=self._default_title)
        self._root = root.winfo_toplevel()
        self.columnconfigure(9, weight=1)
        self.rowconfigure(0, weight=1)
        self._buttons = []
        self._buttons.append(ttk.Button(self, text="|<", width=3))
        self._buttons.append(ttk.Button(self, text="<<<", width=4))
        self._buttons.append(ttk.Button(self, text="<<", width=4))
        self._buttons.append(ttk.Button(self, text="<", width=4))
        self._buttons.append(ttk.Button(self, text="Play/Pause"))
        self._buttons.append(ttk.Button(self, text=">", width=4))
        self._buttons.append(ttk.Button(self, text=">>", width=4))
        self._buttons.append(ttk.Button(self, text=">>>", width=4))
        self._buttons.append(ttk.Button(self, text=">|", width=3))
        self._init_button_to_key_dict()
        n_buttons = len(self._buttons)
        for i in range(0, n_buttons):
            self._buttons[i].grid(row=0, column=i, padx=5, pady=5)
        self.grid(padx=2, pady=2, sticky="nesw")

    def _init_button_to_key_dict(self):
        self._button_to_key_dict = {
            "|<": "<Control-Shift-Left>",
            "<<<": "<Control-Left>",
            "<<": "<Shift-Left>",
            "<": "<Left>",
            "Play/Pause": "<p>",
            ">>>": "<Control-Right>",
            ">>": "<Shift-Right>",
            ">": "<Right>",
            ">|": "<Control-Shift-Right>",
        }

    def bind_player_controls_commands(self, player_controls_funcs: Dict[str, callable]):
        for button in self._buttons:
            button_name = button.cget("text")
            button.configure(command=player_controls_funcs[button_name])
            if button_name in self._button_to_key_dict:
                self._root.bind(
                    self._button_to_key_dict[button_name],
                    ignore_arguments(player_controls_funcs[button_name]),
                )

    def set_player_instance_name(self, instance_name: str):
        if instance_name:
            self.configure(text=f"{self._default_title} : {instance_name}")
        else:
            self.configure(text=self._default_title)


class AppMenuBar(tk.Menu):
    def __init__(self, main_window: tk.Tk):
        super().__init__()
        self._main_window = main_window
        self._main_window.config(menu=self)

        self._connection_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Player", menu=self._connection_menu, underline=0)

        self._themes_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Theme", menu=self._themes_menu, underline=0)

        self._chapters_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Load/Save", menu=self._chapters_menu, underline=0)

    def bind_connect_to_player_command(self, connect_player_command: callable):
        self._connection_menu.add_command(
            label="Select a player ...", command=connect_player_command, underline=0
        )

    def bind_save_chapters_file_command(self, save_chapters_file_command: callable):
        self._chapters_menu.add_command(
            label="Save chapters file ...",
            command=save_chapters_file_command,
            underline=0,
        )

    def bind_load_chapters_file_command(self, load_chapters_file_command: callable):
        self._chapters_menu.add_command(
            label="Load chapters file ...",
            command=load_chapters_file_command,
            underline=0,
        )

    def bind_load_chapters_from_youtube_command(
        self, load_chapters_from_youtube_command: callable
    ):
        self._chapters_menu.add_command(
            label="Load chapters from Youtube ...",
            command=load_chapters_from_youtube_command,
            underline=19,
        )

    def bind_theme_selection_command(self, load_theme_selection_command: callable):
        self._themes_menu.add_command(
            label="Select a theme ...",
            command=load_theme_selection_command,
            underline=0,
        )


class AppMainWindow(ttk.tk.Tk):
    """The main window for the application. In addation, this class implements a view
    protocol (AppInterface) as part of an MVP implementation"""

    def __init__(self):
        super().__init__(className="Chapters")
        self.geometry("625x310")
        ttk.Style("darkly")
        self.bind("<Escape>", self._handle_escape_pressed)
        self._default_title = "Chapters"
        self.title(self._default_title)
        icon.apply_icon(self)
        self.wm_title()
        self._menu_bar = AppMenuBar(self)
        self._chapters_place_panel = ttk.Frame(self)
        self._player_control_place_panel = ttk.Frame(self)
        self._chapters_listbox_items = []
        self._chapters_position_functions = []
        self._chapters_panel = ChaptersPanel(
            self._chapters_place_panel,
            chapters=self._chapters_listbox_items,
            chapters_selection_action_functs=self._chapters_position_functions,
        )
        self._player_control_panel = PlayerControlPanel(
            root=self._player_control_place_panel
        )
        # place the ChaptersPanel and PlayerControlPanel in the main window
        self._chapters_place_panel.place(relx=0, rely=0, relwidth=1, relheight=0.8)
        self._player_control_place_panel.place(
            relx=0, rely=0.8, relwidth=1, relheight=0.2
        )
        self._chapters_file_path = None
        self._supported_themes = self.get_themes()
        self._menu_bar.bind_theme_selection_command(self.select_theme)

    @property
    def menu_bar(self):
        return self._menu_bar

    @menu_bar.setter
    def menu_bar(self, menu_bar: AppMenuBar):
        self._menu_bar = menu_bar

    @property
    def chapters_panel(self):
        return self._chapters_panel

    @chapters_panel.setter
    def chapters_panel(self, chapters_panel: ChaptersPanel):
        self._chapters_panel = chapters_panel

    @property
    def player_control_panel(self):
        return self._player_control_panel

    @player_control_panel.setter
    def player_control_panel(self, player_control_panel: PlayerControlPanel):
        self._player_control_panel = player_control_panel

    def _handle_escape_pressed(self, event):
        self.destroy()

    def show_display(self):
        self.grid()
        self.resizable(width=False, height=False)
        self.mainloop()

    def set_main_window_title(self, media_title: str):
        if media_title:
            self.title(media_title)
        else:
            self.title(self._default_title)

    def get_themes(self):
        s = ttk.Style()
        return s.theme_names()

    def set_theme(self, theme_name: str):
        if theme_name:
            style = ttk.Style(theme=theme_name)
            style.theme_use(theme_name)
            self.update()

    def set_player_instance_name(self, instance_name: str):
        self._player_control_panel.set_player_instance_name(instance_name)

    def set_chapters(self, chapters: List[str]):
        self._chapters_panel.set_chapters(chapters=chapters)

    def set_chapters_file_path(self, chapters_file_path: str):
        self._chapters_file_path = chapters_file_path

    def bind_chapters_selection_commands(
        self, chapters_selection_action_functs: List[callable]
    ):
        self._chapters_panel.bind_chapters_selection_commands(
            chapters_selection_action_functs=chapters_selection_action_functs
        )

    def bind_player_controls_commands(self, player_controls_funcs: Dict[str, callable]):
        self._player_control_panel.bind_player_controls_commands(player_controls_funcs)

    def bind_connect_to_player_command(self, connect_player_command: callable):
        self._menu_bar.bind_connect_to_player_command(connect_player_command)

    def bind_save_chapters_file_command(self, save_chapters_file_command: callable):
        self._menu_bar.bind_save_chapters_file_command(save_chapters_file_command)

    def bind_load_chapters_file_command(self, load_chapters_file_command: callable):
        self._menu_bar.bind_load_chapters_file_command(load_chapters_file_command)

    def bind_load_chapters_from_youtube_command(
        self, load_chapters_from_youtube_command: callable
    ):
        self._menu_bar.bind_load_chapters_from_youtube_command(
            load_chapters_from_youtube_command
        )

    def bind_reload_chapters(self, reload_chapters: callable):
        self.bind("<F5>", reload_chapters)

    def bind_clear_chapters(self, clear_chapters: callable):
        self.bind("<Control-l>", clear_chapters)

    def bind_save_chapters(self, save_chapters: callable):
        self.bind("<Control-s>", save_chapters)

    def bind_select_player_shortcut(self, select_player: callable):
        self.bind("<s>", select_player)

    def request_save_chapters_file(
        self, default_filename: str = "chapters.ch"
    ) -> TextIO:
        if not self._chapters_file_path:
            self._chapters_file_path = f"{Path.home()}/Videos/Computing"
        if not Path(self._chapters_file_path).exists():
            self._chapters_file_path = f"{Path.home()}/Videos"
        if not Path(self._chapters_file_path).exists():
            self._chapters_file_path = f"{Path.home()}"
        selected_chapters_file = filedialog.asksaveasfile(
            initialdir=self._chapters_file_path,
            title="Select Chapters file",
            initialfile=default_filename,
        )
        if selected_chapters_file:
            dir = (Path(selected_chapters_file.name)).parent.absolute()
            self._chapters_file_path = str(dir)
        return selected_chapters_file

    def request_chapters_file(self) -> TextIO:
        if not self._chapters_file_path:
            self._chapters_file_path = f"{Path.home()}/Videos/Computing"
        if not Path(self._chapters_file_path).exists():
            self._chapters_file_path = f"{Path.home()}/Videos"
        if not Path(self._chapters_file_path).exists():
            self._chapters_file_path = f"{Path.home()}"
        selected_chapters_file = filedialog.askopenfile(
            initialdir=self._chapters_file_path,
            filetypes=(("chapters files", "*.ch"),),
        )
        if selected_chapters_file:
            dir = (Path(selected_chapters_file.name)).parent.absolute()
            self._chapters_file_path = str(dir)
        return selected_chapters_file

    def select_new_player(self, running_player_names: List[str]) -> str:
        self.popup = PlayerConnectionPopup(master=self)
        return self.popup.select_new_player_name(running_player_names)

    def get_youtube_video(self, url_str) -> str:
        self._yt_video_popup = YoutubeChaptersPopup(master=self)
        video = self._yt_video_popup.get_video(url_str)
        return video

    def select_theme(self) -> str:
        if not self._supported_themes:
            self._supported_themes = self.get_themes()
        self._theme_selection_popup = ThemeSelectionPopup(
            self, themes=self._supported_themes
        )
        self._selected_theme = self._theme_selection_popup.select_theme()
        self.set_theme(self._selected_theme)


class YoutubeChaptersPopup:
    def __init__(self, master: tk.Tk):
        self._video = ""
        self._master: tk.Tk = master
        self._video_name = tk.StringVar()
        self._video_name_return = ""

    def get_video(self, url_str) -> str:
        url_str = url_str if url_str else ""
        self._popup = tk.Toplevel(self._master)
        self._popup.title("Enter Youtube video id or url")
        self._create_video_entry_panel()
        self._video_name.set(url_str)
        self._popup.bind("<Return>", self._handle_enter_pressed)
        self._popup.bind("<Escape>", self._handle_escape_pressed)
        self._popup.bind("<Button-3>", self._handle_right_click_pressed)
        self._popup.resizable(width=False, height=False)
        self._popup.grid()
        # set to be on top of the main window
        self._popup.transient(self._master)
        # hijack all commands from the master (clicks on the main window are ignored)
        self._popup.grab_set()
        self._master.wait_window(
            self._popup
        )  # pause anything on the main window until this one closes
        return self._video_name_return

    def _create_video_entry_panel(self):
        self._input_panel = ttk.LabelFrame(
            master=self._popup, text="Youtube Video", width=50
        )
        self._video_name = tk.StringVar()
        self._video_name_entry = ttk.Entry(
            master=self._input_panel, textvariable=self._video_name
        )
        self._video_name_entry.grid(padx=5, pady=5)
        self._input_panel.grid(padx=5, pady=5)

        button_panel = ttk.Frame(master=self._popup)
        ok_button = ttk.Button(
            master=button_panel, text="OK", command=self._handle_ok_command
        )
        cancel_button = ttk.Button(
            master=button_panel, text="Cancel", command=self._handle_cancel_command
        )
        ok_button.grid(row=0, column=1, padx=10)
        cancel_button.grid(row=0, column=2, padx=10)
        ok_button.focus_force()
        button_panel.grid_columnconfigure(0, weight=1)
        button_panel.grid_rowconfigure(0, weight=1)
        button_panel.grid(padx=5, pady=5)

    def _handle_cancel_command(self):
        self._popup.destroy()

    def _handle_ok_command(self):
        self._video_name_return = self._video_name.get()
        self._popup.destroy()

    def _handle_enter_pressed(self, event):
        self._handle_ok_command()

    def _handle_escape_pressed(self, event):
        self._handle_cancel_command()

    def _handle_right_click_pressed(self, event):
        paste_text: str = self._master.clipboard_get()
        if paste_text:
            self._video_name.set(paste_text)


class PlayerConnectionPopup:
    def __init__(self, master: tk.Tk):
        self._master: tk.Tk = master
        self._selected_player_name: str = None

    def select_new_player_name(self, running_player_names: List[str]) -> str:
        self._popup = tk.Toplevel(self._master)
        self._popup.title("Connect to Player")
        self._popup.bind("<Return>", self._handle_enter_pressed)
        self._popup.bind("<Escape>", self._handle_escape_pressed)
        if not running_player_names:
            self._create_error_message_panel()
        else:
            self._create_players_selection_panel(running_player_names)
        self._popup.resizable(width=False, height=False)
        self._popup.grid()
        # set to be on top of the main window
        self._popup.transient(self._master)
        # hijack all commands from the master (clicks on the main window are ignored)
        self._popup.grab_set()
        # pause anything on the main window until this one closes
        self._master.wait_window(self._popup)
        return self._selected_player_name

    def _create_error_message_panel(self):
        message_panel = ttk.Frame(master=self._popup)
        message = ttk.Label(
            master=message_panel,
            text="No MPRIS enabled media players are currently running!",
        )
        ok_button = ttk.Button(
            master=message_panel, text="OK", command=self._handle_ok_command
        )
        message.grid(row=0, column=0, padx=5, pady=5)
        ok_button.grid(row=1, column=0, padx=10, pady=5)
        message_panel.grid()

    def _create_players_selection_panel(self, running_player_names: List[str]):
        players_panel = ttk.LabelFrame(master=self._popup, text="Players")
        lb_height = 5
        self._players_listbox = tk.Listbox(
            master=players_panel,
            listvariable=tk.StringVar(value=running_player_names),
            width=20,
            height=lb_height,
        )
        self._players_listbox.grid(column=0, row=0, sticky="NWES")
        self._players_listbox.select_set(0)
        sv = ttk.Scrollbar(
            players_panel, orient=tk.VERTICAL, command=self._players_listbox.yview
        )
        sv.grid(column=1, row=0, sticky="NS")
        self._players_listbox["yscrollcommand"] = sv.set
        sh = ttk.Scrollbar(
            players_panel, orient=tk.HORIZONTAL, command=self._players_listbox.xview
        )
        sh.grid(column=0, row=1, sticky="EW")
        self._players_listbox["xscrollcommand"] = sh.set
        players_panel.grid_columnconfigure(0, weight=1)
        players_panel.grid_rowconfigure(0, weight=1)
        players_panel.grid(padx=0, pady=5)

        button_panel = tk.Frame(master=self._popup)
        connect_button = ttk.Button(
            master=button_panel, text="Connect", command=self._handle_connect_command
        )
        cancel_button = ttk.Button(
            master=button_panel, text="Cancel", command=self._handle_cancel_command
        )
        connect_button.grid(row=0, column=1, padx=10)
        cancel_button.grid(row=0, column=2, padx=10)
        button_panel.grid_columnconfigure(0, weight=1)
        button_panel.grid_rowconfigure(0, weight=1)
        button_panel.grid(pady=10)
        self._players_listbox.focus_force()

    def _handle_connect_command(self):
        self._selected_player_name = self._players_listbox.get(tk.ACTIVE)
        self._popup.destroy()

    def _handle_cancel_command(self):
        self._selected_player = None
        self._popup.destroy()

    def _handle_ok_command(self):
        self._popup.destroy()

    def _handle_enter_pressed(self, event):
        self._handle_connect_command()

    def _handle_escape_pressed(self, event):
        self._handle_cancel_command()


class ThemeSelectionPopup:
    def __init__(self, master: tk.Tk, themes: List):
        self._master: tk.Tk = master
        self._supported_themes: List = themes
        self._selected_theme: str = None

    def select_theme(self) -> str:
        self._popup = tk.Toplevel(self._master)
        self._popup.title("Select a Theme")
        self._popup.bind("<Return>", self._handle_enter_pressed)
        self._popup.bind("<Escape>", self._handle_escape_pressed)
        self._create_theme_selection_panel()
        self._popup.resizable(width=False, height=False)
        self._popup.grid()
        # set to be on top of the main window
        self._popup.transient(self._master)
        # hijack all commands from the master (clicks on the main window are ignored)
        self._popup.grab_set()
        self._master.wait_window(
            self._popup
        )  # pause anything on the main window until this one closes
        return self._selected_theme

    def _create_theme_selection_panel(self):
        themes_panel = ttk.LabelFrame(master=self._popup, text="Themes")
        lb_height = 5
        self._themes_listbox = tk.Listbox(
            master=themes_panel,
            listvariable=tk.StringVar(value=self._supported_themes),
            width=20,
            height=lb_height,
        )
        self._themes_listbox.grid(column=0, row=0, sticky="NWES")
        self._themes_listbox.select_set(0)
        sv = ttk.Scrollbar(
            themes_panel, orient=tk.VERTICAL, command=self._themes_listbox.yview
        )
        sv.grid(column=1, row=0, sticky="NS")
        self._themes_listbox["yscrollcommand"] = sv.set
        sh = ttk.Scrollbar(
            themes_panel, orient=tk.HORIZONTAL, command=self._themes_listbox.xview
        )
        sh.grid(column=0, row=1, sticky="EW")
        self._themes_listbox["xscrollcommand"] = sh.set
        themes_panel.grid_columnconfigure(0, weight=1)
        themes_panel.grid_rowconfigure(0, weight=1)
        themes_panel.grid(padx=0, pady=5)

        button_panel = tk.Frame(master=self._popup)
        connect_button = ttk.Button(
            master=button_panel, text="Select", command=self._handle_selection_command
        )
        cancel_button = ttk.Button(
            master=button_panel, text="Cancel", command=self._handle_cancel_command
        )
        connect_button.grid(row=0, column=1, padx=10)
        cancel_button.grid(row=0, column=2, padx=10)
        button_panel.grid_columnconfigure(0, weight=1)
        button_panel.grid_rowconfigure(0, weight=1)
        button_panel.grid(pady=10)
        connect_button.focus_force()

    def _handle_selection_command(self):
        self._selected_theme = self._themes_listbox.get(tk.ACTIVE)
        self._popup.destroy()

    def _handle_cancel_command(self):
        self._selected_theme = None
        self._popup.destroy()

    def _handle_ok_command(self):
        self._popup.destroy()

    def _handle_enter_pressed(self, event):
        self._handle_selection_command()

    def _handle_escape_pressed(self, event):
        self._handle_cancel_command()
