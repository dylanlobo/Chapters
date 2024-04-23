from .player import Player
from typing import Any, Dict, List
from functools import cached_property
import dbus
import logging
from chapters import logger_config

logger = logger_config.app_logger


class Player_dbus_python(Player):
    """A convenience class whose object instances encapsulates
    an MPRIS player object and exposes a subset of
    the org.mpris.MediaPlayer2.Player interface."""

    @staticmethod
    def get_service_names() -> List:
        all_service_names = dbus.SessionBus().list_names()
        return all_service_names

    def __init__(self, mpris_player_name, ext_player_name) -> None:
        super().__init__(mpris_player_name, ext_player_name)

    def connect(self):
        bus = dbus.SessionBus()
        try:
            self._proxy = bus.get_object(self._name, "/org/mpris/MediaPlayer2")
        except Exception as e:
            logger.error(f"Caught exceptio {type(e)}")
            logger.error(f"Unable to retrieve the {self._name} proxy from dbus.")
            logger.error(e)
            raise Exception(
                f"Unable to connect to {self._ext_name},"
                f" check if {self._ext_name} it is running."
            )
        self._media_player2 = dbus.Interface(
            self._proxy, dbus_interface="org.mpris.MediaPlayer2"
        )
        self._player = dbus.Interface(
            self._proxy, dbus_interface="org.mpris.MediaPlayer2.Player"
        )
        self._player_properties = dbus.Interface(
            self._player, dbus_interface="org.freedesktop.DBus.Properties"
        )

    def raise_window(self) -> None:
        self.mpris_media_player2.Raise()

    def play(self) -> None:
        self.mpris_player.Play()

    def play_pause(self) -> None:
        self.mpris_player.PlayPause()

    def pause(self) -> None:
        self.mpris_player.Pause()

    def next(self) -> None:
        self.mpris_player.Next()

    def previous(self) -> None:
        self.mpris_player.Previous()

    def stop(self) -> None:
        self.mpris_player.Stop()

    def seek(self, offset: int) -> None:
        self.mpris_player.Seek(offset)

    def set_position(self, to_position: int) -> None:
        if self._is_object_path_valid(self.trackid):
            self.mpris_player.SetPosition(self.trackid, to_position)
        else:
            logger.warning(f"The trackid returned by {self.ext_name} is not valid.")
            logger.debug(
                "Unable to use SetPosition(trackid,postion),"
                " due to invalid trackid value."
            )
            logger.debug("Attempting to use Seek() to set the requested postion.")
            cur_pos = self.position
            seek_to_position = to_position - cur_pos
            self.seek(seek_to_position)

    def get(
        self, property_name: str, interface_name: str = "org.mpris.MediaPlayer2.Player"
    ) -> Any:
        return self.mpris_player_properties.Get(interface_name, property_name)

    @property
    def mpris_player(self):
        return self._player

    @property
    def mpris_media_player2(self):
        return self._media_player2

    @property
    def mpris_player_properties(self):
        return self._player_properties

    @property
    def name(self) -> str:
        return self._name

    @property
    def ext_name(self) -> str:
        return self._ext_name

    @property
    def playback_status(self) -> str:
        return self.get(property_name="PlaybackStatus")

    @property
    def position(self) -> int:
        return self.get(property_name="Position")

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.get(property_name="Metadata")

    @property
    def trackid(self) -> str:
        if "mpris:trackid" in self.metadata:
            return self.metadata["mpris:trackid"]
        else:
            logger.warning(
                f"Metadata from {self.ext_name} does not contain mpris:trackid\n"
                f"Returning an empty string instead"
            )
            return ""

    @cached_property
    def can_control(self) -> bool:
        return self.get(property_name="CanControl")

    @cached_property
    def can_seek(self) -> bool:
        return self.get(property_name="CanSeek")

    @cached_property
    def can_pause(self) -> bool:
        return self.get(property_name="CanPause")

    @cached_property
    def can_play(self) -> bool:
        return self.get(property_name="CanPlay")
