from pathlib import Path

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat
from dataclasses import dataclass

import logging
logger = logging.getLogger(Path(__file__).name)


@dataclass
class HighlightRule:
    rexp: QRegularExpression
    format: QTextCharFormat


class RuleBasedHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._highlighting_rules: list[HighlightRule] = []

    def add_rule(self, rule: HighlightRule):
        self._highlighting_rules.append(rule)

    def highlightBlock(self, text):
        for rule in self._highlighting_rules:
            match_iterator = rule.rexp.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), rule.format)


class HighlighterRegistry:
    __INSTANCE: 'HighlighterRegistry' = None

    @staticmethod
    def get_instance() -> 'HighlighterRegistry':
        return HighlighterRegistry.__INSTANCE

    def __init__(self):
        current_instance = HighlighterRegistry.__INSTANCE
        if current_instance is not None:
            logger.warning('There is already a global instance of HighlighterRegistry that is going to be replaced')
        HighlighterRegistry.__INSTANCE = self

        self.__registry: dict[str, type] = dict()

    def register(self, highlighter: type):
        key = highlighter.__name__
        self.__registry[key] = highlighter

        logger.info("Registered type %s as %s", highlighter, key)

    def get(self, key: str) -> type | None:
        return self.__registry.get(key, None)
