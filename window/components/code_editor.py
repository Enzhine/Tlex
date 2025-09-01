from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QFont, QTextBlock, QPainter, QFontMetrics, QColor, QTextFormat
from PyQt6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("JetBrains Mono", 12))
        # self.highlighter = PythonHighlighter(self.document())
        self.line_number_area = LineNumberArea(self)
        self.highlight_color = QColor(232, 242, 254) # Light blue
        self.tab_width = 2

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.line_number_area.update_on_resize(self.contentsRect())

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
