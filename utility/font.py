from os import listdir
from pathlib import Path

import logging
logger = logging.getLogger(Path(__file__).name)

from PyQt6.QtGui import QFontDatabase

# Params
SEARCH_PATH: Path | None = None
FONT_FILTER_BY_EXT = ['.ttf']

# Methods
def __load_font(path_font: Path):
    path_font_str = str(path_font)
    return  QFontDatabase.addApplicationFont(path_font_str)


def __filter_fonts(path: Path) -> bool:
    return path.is_file() and (path.suffix in FONT_FILTER_BY_EXT)


def __scan_fonts() -> list[Path]:
    logger.debug("Attempt to scan fonts with SEARCH_PATH=%s and FILTER_BY_EXT=%s", SEARCH_PATH, FONT_FILTER_BY_EXT)

    if SEARCH_PATH is None:
        logger.error("Unable to scan fonts as SEARCH_PATH not set")
        return []
    if not SEARCH_PATH.exists():
        logger.error("SEARCH_PATH set to '%s' not exists", SEARCH_PATH)
        return []
    if not SEARCH_PATH.is_dir():
        logger.error("SEARCH_PATH set to '%s' exists, but requires to be a folder", SEARCH_PATH)
        return []

    filtered = filter(__filter_fonts, [SEARCH_PATH / sub_path for sub_path in listdir(SEARCH_PATH)])
    return list(filtered)



def load_fonts():
    font_paths = __scan_fonts()
    logger.debug("Found fonts: %s", list(map(str, font_paths)))

    if len(font_paths) == 0:
        logger.warning("No fonts loaded")
        return

    for font_path in font_paths:
        id = __load_font(font_path)

        if id < 0:
            logger.error("Unable to load font '%s'", font_path)
            continue
        fams = QFontDatabase.applicationFontFamilies(id)
        logger.debug("Loaded font '%s' with id %s and families: %s", font_path, id, fams)
