from PyQt6.QtCore import QRect, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QTextBlock, QPainter, QFontMetrics, QColor, QTextFormat, QKeyEvent, QTextCursor, \
    QSyntaxHighlighter
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit, QLabel, QHBoxLayout, QVBoxLayout

from utility.bindng import Binding
from utility.locale import LocaleManager

locm = LocaleManager.get_instance


def qlabel_tooltip_setter(o, txt):
    o.setToolTip(txt)


class CodeEditorWrapper(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        vbox = QVBoxLayout()

        self.editor = CodeEditor(self)
        vbox.addWidget(self.editor)

        self.info_block = InfoBlock(self, self.editor)
        vbox.addWidget(self.info_block)

        self.setLayout(vbox)


class CodeEditor(QPlainTextEdit):
    code_changed = pyqtSignal(QObject)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("JetBrains Mono", 12))
        self.line_number_area = LineNumberArea(self)

        self.highlight_color = QColor(232, 242, 254) # Light blue
        self.tab_width = 4
        self.is_edited = False

        self.blockCountChanged.connect(self.update_la_offset)
        self.update_la_offset(0)

        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.highlight_current_line()

        self.updateRequest.connect(self.update_on_request)

    def update_la_offset(self, _):
        la_w_px = self.line_number_area.width_px()
        self.setViewportMargins(la_w_px, 0, 0, 0)

    def update_on_request(self, rect, dy):
        self.line_number_area.update_on_request(rect, dy)

        if rect.contains(self.viewport().rect()):
            self.update_la_offset(0)

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            selection.format.setBackground(self.highlight_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.line_number_area.update_on_resize(self.contentsRect())

    def keyPressEvent(self, event: QKeyEvent):
        event_handled = self.__handle_press_event(event)
        if event_handled:
            self.is_edited = True
            self.code_changed.emit(self)

    def __handle_press_event(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Tab:
            self.insertPlainText(' ' * self.tab_width)
            return True

        if event.key() == Qt.Key.Key_Backspace:
            cursor = self.textCursor()
            cursor_pos = cursor.positionInBlock()

            if cursor_pos >= self.tab_width:
                cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.KeepAnchor, self.tab_width)
                selected = cursor.selectedText()
                if selected == ' ' * self.tab_width:
                    cursor.removeSelectedText()
                    return True

        super().keyPressEvent(event)
        return event.isAccepted()


class LineNumberArea(QWidget):
    def __init__(self, editor: CodeEditor):
        super().__init__(editor)
        self.__code_editor = editor

        self.left_offset_px = 8
        self.bg_color = QColor(240, 240, 240) # Light gray
        self.nums_color = QColor(100, 100, 100) # Dark gray

    def __code_editor_block_count(self) -> int:
        return self.__code_editor.blockCount()

    def __code_editor_font_metrics(self) -> QFontMetrics:
        return self.__code_editor.fontMetrics()

    def update_on_resize(self, cont_rect: QRect):
        la_rect = QRect(cont_rect.left(), cont_rect.top(), self.width_px(), cont_rect.height())
        self.setGeometry(la_rect)

    def update_on_request(self, rect: QRect, dy):
        if dy:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.width(), rect.height())

    def width_px(self):
        block_count = self.__code_editor_block_count()
        digits_count = len(str(max(1, block_count)))

        ha = self.__code_editor_font_metrics().horizontalAdvance('9')
        return self.left_offset_px + ha * digits_count

    def paintEvent(self, event):
        ce = self.__code_editor

        # draw bg
        painter = QPainter(self)
        painter.fillRect(event.rect(), self.bg_color)

        # draw nums
        ## init params
        block: QTextBlock = ce.firstVisibleBlock()
        block_number = block.blockNumber()
        top = ce.blockBoundingGeometry(block).translated(ce.contentOffset()).top()
        bottom = top + ce.blockBoundingRect(block).height()
        font_height = ce.fontMetrics().height()
        number_width = self.width() - 5

        ## draw each visible
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                num_txt = str(block_number + 1)
                painter.setPen(self.nums_color)
                painter.drawText(0, int(top), number_width, font_height,
                                 Qt.AlignmentFlag.AlignRight, num_txt)

            block = block.next()
            top = bottom
            bottom = top + ce.blockBoundingRect(block).height()
            block_number += 1


class InfoBlock(QWidget):
    def __init__(self, parent, editor: CodeEditor):
        super().__init__(parent)
        self.editor = editor
        layout = QHBoxLayout()
        layout.setContentsMargins(4, 2, 4, 0)
        layout.setSpacing(6)

        self.highlighter = None

        self.file_path_label = locm().bind(QLabel(self), 'notepad.info.path', qlabel_tooltip_setter)

        self.position_label = locm().bind(QLabel(self), 'notepad.info.cursor_position', qlabel_tooltip_setter)
        self.editor.cursorPositionChanged.connect(self.__update_position)

        self.binding_label = locm().bind(QLabel(self), 'notepad.info.file_type', qlabel_tooltip_setter)

        layout.addWidget(self.file_path_label)
        layout.addStretch()
        layout.addWidget(self.position_label)
        layout.addWidget(self.binding_label)

        self.setLayout(layout)
        self.setFixedHeight(self.sizeHint().height())

    def update_file_path_label(self, txt: str):
        self.file_path_label.setText(txt)

    def __update_position(self):
        cursor: QTextCursor = self.editor.textCursor()
        line = cursor.blockNumber()
        cursor_pos = cursor.positionInBlock()
        self.position_label.setText(f'{line}:{cursor_pos}')

    def update_binding(self, binding: Binding):
        if binding:
            self.binding_label.setText(binding.name)
            editor = self.editor

            if binding.highlighter_type is not None:
                highlighter_type = binding.highlighter_type
                self.highlighter = highlighter_type(editor.document())
        else:
            self.highlighter = None
            self.editor.setPlainText(self.editor.toPlainText())
