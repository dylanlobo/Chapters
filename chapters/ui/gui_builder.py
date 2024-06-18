from chapters.ui.gui import AppMainWindow
import chapters.helpers as helpers
from chapters.ui.gui_controller import GuiController
from functools import partial
from typing import Tuple, List, Dict
from pathlib import Path
from chapters.logger_config import logger


class AppGuiBuilder:
    def __init__(self, chapters_filename: str):
        self._chapters_filename = chapters_filename
        self._view: AppMainWindow = AppMainWindow()
        self._gui_controller = GuiController(self._view, self)
        self._gui_controller.set_chapters_filename(chapters_filename)

    def create_menu_bar_bindings(self) -> None:
        logger().debug("Creating menu bar")
        self._view.menu_bar.bind_connect_to_player_command(
            self._gui_controller.handle_connection_command
        )
        self._view.menu_bar.bind_disconnect_player_command(
            self._gui_controller.handle_disconnection_command
        )
        self._view.menu_bar.bind_load_chapters_file_command(
            self._gui_controller.handle_load_chapters_file_command
        )
        self._view.menu_bar.bind_load_chapters_from_youtube_command(
            self._gui_controller.handle_load_chapters_from_youtube
        )

        self._view.menu_bar.bind_save_chapters_file_command(
            self._gui_controller.handle_save_chapters_file_command
        )

    def create_chapters_panel_bindings(
        self, chapters_title: str = "", chapters: Dict[str, str] = {}
    ) -> None:
        logger().debug("Creating ChaptersPanel bindings")

        (
            listbox_items,
            chapters_position_functions,
        ) = self._build_chapters_listbox_bindings(chapters)
        self._create_listbox_items(
            chapters_title, listbox_items, chapters_position_functions
        )

    def _build_chapters_listbox_bindings(
        self, chapters: Dict[str, str]
    ) -> Tuple[List[str], List[callable]]:
        logger().debug("Creating chapters listbox bindings")

        listbox_items: List[str] = []
        chapters_position_functions: List[callable] = []
        chapter: str
        position: str
        if chapters:
            n_items = len(chapters)
            for i, (chapter, position) in enumerate(chapters.items()):
                if n_items >= 10:
                    index = f"0{i+1}" if i < 9 else f"{i+1}"
                else:
                    index = f"{i+1}"
                listbox_items.append(f"{index}.  {chapter} ({position})")
                chapters_position_functions.append(
                    partial(self._gui_controller.set_player_position, position)
                )
        return (listbox_items, chapters_position_functions)

    def _create_listbox_items(
        self,
        chapters_title: str,
        listbox_items: List[str],
        chapters_position_functions: List[callable],
    ) -> None:
        logger().debug("Creating chapters listbox items")

        self._view.set_main_window_title(chapters_title)
        self._view.set_chapters(chapters=listbox_items)
        self._view.bind_chapters_selection_commands(
            chapters_selection_action_functs=chapters_position_functions
        )

    def create_player_control_panel_bindings(self) -> None:
        logger().debug("Creating Player Control Panel bindings")
        button_action_funcs = {
            "Play/Pause": self._gui_controller.play_pause_player,
            ">|": self._gui_controller.next_player,
            ">": partial(self._gui_controller.skip_player, offset="00:00:05"),
            ">>": partial(self._gui_controller.skip_player, offset="00:00:10"),
            ">>>": partial(self._gui_controller.skip_player, offset="00:01:00"),
            "<": partial(
                self._gui_controller.skip_player,
                offset="00:00:05",
                direction=helpers.Direction.REVERSE,
            ),
            "<<": partial(
                self._gui_controller.skip_player,
                offset="00:00:10",
                direction=helpers.Direction.REVERSE,
            ),
            "<<<": partial(
                self._gui_controller.skip_player,
                offset="00:01:00",
                direction=helpers.Direction.REVERSE,
            ),
            "|<": self._gui_controller.previous_player,
        }
        self._view.bind_player_controls_commands(button_action_funcs)

    def create_app_window_bindings(self) -> None:
        logger().debug("Creating Application Window bindings")
        self._view.bind_reload_chapters(self._gui_controller.handle_reload_chapters)
        self._view.bind_clear_chapters(self._gui_controller.handle_clear_chapters)
        self._view.bind_select_player_shortcut(
            self._gui_controller.handle_connection_command
        )
        self._view.bind_insert_chapter(self._gui_controller.handle_insert_chapter)
        self._view.bind_edit_chapter(self._gui_controller.handle_edit_chapter)
        self._view.bind_jump_to_position(self._gui_controller.handle_jump_to_position)
        self._view.bind_save_chapters(
            self._gui_controller.handle_save_chapters_file_command
        )
        self._view.bind_raise_player_window(self._gui_controller.raise_player_window)

    def build(self) -> AppMainWindow:
        self.create_menu_bar_bindings()
        chapters_title: str = ""
        chapters: Dict[str, str] = {}
        if self._chapters_filename:
            chapters_title, chapters = self._gui_controller.load_chapters_file(
                self._chapters_filename
            )
            dir = (Path(self._chapters_filename)).parent.absolute()
            self._view.set_chapters_file_path(str(dir))
        self.create_chapters_panel_bindings(chapters_title, chapters)
        self.create_player_control_panel_bindings()
        self.create_app_window_bindings()
        return self._view


def build_gui(chapters_filename: str) -> AppMainWindow:
    gui_builder = AppGuiBuilder(chapters_filename)
    gui_window = gui_builder.build()
    return gui_window
