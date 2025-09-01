from os import listdir
from pathlib import Path

import logging
logger = logging.getLogger(Path(__file__).name)

# Params
ENABLE_INSECURE_LOAD = True
SEARCH_PATH: Path | None = None
FILTER_BY_EXT = ['.py']

# Methods
class CheckScriptError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def __load_script(path_script: Path):
    with open(path_script, mode='r') as f:
        script_content = f.read()

    exec(script_content)


def __check_script(path_script: Path):
    if not ENABLE_INSECURE_LOAD:
        raise CheckScriptError('Insecure scripts prohibited')
    pass


def __filter_script(path: Path) -> bool:
    return path.is_file() and (path.suffix in FILTER_BY_EXT)


def __scan_scripts() -> list[Path]:
    logger.debug("Attempt to scan scripts with SEARCH_PATH=%s and FILTER_BY_EXT=%s", SEARCH_PATH, FILTER_BY_EXT)

    if SEARCH_PATH is None:
        logger.error("Unable to scan scripts as SEARCH_PATH not set")
        return []
    if not SEARCH_PATH.exists():
        logger.error("SEARCH_PATH set to '%s' not exists", SEARCH_PATH)
        return []
    if not SEARCH_PATH.is_dir():
        logger.error("SEARCH_PATH set to '%s' exists, but requires to be a folder", SEARCH_PATH)
        return []

    filtered = filter(__filter_script, [SEARCH_PATH / sub_path for sub_path in listdir(SEARCH_PATH)])
    return list(filtered)


def load_scripts():
    script_paths = __scan_scripts()
    logger.debug("Found scripts: %s", list(map(str, script_paths)))

    if len(script_paths) == 0:
        logger.warning("No scripts loaded")
        return

    for script_path in script_paths:
        try:
            __check_script(script_path)

            logger.debug("Loading script '%s'", script_path)
            __load_script(script_path)
            logger.debug("Script loaded!")
        except CheckScriptError as err:
            logger.warning("Ignored script '%s' because of %s", script_path, err)
