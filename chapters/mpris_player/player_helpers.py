from chapters.mpris_player import Player
from chapters.mpris_player import PlayerFactory, PlayerCreationError
from chapters.logger_config import logger
from typing import List


def get_latest_running_player_instance_name_by_type(
    player_type: str, inststance_prefix: str, player_names: List[str]
) -> str:
    selected_player_name: str = ""
    latest_inst_number = 0
    for player_name in player_names:
        if player_name.startswith(player_type + "."):
            inst_name = player_name.split(".")[1]
            inst_number = int(inst_name.replace(inststance_prefix, ""))
            if inst_number > latest_inst_number:
                latest_inst_number = inst_number
                selected_player_name = player_name
    return selected_player_name


def select_running_player() -> Player | None:
    running_player_names = PlayerFactory.get_running_player_names()
    selected_player: Player | None = None
    selected_player_name: str = ""
    player_names: List = list(running_player_names.keys())
    if player_names:
        selected_player_name = get_latest_running_player_instance_name_by_type(
            "vlc", "instance", player_names
        )
        if not selected_player_name:
            selected_player_name = get_latest_running_player_instance_name_by_type(
                "chrome", "tab", player_names
            )
        if not selected_player_name:
            selected_player_name = player_names[0]

    if selected_player_name:
        selected_player_fq_name = running_player_names[selected_player_name]
        logger().debug("Creating player")
        try:
            selected_player = PlayerFactory.get_player(
                selected_player_fq_name, selected_player_name
            )
        except PlayerCreationError as e:
            logger().error(e)
        else:
            logger().debug("Created player")
    return selected_player
