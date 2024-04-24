"""Convenience wrappers for DBbus MPRIS core functionality"""

from abc import ABC, abstractmethod
import re
from typing import Any, Dict
from functools import lru_cache, cached_property
from chapters import logger_config


logger = logger_config.get_logger()


class Player(ABC):
    """A convenience class whose object instances encapsulates
    an MPRIS player object and exposes a subset of
    the org.mpris.MediaPlayer2.Player interface."""

    @abstractmethod
    def __init__(self, mpris_player_name, ext_player_name) -> None:
        self._name = mpris_player_name
        self._ext_name = ext_player_name
        self.connect()

    def connect(self):
        pass

    @abstractmethod
    def raise_window(self) -> None: ...

    @abstractmethod
    def play(self) -> None: ...

    @abstractmethod
    def play_pause(self) -> None: ...

    @abstractmethod
    def pause(self) -> None: ...

    @abstractmethod
    def next(self) -> None: ...

    @abstractmethod
    def previous(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def seek(self, offset: int) -> None: ...

    @abstractmethod
    def set_position(self, to_position: int) -> None: ...

    def get(self, interface_name: str, property_name: str) -> Any: ...

    @lru_cache()
    def _is_object_path_valid(self, path: str) -> bool:
        """Whether this is a valid object path.
        :param path: The object path to validate.
        :returns: Whether the object path is valid.
        """
        _path_re = re.compile(r"^[A-Za-z0-9_]+$")
        if not isinstance(path, str):
            return False

        if not path:
            return False

        if not path.startswith("/"):
            return False

        if len(path) == 1:
            return True

        for element in path[1:].split("/"):
            if _path_re.search(element) is None:
                return False

        return True

    @property
    @abstractmethod
    def mpris_player(self) -> Any: ...

    @property
    @abstractmethod
    def mpris_media_player2(self) -> Any: ...

    @property
    @abstractmethod
    def mpris_player_properties(self) -> Any: ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...
        return self._name

    @property
    @abstractmethod
    def ext_name(self) -> str:
        ...
        return self._ext_name

    @property
    @abstractmethod
    def playback_status(self) -> str: ...

    @property
    @abstractmethod
    def position(self) -> int: ...

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]: ...

    @property
    @abstractmethod
    def trackid(self) -> str: ...

    @cached_property
    @abstractmethod
    def can_control(self) -> bool: ...

    @cached_property
    @abstractmethod
    def can_seek(self) -> bool: ...

    @cached_property
    @abstractmethod
    def can_pause(self) -> bool: ...

    @cached_property
    @abstractmethod
    def can_play(self) -> bool: ...


class NoValidMprisPlayersError(Exception):
    pass


class PlayerConnectionError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        logger.error("Player connection failed")


class PlayerCreationError(Exception):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        logger.error("Player creation failed")
