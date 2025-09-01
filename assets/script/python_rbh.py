from ext.code_highlight import RuleBasedHighlighter, HighlighterRegistry

class PythonRBH(RuleBasedHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        from ext.code_highlight import HighlightRule
        from PyQt6.QtCore import QRegularExpression
        from PyQt6.QtGui import QTextCharFormat, QColor, QFont

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 0, 255))  # Blue
        keyword_format.setFontWeight(QFont.Weight.Bold)

        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda",
            "None", "nonlocal", "not", "or", "pass", "raise", "return",
            "True", "try", "while", "with", "yield"
        ]

        for keyword in keywords:
            rule = HighlightRule(QRegularExpression(rf"\b{keyword}\b"), keyword_format)
            self.add_rule(rule)

        # Class name formatting
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(139, 0, 139))  # Dark magenta
        class_format.setFontWeight(QFont.Weight.Bold)
        self.add_rule(HighlightRule(QRegularExpression(r"\b[A-Z][a-zA-Z0-9_]*\b"), class_format))

        # Function/method formatting
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(0, 139, 139))  # Dark cyan
        self.add_rule(HighlightRule(QRegularExpression("\\b[a-zA-Z_][a-zA-Z0-9_]*(?=\\()"), function_format))

        # String formatting
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(163, 21, 21))  # Red-brown
        self.add_rule(HighlightRule(QRegularExpression("\".*\""), string_format))
        self.add_rule(HighlightRule(QRegularExpression("'.*'"), string_format))

        # Comment formatting
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(0, 128, 0))  # Green
        self.add_rule(HighlightRule(QRegularExpression("#[^\n]*"), comment_format))

        # Number formatting
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(255, 69, 0))  # Orange-red
        self.add_rule(HighlightRule(QRegularExpression("\\b[0-9]+\\b"), number_format))

HighlighterRegistry.get_instance().register(PythonRBH)
