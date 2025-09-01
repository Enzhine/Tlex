from pathlib import Path

from PyQt6.QtGui import QAction, QKeySequence, QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QMenu, QFileDialog, QMessageBox, QTabWidget

from window.components.code_editor import CodeEditor
from utility.bindng import match_binding_by_path
from utility.locale import LocaleManager
from utility.icon import find_icon
from window.components.dialog import getItemAt

locm = LocaleManager.get_instance


def window_title_setter(o, txt):
    o.setWindowTitle(txt)


def menu_title_setter(o, txt):
    o.setTitle(txt)


class Notepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__init_ui()

    def __init_ui(self):
        self.tabs = QTabWidget(self)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.__on_tab_closed)

        self.new_file()
        self.setCentralWidget(self.tabs)

        self.__init_menu_file()
        self.__init_menu_settings()

        self.setGeometry(100, 100, 800, 600)
        locm().bind(self, 'notepad.title', window_title_setter)
        self.setWindowIcon(find_icon('tlex'))

    def __init_menu_file(self):
        menu_file: QMenu = locm().bind(self.menuBar().addMenu('menu_file'), 'notepad.menu.file', menu_title_setter)

        action_new_file = locm().bind(QAction(self), 'notepad.action.new_file')
        action_new_file.setShortcut(QKeySequence.StandardKey.New)
        action_new_file.triggered.connect(self.new_file)
        menu_file.addAction(action_new_file)

        action_open_file = locm().bind(QAction(self), 'notepad.action.open_file')
        action_open_file.setShortcut(QKeySequence.StandardKey.Open)
        action_open_file.triggered.connect(self.open_file)
        menu_file.addAction(action_open_file)

        action_save_file = locm().bind(QAction(self), 'notepad.action.save_file')
        action_save_file.setShortcut(QKeySequence.StandardKey.Save)
        action_save_file.triggered.connect(self.save_file)
        menu_file.addAction(action_save_file)

        action_save_file_as = locm().bind(QAction(self), 'notepad.action.save_file_as')
        action_save_file_as.triggered.connect(self.save_file_as)
        menu_file.addAction(action_save_file_as)

    def closeEvent(self, event: QCloseEvent):
        while self.tabs.count() != 0:
            if not self.__on_tab_closed(0):
                event.ignore()
                return
        event.accept()

    def __on_tab_closed(self, tab_idx: int) -> bool:
        editor: CodeEditor = self.tabs.widget(tab_idx)
        if not editor.is_edited:
            self.tabs.removeTab(tab_idx)
            return True
        file_name = self.tabs.tabToolTip(tab_idx)
        if len(file_name) == 0:
            file_name = self.tabs.tabText(tab_idx)
            if file_name.endswith('*'):
                file_name = file_name[:-1]

        title = locm().localize('notepad.window.question.title')
        description = locm().localize('notepad.window.close_tab.description') % file_name
        reply = QMessageBox.question(self, title, description)
        if reply == QMessageBox.StandardButton.Yes:
            self.tabs.removeTab(tab_idx)
            return True
        return False

    def __init_menu_settings(self):
        menu_settings: QMenu = locm().bind(self.menuBar().addMenu('menu_settings'), 'notepad.menu.settings',
                                           menu_title_setter)

        action_change_language = locm().bind(QAction(self), 'notepad.action.change_language')
        action_change_language.triggered.connect(self.change_language)
        menu_settings.addAction(action_change_language)

    def __create_new_tab(self, file_path: str | Path, file_data: str | None, focus: bool = True) -> int:
        editor = CodeEditor()
        if file_data:
            editor.setPlainText(file_data)

        if isinstance(file_path, Path):
            binding = match_binding_by_path(file_path)
            if binding:
                icon = binding.icon

                if binding.highlighter_type is not None:
                    highlighter_type = binding.highlighter_type
                    editor.hl = highlighter_type(editor.document())
            else:
                icon = find_icon('unknown')

            tab_idx = self.tabs.addTab(editor, icon, file_path.name)
            self.tabs.setTabToolTip(tab_idx, str(file_path))
        else:
            icon = find_icon('unknown')

            tab_idx = self.tabs.addTab(editor, icon, file_path)

        def follow_editor_state(_editor: CodeEditor):
            tab_idx = self.tabs.indexOf(_editor)
            tab_name = self.tabs.tabText(tab_idx)

            if _editor.is_edited and not tab_name.endswith('*'):
                self.tabs.setTabText(tab_idx, tab_name + '*')

        editor.code_changed.connect(follow_editor_state)

        if focus:
            self.tabs.setCurrentIndex(tab_idx)
        return tab_idx

    def new_file(self):
        self.__create_new_tab('New', None)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, locm().localize('notepad.window.open_file.title'))
        if not filename:
            return
        file_path = Path(filename)

        try:
            file_size = file_path.stat().st_size
            if file_size > 1024 * 1024 * 2:
                raise RuntimeWarning("Operation with files larger than 2Mb is not yet implemented")

            with open(filename, 'r') as f:
                file_data = f.read()

            self.__create_new_tab(file_path, file_data)
        except Exception as e:
            title = locm().localize('notepad.window.error.title')
            description = locm().localize('notepad.window.open_file.error')
            QMessageBox.critical(self, title, f'{description}. {e}')

    def save_file(self):
        tab_idx = self.tabs.currentIndex()
        stored_path_str = self.tabs.tabToolTip(tab_idx)

        if len(stored_path_str) == 0:
            self.save_file_as()
            return
        stored_path = Path(stored_path_str)

        editor: CodeEditor = self.tabs.widget(tab_idx)
        if not editor.is_edited:
            return

        self.__save_file(stored_path, tab_idx)
        self.__update_tab_state(tab_idx, stored_path)
        editor.is_edited = False

    def save_file_as(self) -> bool:
        filename, _ = QFileDialog.getSaveFileName(self, locm().localize('notepad.window.save_file.title'))
        if not filename:
            return False
        file_path = Path(filename)

        tab_idx = self.tabs.currentIndex()
        self.__save_file(filename, tab_idx)
        self.__update_tab_state(tab_idx, file_path)
        return True

    def __update_tab_state(self, tab_idx: int, file_path: Path):
        self.tabs.setTabText(tab_idx, file_path.name)
        self.tabs.setTabToolTip(tab_idx, str(file_path))

    def __save_file(self, filename: str | Path, tab_idx: int):
        try:
            editor: CodeEditor = self.tabs.widget(tab_idx)
            file_data = editor.toPlainText()

            with open(filename, 'w') as f:
                f.write(file_data)

        except Exception as e:
            title = locm().localize('notepad.window.error.title')
            error_description = locm().localize('notepad.window.save_file.error')
            QMessageBox.critical(self, title, f'{error_description}. {e}')

    def change_language(self):
        lm = locm()

        title_txt = lm.localize('notepad.window.change_language.title')
        call_to_action_txt = lm.localize('notepad.window.change_language.call_to_action')

        locales = lm.get_available_locales()
        items = [lm.localize_by_locale(locale, 'meta.local_name') for locale in locales]
        current_item = locales.index(lm.get_locale())

        idx, ok_pressed = getItemAt(self, title_txt, call_to_action_txt, items, current_item)
        if ok_pressed:
            locm().set_locale(locales[idx])
