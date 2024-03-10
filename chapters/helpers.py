"""
Helper functions for mpris-dbus-apps
"""

import re
import logging
import os
import json
from chapters.dbus_mpris.player import (
    Player,
)
from enum import IntEnum
from functools import lru_cache
from typing import Dict, Tuple, TextIO
import chapters.yt_ch as youtube_chapters

import pyclip
import validators


logger = logging.getLogger(__name__)


class Direction(IntEnum):
    FORWARD = 1
    REVERSE = -1


class SuspiciousOperation(Exception):
    """The user did something suspicious"""


class SuspiciousFileOperation(SuspiciousOperation):
    """A Suspicious filesystem operation was attempted"""

    pass


def get_url_from_clipboard():
    _url = None
    try:
        _url = pyclip.paste()
        _url = _url.decode('utf-8')
    except Exception as e:
        logger.warning(e)
    _valid = validators.url(_url)
    if _valid:
        if _url.find("youtu") == -1:
            _url = None
    else:
        _url = None
    return _url


def get_valid_filename(name):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    >>> get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise SuspiciousFileOperation("Could not derive file name from '%s'" % name)
    return s


def is_player_useable(player: Player) -> bool:
    if player.can_control and player.can_seek:
        return True
    return False


@lru_cache
def to_microsecs(time_str: str) -> int:
    """Converts time specified by the string HH:MM:SS into microseconds.

    Arguments
    time_str is a string.  The maximum value is 99:59:59. The minimum value is 00:00:00
    Returns
    An interger value of the converted time in microseconds
    """

    # Setup the regex expression that will validate the time format
    m = re.search("^[0-9][0-9]:[0-5][0-9]:[0-5][0-9]$", time_str)
    if m is None:
        raise ValueError(
            "Invalid time format. The valid format is HH:MM:SS."
            "The maximum value is 99:59:59."
            "The minimum value is 00:00:00"
        )
    parts = time_str.split(":")
    int_parts = [int(s) for s in parts]
    hours, mins, secs = int_parts
    total_mins = (hours * 60) + mins
    mins_in_microsecs = total_mins * 60000000
    total_microsecs = mins_in_microsecs + (secs * 1000000)
    return total_microsecs


def to_HHMMSS(microsecs: int) -> str:
    """Converts time specifed in microseconds to HH:MM:SS time format.
    The maximum input value is 359999000000, which is equvalent to
    99:59:59 in HH:MM:SS format.

    Arguments
    microsecs is an integer, -ve input values are converted to +ve values
    Returns a string in HH:MM:SS time format.
    """

    abs_microsecs = abs(microsecs)
    if abs_microsecs > 359999000000:
        raise ValueError("Max absolute value of microsecs is 359999000000")
    total_secs = int(abs_microsecs / 1000000)
    total_minutes = int(total_secs / 60)
    left_over_secs = total_secs % 60
    hours = int(total_minutes / 60)
    minutes = int(total_minutes % 60)
    seconds = left_over_secs
    sec_s = f"{seconds}" if seconds > 9 else f"0{seconds}"
    min_s = f"{minutes}" if minutes > 9 else f"0{minutes}"
    hr_s = f"{hours}" if hours > 9 else f"0{hours}"
    return f"{hr_s}:{min_s}:{sec_s}"


def chapters_json_to_py(ch_json: str) -> Tuple[str, Dict[str, str]]:
    chapters = {}
    title = "No Title"
    try:
        json_dict = json.loads(ch_json)
    except json.JSONDecodeError as e:
        logger.critical(f"Chapters content is not a valid JSON document. {e}")
        raise ValueError(f"Chapters content is not a valid JSON document.{e}")

    if json_dict["title"]:
        title = json_dict["title"]
    else:
        title = "Chapters"
    if json_dict["chapters"]:
        chapters = json_dict["chapters"]
    else:
        chapters = {}
    return title, chapters


def chapters_py_to_json(title: str, chapters: Dict[str, str]) -> str:
    chapters_dict = {"title": None, "chapters": None}
    title = title if title else "title"
    chapters_dict["title"] = title
    chapters_dict["chapters"] = chapters
    return json.dumps(chapters_dict, indent=4)


def load_chapters_file(chapters_file: str | TextIO) -> Tuple[str, Dict[str, str]]:
    if not chapters_file:
        raise FileNotFoundError()
    chapters = {}
    title = "Chapters"
    chapters_json = ""
    if isinstance(chapters_file, str):
        if os.path.isfile(chapters_file) is False:
            logger.error(f"{chapters_file} does not exist")
            raise FileNotFoundError(f"{chapters_file} does not exist")
        chapters_file = open(chapters_file, "r")
    with chapters_file:
        chapters_json = chapters_file.read()

    (title, chapters) = chapters_json_to_py(chapters_json)
    return title, chapters


def save_chapters_file(
    chapters_file: str | TextIO, title: str, chapters: Dict[str, str]
):
    if not chapters_file:
        raise FileNotFoundError()
    json_str = chapters_py_to_json(title=title, chapters=chapters)
    if isinstance(chapters_file, str):
        if os.path.isfile(chapters_file) is False:
            logger.error(f"{chapters_file} does not exist")
            raise FileNotFoundError(f"{chapters_file} does not exist")
        chapters_file = open(chapters_file, "w")
    with chapters_file:
        chapters_file.write(json_str)


def load_chapters_from_youtube(video: str):
    chapters = {}
    title = "Chapters"
    chapters_json = ""
    _, chapters_json = youtube_chapters.get_chapters_json(video)
    (title, chapters) = chapters_json_to_py(chapters_json)
    return title, chapters
