import re
from functools import lru_cache
from os import listdir
from pathlib import Path
import toml

import logging
logger = logging.getLogger(Path(__file__).name)

# Params
SEARCH_PATH: Path | None = None
DEFAULT_LOCALE_BY_LATIN = 'Russian'
DEFAULT_ENCODING = 'utf-8'
LOCALE_FILTER_BY_EXT = ['.toml']

# Private params
__ENCODING_REXP = r'###\s*(?i:encoding)=(.+)'
_LOADED_LOCALES: dict[str, dict] = dict()
_ID_SEQ: int = 0

# Methods and classes
def unwrap_dict(_dict: dict, keys: str, unwrap_key_sep='.'):
    ret = keys
    try:
        for key in keys.split(unwrap_key_sep):
            _dict = _dict[key]
        ret = _dict
    except KeyError:
        pass

    return ret


def __read_encoding(file_path: Path) -> str:
    encoding = DEFAULT_ENCODING

    with open(file_path, encoding='utf-8') as f:
        first_line = f.readline()
        if match := re.match(__ENCODING_REXP, first_line):
            encoding = match.group(1)

    return encoding


def __get_toml_data(file_path: Path) -> dict:
    encoding = __read_encoding(file_path)
    with open(file_path, mode='r', encoding=encoding) as f:
        toml_data = f.read()

    return toml.loads(toml_data)


def __filter_locales(path: Path) -> bool:
    return path.is_file() and (path.suffix in LOCALE_FILTER_BY_EXT)


def __scan_locales() -> list[Path]:
    logger.debug("Attempt to scan locales with SEARCH_PATH=%s", SEARCH_PATH)

    if SEARCH_PATH is None:
        logger.error("Unable to scan locales as SEARCH_PATH not set")
        return []
    if not SEARCH_PATH.exists():
        logger.error("SEARCH_PATH set to '%s' not exists", SEARCH_PATH)
        return []
    if not SEARCH_PATH.is_dir():
        logger.error("SEARCH_PATH set to '%s' exists, but requires to be a folder", SEARCH_PATH)
        return []

    filtered = filter(__filter_locales, [SEARCH_PATH / sub_path for sub_path in listdir(SEARCH_PATH)])
    return list(filtered)

def _new_id() -> int:
    global _ID_SEQ
    ret = _ID_SEQ
    _ID_SEQ += 1
    return ret

class LocaleManager:
    __INSTANCE: 'LocaleManager' = None

    @staticmethod
    def get_instance() -> 'LocaleManager':
        return LocaleManager.__INSTANCE

    def __init__(self, locale_latin: str = None, _load_locales = False):
        current_instance = LocaleManager.__INSTANCE
        if current_instance is not None:
            logger.warning('There is already a global instance of LocaleManager that is going to be replaced')
            current_instance.reset()
        if _load_locales:
            load_locales()
        LocaleManager.__INSTANCE = self

        self.__refs: dict[int, tuple[any, str, any, callable, callable]] = {}

        if len(_LOADED_LOCALES) == 0:
            logger.warning('No locales loaded yet')

        if locale_latin is None:
            self.__locale = DEFAULT_LOCALE_BY_LATIN
            logger.debug("Set default locale to '%s'", self.__locale)
        else:
            self.__locale = locale_latin
            self.set_locale(locale_latin)

        if self.__locale not in _LOADED_LOCALES:
            logger.warning("LocaleManager locale set to '%s', but locales does not contain one", self.__locale)

    def __refs_iterable(self):
        return list(self.__refs.keys())

    def __drop_reference(self, ref_id: int, obj_still: bool):
        try:
            if obj_still:
                obj, _, connection, *_ = self.__refs[ref_id]
                obj.destroyed.disconnect(connection)
            del self.__refs[ref_id]
            logger.debug("Stopped tracking ref_id(%s)", ref_id)
        except ValueError:
            logger.warning('ref_id(%s) is already dropped', ref_id)
        except KeyError:
            logger.error('Attempt to drop unknown ref_id(%s)', ref_id)

    def add_reference(self, obj: any, locale_key: str, setter: callable = None, formatter: callable = None):
        if setter is None:
            setter = lambda _obj, txt: obj.setText(txt)

        if formatter is None:
            formatter = lambda txt: txt

        ref_id = _new_id()
        destroy_connection = obj.destroyed.connect(lambda _: self.__drop_reference(ref_id, False))
        self.__refs[ref_id] = (obj, locale_key, destroy_connection, setter, formatter)

        logger.debug("Now tracking obj=%s as ref_id(%s)", obj, ref_id)
        return ref_id

    def bind[T](self, obj: T, locale_key: str, setter: callable = None, formatter: callable = None) -> T:
        ref_id = self.add_reference(obj, locale_key, setter=setter, formatter=formatter)
        self.__localize_one(ref_id)

        return obj

    def reset(self):
        for ref_id in self.__refs_iterable():
            self.__drop_reference(ref_id, True)
        self.__reset_lru_cache()

    def __localize_all(self):
        for ref_id in self.__refs_iterable():
            self.__localize_one(ref_id)

    def get_available_locales(self) -> list[str]:
        return list(_LOADED_LOCALES.keys())

    def get_locale(self) -> str:
        return self.__locale

    def set_locale(self, locale_latin: str):
        self.__locale = locale_latin
        self.__reset_lru_cache()
        self.__localize_all()

    def __reset_lru_cache(self):
        self.localize.cache_clear()

    def localize_by_locale(self, locale: str, locale_key: str) -> str:
        return unwrap_dict(_LOADED_LOCALES[locale], locale_key)

    @lru_cache
    def localize(self, locale_key: str) -> str:
        return self.localize_by_locale(self.__locale, locale_key)

    def __localize_one(self, ref_id: int):
        try:
            obj, key, _, setter, formatter = self.__refs[ref_id]
            localized_str = self.localize(key)
            setter(obj, formatter(localized_str))
        except KeyError:
            logger.error('Attempt to localize unknown ref_id(%s)', ref_id)


def load_locales():
    locale_paths = __scan_locales()
    logger.debug("Found locales: %s", list(map(str, locale_paths)))

    if len(locale_paths) == 0:
        logger.warning("No locales loaded")
        return

    for locale_path in locale_paths:
        _toml = __get_toml_data(locale_path)
        latin_name = _toml['meta']['latin_name']

        if latin_name in _LOADED_LOCALES:
            logger.warning("Locale '%s' is already present and going to rewritten", latin_name)

        _LOADED_LOCALES[latin_name] = _toml
        logger.debug("Loaded '%s' locale", latin_name)
