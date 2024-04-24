from .player import Player
from functools import cached_property, wraps
from typing import Any, Dict
from chapters import logger_config

logger = logger_config.get_logger()


def reconnect_player(func):
    @wraps(func)
    def decorator(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except Exception as e:
            logger.error(type(e))
            logger.info(e)
            logger.info("Possible player discconnection, attempting to reconnect")
            self.connect()
            logger.info(f"Attempting to call {func.__name__} again")
            func(self, *args, **kwargs)

    return decorator


def handle_player_error(func: callable):
    def decorator(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.error("An error occured when attempting to call the player")
            logger.error(type(e))
            raise

    return decorator


class PlayerProxy(Player):
    def __init__(self, player: Player):
        self._player = player

    def set_player(self, player: Player):
        self._player = player

    @handle_player_error
    def connect(self):
        if self._player:
            self._player.connect()

    @reconnect_player
    def raise_window(self) -> None:
        if self._player:
            self._player.raise_window()

    @reconnect_player
    def play(self) -> None:
        if self._player:
            self._player.play()

    @reconnect_player
    @handle_player_error
    def play_pause(self) -> None:
        if self._player:
            self._player.play_pause()

    @reconnect_player
    def pause(self) -> None:
        if self._player:
            self._player.pause()

    @reconnect_player
    def next(self) -> None:
        if self._player:
            self._player.next()

    @reconnect_player
    def previous(self) -> None:
        if self._player:
            self._player.previous()

    @reconnect_player
    def stop(self) -> None:
        if self._player:
            self._player.stop()

    @reconnect_player
    def seek(self, offset: int) -> None:
        if self._player:
            self._player.seek(offset)

    @reconnect_player
    def set_position(self, to_position: int) -> None:
        if self._player:
            self._player.set_position(to_position)

    @reconnect_player
    def get(self, interface_name: str, property_name: str) -> Any:
        if self._player:
            self._player.get(interface_name, property_name)

    @property
    def mpris_player(self) -> Any:
        if self._player:
            return self._player.mpris_player
        else:
            return None

    @property
    def mpris_media_player2(self) -> Any:
        if self._player:
            return self._player.mpris_media_player2
        else:
            return None

    @property
    def mpris_player_properties(self) -> Any:
        if self._player:
            return self._player.mpris_player_properties
        else:
            return None

    @property
    def name(self) -> str:
        if self._player:
            return self._player.name
        else:
            return None

    @property
    def ext_name(self) -> str:
        if self._player:
            return self._player.ext_name
        else:
            return None

    @property
    def playback_status(self) -> str:
        if self._player:
            return self._player.playback_status
        else:
            return None

    @property
    def position(self) -> int:
        if self._player:
            return self._player.position
        else:
            return None

    @property
    def metadata(self) -> Dict[str, Any]:
        if self._player:
            return self._player.metadata
        else:
            return None

    @property
    def trackid(self) -> str:
        if self._player:
            return self._player.trackid
        else:
            return None

    @cached_property
    def can_control(self) -> bool:
        if self._player:
            return self._player.can_control
        else:
            return None

    @cached_property
    def can_seek(self) -> bool:
        if self._player:
            return self._player.can_seek
        else:
            return None

    @cached_property
    def can_pause(self) -> bool:
        if self._player:
            return self._player.can_pause
        else:
            return None

    @cached_property
    def can_play(self) -> bool:
        if self._player:
            return self._player.can_play
        else:
            return None
