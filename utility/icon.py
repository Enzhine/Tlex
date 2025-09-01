from os import listdir
from pathlib import Path
from PyQt6.QtGui import QIcon

import logging
logger = logging.getLogger(Path(__file__).name)

# Params
SEARCH_PATH: Path | None = None
ICON_FILTER_BY_EXT = ['.ico']

# Private params
_LOADED_ICONS: dict[str, QIcon] = dict()

# Methods
def __load_icon(path_icon: Path):
    path_icon_str = str(path_icon)
    return QIcon(path_icon_str)


def __filter_icons(path: Path) -> bool:
    return path.is_file() and (path.suffix in ICON_FILTER_BY_EXT)


def __scan_icons() -> list[Path]:
    logger.debug("Attempt to scan icons with SEARCH_PATH=%s and FILTER_BY_EXT=%s", SEARCH_PATH, ICON_FILTER_BY_EXT)

    if SEARCH_PATH is None:
        logger.error("Unable to scan icons as SEARCH_PATH not set")
        return []
    if not SEARCH_PATH.exists():
        logger.error("SEARCH_PATH set to '%s' not exists", SEARCH_PATH)
        return []
    if not SEARCH_PATH.is_dir():
        logger.error("SEARCH_PATH set to '%s' exists, but requires to be a folder", SEARCH_PATH)
        return []

    filtered = filter(__filter_icons, [SEARCH_PATH / sub_path for sub_path in listdir(SEARCH_PATH)])
    return list(filtered)


def find_icon(icon_key: str) -> QIcon | None:
    try:
        return _LOADED_ICONS[icon_key]
    except KeyError:
        return None


def load_icons():
    icons_paths = __scan_icons()
    logger.debug("Found icons: %s", list(map(str, icons_paths)))

    if len(icons_paths) == 0:
        logger.warning("No icons loaded")
        return

    for icon_path in icons_paths:
        icon_key = icon_path.stem
        icon = __load_icon(icon_path)

        if icon_key in _LOADED_ICONS:
            logger.warning("Icon '%s' is already loaded and will be replaced", icon_key)
        _LOADED_ICONS[icon_key] = icon

        logger.debug("Loaded icon '%s'", icon_key)
