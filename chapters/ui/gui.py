import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import ttkbootstrap as ttk
import chapters.ui.ch_icon as icon
from chapters.ui.gui_popups import (
    EntryFieldsPopup,
    ListSelectionPopup,
    MessagePopup,
    ErrorMessagePopup,
    InfoMessagePopup,
    HelpPopup,
)
from typing import List, Dict, TextIO
from chapters.logger_config import logger


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
        # Create a vertical scrollbar
        vertical_scrollbar = ttk.Scrollbar(self)
        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create a horizontal scrollbar
        horizontal_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        lb_height = 11
        self._chapters_lb = tk.Listbox(
            self,
            listvariable=tk.StringVar(value=chapters),
            height=lb_height,
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )
        self._chapters_lb.pack(fill=tk.BOTH, expand=True)
        self.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Configure the scrollbars to control the listbox
        vertical_scrollbar.config(command=self._chapters_lb.yview)
        horizontal_scrollbar.config(command=self._chapters_lb.xview)

        # Key Bindings
        self._chapters_lb.bind("<Return>", self.lb_selection_handler)
        self._chapters_lb.bind("<KP_Enter>", self.lb_selection_handler)
        self._chapters_lb.bind("<Button-3>", self.lb_right_button_handler)
        self._chapters_lb.bind("<Button-3>", self.lb_selection_handler, add="+")

    def set_chapters(self, chapters: List[str]):
        self._chapters_lb.delete(0, tk.END)
        self._chapters_lb.insert(tk.END, *chapters)
        # self._chapters_lb.selection_clear(0, tk.END)
        # self._chapters_lb.selection_set(0)

    def bind_chapters_selection_commands(
        self, chapters_selection_action_functs: List[callable]
    ):
        self._chapter_selection_action_functs = chapters_selection_action_functs

    def lb_right_button_handler(self, event):
        self._chapters_lb.selection_clear(0, tk.END)
        self._chapters_lb.focus_set()
        self._chapters_lb.selection_set(self._chapters_lb.nearest(event.y))
        self._chapters_lb.activate(self._chapters_lb.nearest(event.y))

    def lb_selection_handler(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self._chapter_selection_action_functs[index]()

    def get_selected_chapter_index(self) -> int | None:
        selected_indices = self._chapters_lb.curselection()
        if selected_indices:
            # Return the first (and only) selected index
            return selected_indices[0]
        return None

    def set_selected_chapter_index(self, index: int):
        self._chapters_lb.select_set(index)
        self._chapters_lb.activate(index)
        self._chapters_lb.see(index)


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
            self._buttons[i].grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.columnconfigure(i, weight=1)
        self.pack(fill=tk.X, padx=5, pady=5, expand=True)

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
        self._alt_button_to_key_dict = {
            "|<": "<Control-Shift-less>",
            "<<<": "<Control-comma>",
            "<<": "<Shift-less>",
            "<": "<comma>",
            ">>>": "<Control-period>",
            ">>": "<Shift-greater>",
            ">": "<period>",
            ">|": "<Control-Shift-greater>",
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
            if button_name in self._alt_button_to_key_dict:
                self._root.bind(
                    self._alt_button_to_key_dict[button_name],
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

        self._chapters_file_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="File", menu=self._chapters_file_menu, underline=0)

        self._connection_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Player", menu=self._connection_menu, underline=0)

        self._chapters_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Chapters", menu=self._chapters_menu, underline=0)

        self._themes_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Theme", menu=self._themes_menu, underline=0)

        self._help_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Help", menu=self._help_menu, underline=0)

    # Define menu bindings

    def bind_new_title_command(self, new_title_command: callable):
        self._chapters_menu.add_command(
            label="New Title",
            command=new_title_command,
            underline=0,
        )

    def bind_edit_title_command(self, edit_title_command: callable):
        self._chapters_menu.add_command(
            label="Edit Title",
            command=edit_title_command,
            underline=1,
        )

    def bind_insert_chapter_command(self, insert_chapter_command: callable):
        self._chapters_menu.add_command(
            label="Insert Chapter",
            command=insert_chapter_command,
            underline=0,
        )

    def bind_edit_chapter_command(self, edit_chapter_command: callable):
        self._chapters_menu.add_command(
            label="Edit Chapter",
            command=edit_chapter_command,
            underline=0,
        )

    def bind_delete_chapter_command(self, delete_chapter_command: callable):
        self._chapters_menu.add_command(
            label="Delete Chapter",
            command=delete_chapter_command,
            underline=0,
        )

    def bind_clear_all_command(self, clear_chapters_command: callable):
        self._chapters_menu.add_command(
            label="Clear All",
            command=clear_chapters_command,
            underline=0,
        )

    def bind_recent_chapters_command(self, recent_chapters_command: callable):
        self._chapters_menu.add_command(
            label="Recent Chapters",
            command=recent_chapters_command,
            underline=0,
        )

    def bind_save_chapters_file_command(self, save_chapters_file_command: callable):
        self._chapters_file_menu.add_command(
            label="Save Chapters File ...",
            command=save_chapters_file_command,
            underline=0,
        )

    def bind_load_chapters_file_command(self, load_chapters_file_command: callable):
        self._chapters_file_menu.add_command(
            label="Load Chapters File ...",
            command=load_chapters_file_command,
            underline=0,
        )

    def bind_reload_chapters_file_command(self, reload_chapters_file_command: callable):
        self._chapters_file_menu.add_command(
            label="Reload Current File",
            command=reload_chapters_file_command,
            underline=0,
        )

    def bind_load_chapters_from_youtube_command(
        self, load_chapters_from_youtube_command: callable
    ):
        self._chapters_file_menu.add_command(
            label="Load Chapters From YouTube ...",
            command=load_chapters_from_youtube_command,
            underline=19,
        )

    def bind_exit_application_command(self, exit_application_command: callable):
        self._chapters_file_menu.add_command(
            label="Exit",
            command=exit_application_command,
            underline=1,
        )

    def bind_show_keyboard_shortcuts_help_command(
        self, show_keyboard_shortcuts_help_command: callable
    ):
        self._help_menu.add_command(
            label="Keyboard Shortcuts",
            command=show_keyboard_shortcuts_help_command,
            underline=0,
        )

    def bind_show_overview_help_command(self, show_overview_help_command: callable):
        self._help_menu.add_command(
            label="Overview",
            command=show_overview_help_command,
            underline=0,
        )

    def bind_show_about_help_command(self, show_about_help_command: callable):
        self._help_menu.add_command(
            label="About",
            command=show_about_help_command,
            underline=0,
        )

    def bind_theme_selection_command(self, load_theme_selection_command: callable):
        self._themes_menu.add_command(
            label="Select a theme ...",
            command=load_theme_selection_command,
            underline=0,
        )

    def bind_connect_to_player_command(self, connect_player_command: callable):
        self._connection_menu.add_command(
            label="Connect ...", command=connect_player_command, underline=0
        )

    def bind_disconnect_player_command(self, disconnect_player_command: callable):
        self._connection_menu.add_command(
            label="Disconnect", command=disconnect_player_command, underline=0
        )

    def bind_jump_to_position_player_command(
        self, jump_to_position_player_command: callable
    ):
        self._connection_menu.add_command(
            label="Jump To Position",
            command=jump_to_position_player_command,
            underline=0,
        )

    def bind_raise_player_window_command(self, raise_player_window_command: callable):
        self._connection_menu.add_command(
            label="Raise Player Window",
            command=raise_player_window_command,
            underline=0,
        )


class AppMainWindow(ttk.tk.Tk):
    """The main window for the application. In addation, this class implements a view
    protocol (AppInterface) as part of an MVP implementation"""

    def __init__(self):
        super().__init__(className="Chapters")
        self.minsize(width=625, height=340)
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
        self._chapters_place_panel.grid(row=0, column=0, sticky="nsew")
        self._player_control_place_panel.grid(row=1, column=0, sticky="nsew")
        self._chapters_file_path = None
        self._supported_themes = self.get_themes()
        self._menu_bar.bind_theme_selection_command(self.select_theme)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=4)
        self.grid_rowconfigure(1, weight=1)
        self.grid()
        self.resizable(width=True, height=True)

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
        self.exit_application()

    def exit_application(self):
        logger().debug("Destroying Main Window")
        self.destroy()

    def show_display(self):
        logger().debug("Displaying Main Window")
        self.mainloop()

    def set_main_window_title(self, media_title: str):
        if media_title:
            self.title(media_title)
        else:
            self.title(self._default_title)

    def get_themes(self):
        s = ttk.Style()
        themes = s.theme_names()
        sorted_themes = list(themes)
        sorted_themes.sort()
        return sorted_themes

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

    # Menu bar bindings

    def bind_load_chapters_file_command(self, load_chapters_file_command: callable):
        self._menu_bar.bind_load_chapters_file_command(load_chapters_file_command)
        self.bind("<Control-f>", load_chapters_file_command)

    def bind_reload_chapters_file_command(self, reload_chapters_file_command: callable):
        self._menu_bar.bind_reload_chapters_file_command(reload_chapters_file_command)
        self.bind("<F5>", reload_chapters_file_command)

    def bind_load_chapters_from_youtube_command(
        self, load_chapters_from_youtube_command: callable
    ):
        self._menu_bar.bind_load_chapters_from_youtube_command(
            load_chapters_from_youtube_command
        )
        self.bind("<Control-y>", load_chapters_from_youtube_command)

    def bind_load_chapters_from_youtube_no_prompt_command(
        self, load_chapters_from_youtube_no_prompt_command: callable
    ):
        self.bind("<Control-Shift-Y>", load_chapters_from_youtube_no_prompt_command)

    def bind_save_chapters_file_command(self, save_chapters_file_command: callable):
        self._menu_bar.bind_save_chapters_file_command(save_chapters_file_command)
        self.bind("<Control-s>", save_chapters_file_command)

    def bind_new_title_command(self, new_title_command: callable):
        self._menu_bar.bind_new_title_command(new_title_command)
        self.bind("<Control-n>", new_title_command)

    def bind_edit_title_command(self, edit_title_command: callable):
        self._menu_bar.bind_edit_title_command(edit_title_command)
        self.bind("<Control-e>", edit_title_command)

    def bind_insert_chapter_command(self, insert_chapter_command: callable):
        self._menu_bar.bind_insert_chapter_command(insert_chapter_command)
        self.bind("<Control-i>", insert_chapter_command)

    def bind_edit_chapter_command(self, edit_chapter_command: callable):
        self._menu_bar.bind_edit_chapter_command(edit_chapter_command)
        self.bind("<F2>", edit_chapter_command)

    def bind_delete_chapter_command(self, delete_chapter_command: callable):
        self._menu_bar.bind_delete_chapter_command(delete_chapter_command)
        self.bind("<Delete>", delete_chapter_command)

    def bind_clear_all_command(self, clear_chapters: callable):
        self._menu_bar.bind_clear_all_command(clear_chapters)
        self.bind("<Control-l>", clear_chapters)

    def bind_recent_chapters_command(self, recent_chapters_command: callable):
        self._menu_bar.bind_recent_chapters_command(recent_chapters_command)

    def bind_next_chapters_command(self, next_chapters_command: callable):
        self.bind("<Control-n>", next_chapters_command)

    def bind_connect_to_player_command(self, connect_player_command: callable):
        self._menu_bar.bind_connect_to_player_command(connect_player_command)
        self.bind("<c>", connect_player_command)

    def bind_connect_to_next_player_command(
        self, connect_next_player_command: callable
    ):
        self.bind("<n>", connect_next_player_command)

    def bind_disconnect_player_command(self, disconnect_player_command: callable):
        self._menu_bar.bind_disconnect_player_command(disconnect_player_command)
        self.bind("<d>", disconnect_player_command)

    def bind_jump_to_position_player_command(
        self, jump_to_position_player_command: callable
    ):
        self._menu_bar.bind_jump_to_position_player_command(
            jump_to_position_player_command
        )
        self.bind("<Control-j>", jump_to_position_player_command)

    def bind_raise_player_window_command(self, raise_player_window_command: callable):
        self._menu_bar.bind_raise_player_window_command(raise_player_window_command)
        self.bind("<f>", raise_player_window_command)

    def bind_show_keyboard_shortcuts_help_command(
        self, show_keyboard_shortcuts_help_command: callable
    ):
        self._menu_bar.bind_show_keyboard_shortcuts_help_command(
            show_keyboard_shortcuts_help_command
        )

    def bind_show_overview_help_command(self, show_overview_help_command: callable):
        self._menu_bar.bind_show_overview_help_command(show_overview_help_command)

    def bind_show_about_help_command(self, show_about_help_command: callable):
        self._menu_bar.bind_show_about_help_command(show_about_help_command)

    def bind_exit_application_command(self, exit_application_command: callable):
        self._menu_bar.bind_exit_application_command(exit_application_command)

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
            filetypes=(("chapters files", "*.ch"),),
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
        if not running_player_names:
            msg_popup = MessagePopup(
                master=self,
                title="Connect to Player",
                message_content_description="Message",
                message_content="No MPRIS enabled media players are currently running!",
            )
            msg_popup.show_message()
            return
        self.popup = PlayerConnectionPopup(
            master=self, running_player_names=running_player_names
        )
        return self.popup.select_new_player_name()

    def select_recent_chapters(self, recent_chapters: List[str]) -> str:
        if not recent_chapters:
            msg_popup = MessagePopup(
                master=self,
                title="Select Recent Chapters",
                message_content_description="Message",
                message_content="No recent chapters found!",
            )
            msg_popup.show_message()
            return
        popup = RecentChaptersPopup(master=self, recent_chapters=recent_chapters)
        return popup.select_recent_chapters_title()

    def get_youtube_video(self, url_str) -> str:
        self._yt_video_popup = YoutubeChaptersPopup(master=self, video_url=url_str)
        video = self._yt_video_popup.get_video()
        return video

    def get_jump_to_position_timestamp(self) -> str:
        jump_to_position_popup = JumpToPositionPopup(master=self)
        return jump_to_position_popup.get_jump_to_position_timestamp()

    def request_chapter_title(self, title: str = "") -> str:
        self._title_popup = ChapterTitlePopup(master=self, title=title)
        return self._title_popup.get_response()

    def get_chapter_details(
        self, chapter_name: str = "", chapter_timestamp: str = ""
    ) -> List[str]:
        chapter_details_popup = ChapterDetailsPopup(
            master=self, chapter_name=chapter_name, chapter_timestamp=chapter_timestamp
        )
        chapter_detials = chapter_details_popup.get_chapter_details()
        chapter_name, chapter_timestamp = (
            chapter_detials if chapter_detials else (None, None)
        )
        return chapter_name, chapter_timestamp

    def get_selected_chapter_index(self) -> int:
        return self._chapters_panel.get_selected_chapter_index()

    def set_selected_chapter_index(self, index: int):
        self._chapters_panel.set_selected_chapter_index(index)

    def select_theme(self) -> str:
        if not self._supported_themes:
            self._supported_themes = self.get_themes()
        self._theme_selection_popup = ThemeSelectionPopup(
            self, themes=self._supported_themes
        )
        self._selected_theme = self._theme_selection_popup.select_theme()
        self.set_theme(self._selected_theme)

    def show_error_message(self, message: str) -> None:
        error_message_popup = ErrorMessagePopup(master=self)
        error_message_popup.show_message(message)

    def show_info_message(self, message: str) -> None:
        error_message_popup = InfoMessagePopup(master=self)
        error_message_popup.show_message(message)

    def show_help(self, content: str, view_dimensions: str) -> None:
        help_popup = HelpPopup(
            master=self, help_content=content, help_view_dimensions=view_dimensions
        )
        help_popup.show_help()


class YoutubeChaptersPopup:
    def __init__(self, master: tk.Tk, video_url: str = ""):
        self._popup = EntryFieldsPopup(
            master=master,
            popup_title="Enter Youtube video id",
            input_fields_parameters=[["Youtube Video", video_url]],
        )

    def get_video(self) -> str:
        response = self._popup.get_response()
        return response[0] if response else None


class PlayerConnectionPopup:
    def __init__(self, master: tk.Tk, running_player_names: List[str] = []):
        self._title = "Connect to Player"
        self._popup = ListSelectionPopup(
            master=master,
            popup_title=self._title,
            listbox_title="Players",
            listbox_items=running_player_names,
        )

    def select_new_player_name(self) -> str | None:
        return self._popup.get_response()


class RecentChaptersPopup:
    def __init__(self, master: tk.Tk, recent_chapters: List[str] = []):
        self._title = "Select Recent Chapters"
        self._popup = ListSelectionPopup(
            master=master,
            popup_title=self._title,
            listbox_title="Recent Chapters",
            listbox_items=recent_chapters,
            listbox_width=50,
        )

    def select_recent_chapters_title(self) -> str | None:
        return self._popup.get_response()


class ThemeSelectionPopup:
    def __init__(self, master: tk.Tk, themes: List):
        self._popup = ListSelectionPopup(
            master=master,
            popup_title="Select a Theme",
            listbox_title="Themes",
            listbox_items=themes,
        )

    def select_theme(self) -> str:
        return self._popup.get_response()


class ChapterDetailsPopup:
    def __init__(
        self, master: tk.Tk, chapter_name: str = "", chapter_timestamp: str = ""
    ):
        self._popup = EntryFieldsPopup(
            master=master,
            popup_title="Enter Chapter Details",
            input_fields_parameters=[
                ["Name", chapter_name],
                ["Time Offset", chapter_timestamp],
            ],
        )

    def get_chapter_details(self) -> List[str]:
        return self._popup.get_response()


class ChapterTitlePopup:
    def __init__(self, master: tk.Tk, title: str = ""):
        self._popup = EntryFieldsPopup(
            master=master,
            popup_title="Title",
            input_fields_parameters=[["Title Name", title]],
        )

    def get_response(self) -> str:
        response = self._popup.get_response()
        return response[0] if response else None


class JumpToPositionPopup:
    def __init__(self, master: tk.Tk):
        self._popup = EntryFieldsPopup(
            master=master,
            popup_title="Jump To Position",
            input_fields_parameters=[["Time Offset", "00:00:00"]],
        )

    def get_jump_to_position_timestamp(self) -> str:
        response = self._popup.get_response()
        return response[0] if response else None
