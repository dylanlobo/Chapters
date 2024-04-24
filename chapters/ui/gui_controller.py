from typing import List, Dict, Protocol, TextIO, Tuple
from chapters import helpers
from chapters.mpris_player import Player
from chapters.mpris_player import PlayerFactory, PlayerCreationError
from chapters.mpris_player import PlayerProxy
from chapters.logger_config import logger


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

    def show_display(self): ...


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
        self._initialiase_chapters_content()

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

    def _initialiase_chapters_content(self):
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

    def _load_chapters_from_youtube(self):
        try:
            self._chapters_title, self._chapters = helpers.load_chapters_from_youtube(
                video=self._chapters_yt_video
            )
        except Exception as e:
            logger().error(e)
            raise e

    def chapters_listbox_selection_handler(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self._chapter_selection_action_functs[index]()

    def set_player_position(self, position: str):
        self._cur_player.set_position(helpers.to_microsecs(position))

    def skip_player(
        self, offset: str, direction: helpers.Direction = helpers.Direction.FORWARD
    ):
        offset_with_dir = helpers.to_microsecs(offset) * direction
        self._cur_player.seek(offset_with_dir)

    def play_pause_player(self):
        self._cur_player.play_pause()

    def next_player(self):
        self._cur_player.next()

    def previous_player(self):
        self._cur_player.previous()

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
                # TODO Implement and make call to view object to display error
                # message popup before returning
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

    def handle_load_chapters_file_command(self):
        chapters_file = self._view.request_chapters_file()
        if not chapters_file:
            return
        self._chapters_filename = chapters_file.name
        self.load_chapters_file(chapters_file)
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def handle_load_chapters_from_youtube(self):
        url_str = helpers.get_url_from_clipboard()
        video_name = self._view.get_youtube_video(url_str)
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
            # TODO Implement and make call to view object to display error
            # message popup before returning
            return
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def handle_reload_chapters(self, event):
        if self._chapters_filename:
            self.load_chapters_file(self._chapters_filename)
        self._gui_builder.create_chapters_panel_bindings(
            self._chapters_title, self._chapters
        )

    def handle_clear_chapters(self, event):
        self._initialiase_chapters_content()
        self._gui_builder.create_chapters_panel_bindings()
