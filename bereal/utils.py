"""
Utility functions and constants.

Idea for phone numbers as directory base.

import os

def insert_directory(original_path, new_dir, position):
    path_list = original_path.split(os.sep)
    path_list.insert(position, new_dir)
    new_path = os.path.join(*path_list)
    return new_path

original_path = "/a/b/c"
new_dir = "d"
position = 2  # Position after 'a'

new_path = insert_directory(original_path, new_dir, position)
print(new_path)  # Outputs: /a/d/b/c
"""
import configparser
import os
from datetime import datetime
from enum import StrEnum

# Global constants
BASE_URL = "https://berealapi.fly.dev"

IMAGE_EXTENSIONS: list[str] = [".png", ".jpg", ".jpeg", ".webp"]

YEARS: list[str] = ["2022", "2023"]


class Mode(StrEnum):
    """
    Supported video modes.
    """

    CLASSIC = "classic"
    MODERN = "modern"


def str2mode(s: str | None) -> Mode:
    """
    Convert a string to a Mode object.
    """
    if s is None or s == "":
        return Mode.CLASSIC

    match s:
        case "classic":
            return Mode.CLASSIC
        case "modern":
            return Mode.MODERN
        case _:
            raise ValueError(f"Invalid mode: {s}")


# File system paths, for use globally
# TODO(michaelfromyeg): make song, output variable; make folder paths depend on phone number
CWD = os.getcwd()

STATIC_PATH = os.path.join(CWD, "bereal", "static")

FONT_BASE_PATH = os.path.join(STATIC_PATH, "fonts")

IMAGES_PATH = os.path.join(STATIC_PATH, "images")
VIDEOS_PATH = os.path.join(STATIC_PATH, "videos")

ENDCARD_TEMPLATE_IMAGE_PATH = os.path.join(IMAGES_PATH, "endCard_template.jpg")
ENDCARD_IMAGE_PATH = os.path.join(IMAGES_PATH, "endCard.jpg")
OUTLINE_PATH = os.path.join(IMAGES_PATH, "secondary_image_outline.png")

OUTPUT_SLIDESHOW_PATH = os.path.join(VIDEOS_PATH, "slideshow.mp4")

CONTENT_PATH = os.path.join(CWD, "content")

PRIMARY_IMAGE_PATH = os.path.join(CONTENT_PATH, "primary")
SECONDARY_IMAGE_PATH = os.path.join(CONTENT_PATH, "secondary")
COMBINED_IMAGE_PATH = os.path.join(CONTENT_PATH, "combined")
SONG_PATH = os.path.join(CONTENT_PATH, "song.wav")


# Config variables
config = configparser.ConfigParser()

config.read("config.ini")

HOST: str | None = config.get("bereal", "host", fallback=None)
PORT: int | None = config.getint("bereal", "port", fallback=None)

TIMEOUT = config.getint("bereal", "timeout")


# Utility methods
def year2dates(year_str: str) -> tuple[datetime, datetime]:
    """
    Convert a year string to two dates.
    """
    year = int(year_str)

    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    return start_date, end_date


def str2datetime(s: str) -> datetime:
    """
    Convert a string to a datetime object.
    """
    return datetime.strptime(s, "%Y-%m-%d")
