from typing import Dict
from .player import Player, PlayerConnectionError, PlayerCreationError
from .proxy_player import PlayerProxy
from chapters import logger_config

logger = logger_config.app_logger


try:
    from .player_pydbus import Player_pydbus
except ImportError:
    from .player_dbus_python import Player_dbus_python


class PlayerFactory:
    unuseable_player_names = []

    @staticmethod
    def get_running_player_names() -> Dict[str, str]:
        """Retrieves media player instances names of currently running
        MPRIS D-Bus enabled players, from the dbus SessionBus.
        returns: a dictionary. The dictionary key is the unqualified
        player instance name and value is the fully qualified player name."""

        running_player_names = {}
        media_player_prefix = "org.mpris.MediaPlayer2"
        media_player_prefix_len = len(media_player_prefix)
        try:
            all_service_names = Player_pydbus.get_service_names()
        except NameError:
            all_service_names = Player_dbus_python.get_service_names()
            logger.info("Retrieved running services with dbus-python")

        for service in all_service_names:
            if media_player_prefix in service:
                if service in PlayerFactory.unuseable_player_names:
                    continue
                service_suffix = service[media_player_prefix_len + 1 :]
                try:
                    # Not all org.mpris.MediaPlayer2 instances are useable
                    # Attempting (relatively cheap) player creation to
                    # exclude unusable players
                    PlayerFactory.get_player(str(service), service_suffix)
                    running_player_names[service_suffix] = str(service)
                except PlayerCreationError:
                    PlayerFactory.unuseable_player_names.append(str(service))
        return running_player_names

    @staticmethod
    def get_player(fq_player_name, short_player_name) -> Player:
        try:
            type(Player_pydbus)
            logger.debug("Creating a Player_pydbus instance.")
            player = Player_pydbus(fq_player_name, short_player_name)
            return PlayerProxy(player)
        except (NameError, KeyError):
            logger.debug("Creating a Player_dbus_python instance.")
            player = Player_dbus_python(fq_player_name, short_player_name)
            return PlayerProxy(player)
        except PlayerConnectionError as per:
            raise PlayerCreationError(per)
        except Exception as e:
            logger.error(type(e))
            logger.error(e)
            raise PlayerCreationError(e)
