from typing import List, Dict, Protocol, TextIO, Tuple
from chapters import helpers
from chapters.mpris_player import Player
from chapters.mpris_player import PlayerFactory, PlayerCreationError
from chapters.mpris_player import PlayerProxy
from chapters.chapters_help import keyboard_shortcuts_help
from chapters.logger_config import logger


def ignore_inst_method_args(func):
    """A decorator function that ignores all arguments sent to class instance's
    method and calls the instance method with only the default 'self' argument.
    Useful in cases when a class' instance method is called via a
    callback, with the expecation that the callback accepts one or more parameters.
    """

    def decorator(self, *args, **kwargs):
        func(self)

    return decorator


class AppGuiBuilderInterface(Protocol):
    def create_menu_bar_bindings(self): ...

    def create_chapters_panel_bindings(
        self, chapters_title: str, chapters: Dict[str, str]
    ): ...

    def create_player_control_panel_bindings(self): ...


class GuiAppInterface(Protocol):
    def set_main_window_title(self, media_title: str): ...

    def request_chapters_file(self) -> TextIO: ...

    def request_save_chapters_file(self, default_filename: str = "ch.ch") -> TextIO: ...

    def get_youtube_video(self, url_str) -> str: ...

    def get_chapter_details(
        self, chapter_name: str = "", chapter_timestamp: str = ""
    ) -> List[str]: ...

    def get_jump_to_position_timestamp(self) -> str: ...

    def request_chapter_title(self, title: str = "") -> str: ...

    def set_chapters(self, chapters: List[str]): ...

    def set_chapters_file_path(self, chapters_file_path: str): ...

    def set_player_instance_name(self, instance_name): ...

    def bind_chapters_selection_commands(
        self, chapters_selection_action_functs: List[callable]
    ): ...

    def bind_player_controls_commands(
        self, player_controls_funcs: Dict[str, callable]
    ): ...

    def bind_connect_to_player_command(self, connect_player_command: callable): ...

    def select_new_player(self) -> Player: ...

    def bind_load_chapters_command(self, load_chapters_file_command: callable): ...

    def bind_save_chapters_command(self, load_chapters_file_command: callable): ...

    def bind_reload_chapters(self, reload_chapters: callable): ...

    def bind_clear_chapters(self, clear_chapters: callable): ...

    def bind_raise_player_window(self, raise_player_window: callable): ...

    def show_error_message(self, message: str) -> None: ...

    def show_info_message(self, message: str) -> None: ...

    def show_help(self, content: str) -> None: ...

    def show_display(self): ...

    def exit_application(self): ...


def handle_player_error(func: callable):
    def decorator(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except Exception as e:
            logger().error("An error occured when attempting to call the player")
            logger().error(type(e))
            self._view.show_error_message(
                "An error occurred in the currently connected player.\n"
                "Kindly try reconnecting or disconnecting to avoid this error message"
            )

    return decorator


class GuiController:
    def __init__(
        self,
        view: GuiAppInterface,
        app_gui_builder: AppGuiBuilderInterface,
    ):
        self._view: GuiAppInterface = view
        self._gui_builder: AppGuiBuilderInterface = app_gui_builder
        player = self._get_sole_running_player()
        if player:
            self.cur_player = player
        else:
            self.cur_player = PlayerProxy(None)
        self._initialise_chapters_content()

    def _get_sole_running_player(self) -> Player:
        running_players = PlayerFactory.get_running_player_names()
        player: Player = None
        if len(running_players) == 1:
            player_names = list(running_players.keys())
            selected_player_name = player_names[0]
            selected_player_fq_name = running_players[selected_player_name]
            logger().debug("Creating player")
            try:
                player = PlayerFactory.get_player(
                    selected_player_fq_name, selected_player_name
                )
            except PlayerCreationError as e:
                logger().error(e)
            else:
                logger().debug("Created player")
        return player

    def _initialise_chapters_content(self):
        self._chapters_filename: str = None
        self._chapters_yt_video: str = None
        self._chapters_title: str = None
        self._chapters: Dict[str, str] = {}

    @property
    def cur_player(self):
        return self._cur_player

    @cur_player.setter
    def cur_player(self, player: Player):
        self._cur_player = player
        self._view.set_player_instance_name(player.ext_name)

    def set_chapters_filename(self, filename: str):
        self._chapters_filename = filename

    def set_chapters_yt_video(self, video: str):
        self._chapters_yt_video = video

    def chapters_listbox_selection_handler(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self._chapter_selection_action_functs[index]()

    @handle_player_error
    def set_player_position(self, position: str):
        self._cur_player.set_position(helpers.to_microsecs(position))

    @handle_player_error
    def skip_player(
        self, offset: str, direction: helpers.Direction = helpers.Direction.FORWARD
    ):
        offset_with_dir = helpers.to_microsecs(offset) * direction
        self._cur_player.seek(offset_with_dir)

    @handle_player_error
    def play_pause_player(self):
        self._cur_player.play_pause()

    @handle_player_error
    def next_player(self):
        self._cur_player.next()

    @handle_player_error
    def previous_player(self):
        self._cur_player.previous()

    @handle_player_error
    @ignore_inst_method_args
    def raise_player_window(self):
        self._cur_player.raise_window()

    def handle_disconnection_command(self, event=None):
        self._cur_player = PlayerProxy(None)
        self._view.set_player_instance_name(None)

    def handle_connection_command(self, event=None):
        running_player_names = PlayerFactory.get_running_player_names()
        new_player_name = self._view.select_new_player(
            list(running_player_names.keys())
        )
        if new_player_name:
            try:
                self._cur_player = PlayerFactory.get_player(
                    running_player_names[new_player_name], new_player_name
                )
                self._view.set_player_instance_name(new_player_name)
            except PlayerCreationError as e:
                logger().error(e)

    def handle_raise_player_window_command(self, event=None):
        self.raise_player_window()

    def load_chapters_file(
        self, chapters_file: str | TextIO
    ) -> Tuple[str, Dict[str, str]]:
        if chapters_file:
            try:
                self._chapters_title, self._chapters = helpers.load_chapters_file(
                    chapters_file
                )
            except (FileNotFoundError, ValueError) as e:
                logger().error(e)
                self._view.show_error_message(
                    f"An error occurred when attempting to load {chapters_file.name}.\n"
                    "Kindly ensure the file exists and is in the correct format.\n"
                    "Check the log output for more details."
                )
        return self._chapters_title, self._chapters

    def handle_save_chapters_file_command(self, even=None):
        suggested_filename = helpers.get_valid_filename(f"{self._chapters_title}.ch")
        chapters_file = self._view.request_save_chapters_file(
            default_filename=suggested_filename
        )
        if not chapters_file:
            return
        self._chapters_filename = chapters_file.name
        helpers.save_chapters_file(chapters_file, self._chapters_title, self._chapters)

    def handle_load_chapters_file_command(self, event=None):
        chapters_file = self._view.request_chapters_file()
        if not chapters_file:
            return
        self._chapters_filename = chapters_file.name
        self.load_chapters_file(chapters_file)
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def _load_chapters_from_youtube(self, gui_prompt: bool):
        video_name = helpers.get_url_from_clipboard()
        if gui_prompt:
            video_name = self._view.get_youtube_video(video_name)
        if not video_name:
            return
        video_name = video_name.strip()
        if not video_name:
            return
        self.set_chapters_yt_video(video_name)
        try:
            self._chapters_title, self._chapters = helpers.load_chapters_from_youtube(
                video=self._chapters_yt_video
            )
        except Exception as e:
            logger().error(e)
            self._view.show_error_message(
                "An error occurred when attempting retrieve chapters from:\n"
                f"{video_name}\n"
                "Kindly ensure the secified video exists and is correctly specified\n"
                "Check the log output for more details."
            )
            return
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def handle_load_chapters_from_youtube(self, event=None):
        self._load_chapters_from_youtube(gui_prompt=True)

    def handle_load_chapters_from_youtube_no_prompt(self, event=None):
        self._load_chapters_from_youtube(gui_prompt=False)

    def _update_chapter_details(
        self, suggested_chapter_name: str, suggestd_chapter_timestamp: str
    ) -> tuple[str, str]:
        chapter_name, chapter_timestamp = (
            suggested_chapter_name,
            suggestd_chapter_timestamp,
        )
        while True:
            chapter_name, chapter_timestamp = self._view.get_chapter_details(
                chapter_name=chapter_name, chapter_timestamp=chapter_timestamp
            )
            if not chapter_name and not chapter_timestamp:
                break
            if not chapter_name:
                self._view.show_error_message("Chapter name cannot be empty")
                continue
            if not chapter_timestamp:
                self._view.show_error_message("Chapter timestamp cannot be empty")
                continue
            # Convert the timestamp to an int to check for validity
            try:
                helpers.to_microsecs(chapter_timestamp)
            except ValueError:
                self._view.show_error_message(
                    f"Invalid timestamp {chapter_timestamp} for chapter {chapter_name}"
                )
                continue
            break
        return chapter_name, chapter_timestamp

    def handle_insert_chapter(self, event=None):
        cur_position = 0
        try:
            cur_position = self._cur_player.position
        except Exception as e:
            logger().warning("Unable to get player position")
            logger().warning(e)
            self._view.show_error_message(
                "An error occurred in the currently connected player.\n"
                "Kindly try reconnecting or disconnecting to avoid this error message"
            )
        # Set the current position to 0 when no player is connected
        # When no player is connected, the default "empty" PlayerProxy returns None
        # for the position
        if not cur_position:
            cur_position = 0

        chapter_timestamp = helpers.to_HHMMSS(cur_position)
        chapter_name = ""
        chapter_name, chapter_timestamp = self._update_chapter_details(
            chapter_name, chapter_timestamp
        )
        if not chapter_name and not chapter_timestamp:
            return
        self._chapters[chapter_name] = chapter_timestamp
        self._chapters = helpers.sort_chapters_on_time(self._chapters)
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def handle_delete_chapter(self, event=None):
        selected_chapter_index = self._view.get_selected_chapter_index()
        if selected_chapter_index is None:
            return
        del self._chapters[list(self._chapters.keys())[selected_chapter_index]]
        self._chapters = helpers.sort_chapters_on_time(self._chapters)
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def handle_edit_chapter(self, event=None):
        selected_chapter_index = self._view.get_selected_chapter_index()
        if selected_chapter_index is None:
            self._view.show_info_message(
                "No chapter selected. Select a chapter to edit."
            )
            return
        chapters_list = list(self._chapters.items())
        chapter_name, chapter_timestamp = chapters_list[selected_chapter_index]
        chapter_name, chapter_timestamp = self._update_chapter_details(
            suggested_chapter_name=chapter_name,
            suggestd_chapter_timestamp=chapter_timestamp,
        )
        if not chapter_name and not chapter_timestamp:
            return
        if chapter_name in self._chapters:
            self._chapters[chapter_name] = chapter_timestamp
        else:
            chapters_list[selected_chapter_index] = (chapter_name, chapter_timestamp)
            self._chapters = dict(chapters_list)
        self._chapters = helpers.sort_chapters_on_time(self._chapters)
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def handle_jump_to_position(self, event=None):
        position_timestamp = "00:00:00"
        while True:
            position_timestamp = self._view.get_jump_to_position_timestamp()
            if position_timestamp is None:
                return
            if position_timestamp == "":
                self._view.show_error_message("Position timestamp cannot be empty")
                continue
            # Convert the timestamp to an int to check for validity
            try:
                helpers.to_microsecs(position_timestamp)
            except ValueError:
                self._view.show_error_message(f"Invalid timestamp {position_timestamp}")
                continue
            self.set_player_position(position_timestamp)
            break

    def handle_reload_chapters(self, event=None):
        if self._chapters_filename:
            self.load_chapters_file(self._chapters_filename)
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def handle_clear_chapters(self, event=None):
        self._initialise_chapters_content()
        self._gui_builder.create_chapters_panel_bindings()

    def handle_new_title(self, event=None):
        title = self._view.request_chapter_title()
        if not title:
            return
        self._initialise_chapters_content()
        self._chapters_title = title
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def handle_edit_title(self, event=None):
        title = self._view.request_chapter_title(title=self._chapters_title)
        if not title:
            return
        self._chapters_title = title
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def handle_show_keyboard_shortcuts_help(self, event=None):
        self._view.show_help(content=keyboard_shortcuts_help)

    def handle_exit_application_command(self, event=None):
        self._view.exit_application()
