from os import listdir
from pathlib import Path
from PyQt6.QtGui import QIcon, QSyntaxHighlighter
from utility.icon import find_icon
from ext.code_highlight import HighlighterRegistry
from dataclasses import dataclass
import toml

import logging
logger = logging.getLogger(Path(__file__).name)

# Params
SEARCH_PATH: Path | None = None
FILTER_BY_EXT = ['.toml']

# Private params
@dataclass
class Binding:
    suffixes: list[str]
    icon: QIcon
    highlighter_type: type | None

_LOADED_BINDINGS: list[Binding] = list()

# Methods
def __load_binding(path_binding: Path) -> Binding:
    bind_dict = toml.load(path_binding)
    suffixes: list[str] = bind_dict['suffixes']
    icon_name: str = bind_dict['icon_name']
    highlighter_name: str | None = bind_dict.get('highlighter_name', None)

    icon = find_icon(icon_name)
    if icon is None:
        icon = find_icon('unknown')

    highlighter_type = None
    if highlighter_name is not None:
        highlighter_type = HighlighterRegistry.get_instance().get(highlighter_name)

    binding = Binding(suffixes, icon, highlighter_type)
    _LOADED_BINDINGS.append(binding)

    return binding


def __filter_binding(path: Path) -> bool:
    return path.is_file() and (path.suffix in FILTER_BY_EXT)


def __scan_bindings() -> list[Path]:
    logger.debug("Attempt to scan binding with SEARCH_PATH=%s and FILTER_BY_EXT=%s", SEARCH_PATH, FILTER_BY_EXT)

    if SEARCH_PATH is None:
        logger.error("Unable to scan binding as SEARCH_PATH not set")
        return []
    if not SEARCH_PATH.exists():
        logger.error("SEARCH_PATH set to '%s' not exists", SEARCH_PATH)
        return []
    if not SEARCH_PATH.is_dir():
        logger.error("SEARCH_PATH set to '%s' exists, but requires to be a folder", SEARCH_PATH)
        return []

    filtered = filter(__filter_binding, [SEARCH_PATH / sub_path for sub_path in listdir(SEARCH_PATH)])
    return list(filtered)


def load_bindings():
    binding_paths = __scan_bindings()
    logger.debug("Found bindings: %s", list(map(str, binding_paths)))

    if len(binding_paths) == 0:
        logger.warning("No bindings loaded")
        return

    for binding_path in binding_paths:
        binding = __load_binding(binding_path)

        logger.debug("Loaded binding '%s'", binding)

def match_binding_by_path(file_path: Path) -> Binding | None:
    return next((b for b in _LOADED_BINDINGS if file_path.suffix in b.suffixes), None)
