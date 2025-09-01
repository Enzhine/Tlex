import ext.code_highlight


def main():
    version = '1.0.0'

    import sys
    from pathlib import Path

    import utility.log
    utility.log.setup_logging()

    import logging
    logger = logging.getLogger(Path(__file__).name)
    logger.debug('Starting application v%s...', version)

    __ASSETS_PATH = Path(__file__).parent / "assets"
    logger.debug("Assets path is known as '%s'", __ASSETS_PATH)
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    logger.debug("PyQt6 app created: %s", app)

    logger.debug("Icons setup step===============")
    import utility.icon
    utility.icon.SEARCH_PATH = __ASSETS_PATH / "icon"
    utility.icon.load_icons()
    logger.debug("=========Icons setup step ended")

    logger.debug("Font setup step================")
    import utility.font
    utility.font.SEARCH_PATH = __ASSETS_PATH / "font"
    utility.font.load_fonts()
    logger.debug("==========Font setup step ended")

    logger.debug("Localization setup step========")
    import utility.locale
    utility.locale.SEARCH_PATH = __ASSETS_PATH / "locale"
    utility.locale.LocaleManager(_load_locales=True)
    logger.debug("==Localization setup step ended")

    ext.code_highlight.HighlighterRegistry()

    logger.debug("Scripts setup step=============")
    import utility.script
    utility.script.SEARCH_PATH = __ASSETS_PATH / "script"
    utility.script.load_scripts()
    logger.debug("=======Scripts setup step ended")

    logger.debug("Binding setup step=============")
    import utility.bindng
    utility.bindng.SEARCH_PATH = __ASSETS_PATH / "binding"
    utility.bindng.load_bindings()
    logger.debug("=======Binding setup step ended")

    logger.debug("Notepad init...")
    from window.main_window import Notepad
    notepad = Notepad()
    notepad.show()

    logger.debug('Application started!')
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
