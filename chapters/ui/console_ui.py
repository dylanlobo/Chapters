from consolemenu import ConsoleMenu, SelectionMenu
from consolemenu.items import FunctionItem
from consolemenu.items import SubmenuItem
from typing import Any, Dict, List


from chapters.mpris_player import (
    NoValidMprisPlayersError,
    PlayerCreationError,
)
from chapters.mpris_player import Player, PlayerFactory
from chapters import helpers
from chapters.logger_config import logger


class ChaptersMenuConsole:
    def __init__(self, title: str) -> None:
        self._reload_chapters = False
        self._title = title
        self._console_main_menu = ConsoleMenu(title=self._title, subtitle="Chapters")

    @property
    def reload_chapters_on_exit(self) -> bool:
        return self._reload_chapters

    def append_main_menu_item(self, menu_item: Any) -> None:
        self._console_main_menu.append_item(menu_item)

    def display_menu(self) -> None:
        self._console_main_menu.show()

    def set_reload_chapters_on_exit(self) -> None:
        self._reload_chapters = True


class ChaptersMenuConsoleBuilder:
    def __init__(self, chapters_filename: str, player: Player) -> None:
        self._player = player
        self.load_chapters_file(chapters_filename=chapters_filename)
        self._chapters_menu_console = ChaptersMenuConsole(title=self._chapters_title)

    @property
    def chapters_menu_console(self) -> ChaptersMenuConsole:
        return self._chapters_menu_console

    def load_chapters_file(self, chapters_filename: str):
        try:
            self._chapters_title, self._chapters = helpers.load_chapters_file(
                chapters_filename
            )
        except FileNotFoundError as fe:
            logger().error(fe)
            raise fe

    def build_complete_setup(self) -> None:
        """Builds a ChaptersConsoleMenu with all possible features enabled.
        Useful for interactive testing of all features"""

        self.build_reload_chapters_item()
        self.build_player_control_menu()
        self.build_chapters_menu()

    def build_reload_chapters_item(self) -> None:
        self.chapters_menu_console.append_main_menu_item(
            FunctionItem(
                "Reload Chapters",
                self.chapters_menu_console.set_reload_chapters_on_exit,
                should_exit=True,
            )
        )

    def build_chapters_menu(self) -> None:
        for chapter_name, time_offset in self._chapters.items():
            self.chapters_menu_console.append_main_menu_item(
                FunctionItem(
                    f"{chapter_name} ({time_offset})",
                    self._player.set_position,
                    [helpers.to_microsecs(time_offset)],
                )
            )

    def build_player_control_menu(self) -> None:
        command_menu = ConsoleMenu(title="Player Control Commands")
        command_submenu_item = SubmenuItem(
            text="Player Control Commands",
            submenu=command_menu,
        )
        command_menu.append_item(
            FunctionItem(
                "Play/Pause",
                self._player.play_pause,
            )
        )
        command_menu.append_item(
            FunctionItem(
                "Skip Forward 10 sec",
                self._player.seek,
                [helpers.to_microsecs("00:00:10")],
            )
        )
        command_menu.append_item(
            FunctionItem(
                "Skip Back 10 sec",
                self._player.seek,
                [helpers.to_microsecs("00:00:10") * -1],
            )
        )
        command_menu.append_item(
            FunctionItem(
                "Skip Forward 1 min",
                self._player.seek,
                [helpers.to_microsecs("00:01:00")],
            )
        )
        command_menu.append_item(
            FunctionItem(
                "Skip Back 1 min",
                self._player.seek,
                [helpers.to_microsecs("00:01:00") * -1],
            )
        )
        self.chapters_menu_console.append_main_menu_item(command_submenu_item)


def user_try_another_player() -> bool:
    """Interactive prompt informing the user that their existing player
    selection is not valid and requesting the user to choose a different player"""
    while True:
        answer = input(
            "The selected player does not implement required MPRIS functionality.\n \
                Select another player? Yes[y] or "
            "No[n] default[y]: "
        )
        answer = answer.lower()
        if answer in ("", "y", "yes"):
            return True
        elif answer in ("n", "no"):
            return False


def user_select_player(player_names: List[str]) -> str:
    """Presents the user with an interactive console to select a mpris enabled player
    instance.
    :param: player_names -- a list containing the names of the mpris enabled player \
        instances.
    :returns: a string containing the player name selected by the user"""

    if not isinstance(player_names, list):
        raise TypeError("player_names is not a list")

    selection = SelectionMenu.get_selection(
        title="Select a player to connect to:",
        strings=player_names,
        show_exit_option=False,
    )
    return player_names[selection]


def get_selected_player(running_players: Dict[str, str]) -> Player:
    """Select a player to connect to.
    :param running_players:  A dictionary containing names of running
    mpris enabled players.The key is the unqualified player instance name
    and value is the fully qualified player instance name.
    :returns: A valid Player instance on successful completion.
    :raises: NoValidMprisPlayersError exception if no valid MPRIS enable players
    are available.
    """
    if not running_players:
        raise ValueError("running_players is empty.")

    selected_player_name = ""
    player: Player
    player_names = list(running_players.keys())
    if len(player_names) == 1:
        selected_player_name = player_names[0]
    else:
        selected_player_name = user_select_player(player_names)

    player = PlayerFactory.get_player(
        fq_player_name=running_players[selected_player_name],
        short_player_name=selected_player_name,
    )

    while not helpers.is_player_useable(player):
        player_names.remove(selected_player_name)
        if not player_names:
            msg = f"{selected_player_name} is not useable. \
            No other mpris enabled players are currently running."
            logger().error(msg)
            raise NoValidMprisPlayersError(msg)

        if user_try_another_player():
            selected_player_name = user_select_player(player_names)
            player = PlayerFactory.get_player(
                fq_player_name=running_players[selected_player_name],
                short_player_name=selected_player_name,
            )
        else:
            raise NoValidMprisPlayersError
    return player


def build_console_menu(
    chapters_file: str,
    reload_option: bool,
    player_controls_option: bool,
) -> ChaptersMenuConsole:
    """Orchestrates the building of the console menu by using the capabilities of the
    ChaptersMenuConsoleBuilder. This is the Director in the Builder Pattern"""
    player: Player = None
    running_players = PlayerFactory.get_running_player_names()
    if len(running_players) == 0:
        raise PlayerCreationError("No mpris enabled players are running.")
    if len(running_players) == 1:
        player_names = list(running_players.keys())
        selected_player_name = player_names[0]
        selected_player_fq_name = running_players[selected_player_name]
        logger().debug("Creating player")
        player = PlayerFactory.get_player(selected_player_fq_name, selected_player_name)
        logger().debug("Created player")
    else:
        logger().debug("Requesting user to select a running player")
        player = get_selected_player(running_players)
        logger().debug("Created player")
    console_builder = ChaptersMenuConsoleBuilder(chapters_file, player)
    if reload_option:
        console_builder.build_reload_chapters_item()
    if player_controls_option:
        console_builder.build_player_control_menu()
    console_builder.build_chapters_menu()
    return console_builder.chapters_menu_console
