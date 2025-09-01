class SuggestionList(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMaximumHeight(100)
        self.hide()
        self.setWindowFlags(Qt.WindowType.Popup)

    def sizeHint(self):
        return QSize(200, 100)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Apply the currently selected suggestion
            current_item = self.currentItem()
            if current_item:
                self.itemClicked.emit(current_item)
        elif event.key() == Qt.Key.Key_Escape:
            # Hide the suggestion list
            self.hide()
            # Return focus to the editor
            if self.parent():
                self.parent().setFocus()
        else:
            # Let the parent handle other keys
            super().keyPressEvent(event)
