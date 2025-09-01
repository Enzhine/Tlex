from PyQt6.QtWidgets import QDialog, QInputDialog

from utility.locale import LocaleManager

locm = LocaleManager.get_instance


def getItemAt(parent: any, title: str, label: str, items: list[str], index: int) -> tuple[int | None, bool]:
    dialog = QInputDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)
    dialog.setOkButtonText(locm().localize('button.ok'))
    dialog.setCancelButtonText(locm().localize('button.cancel'))

    dialog.setComboBoxItems(items)
    dialog.setComboBoxEditable(False)
    dialog.setTextValue(items[index])

    selected: int | None = None
    ok_pressed: bool = False
    if dialog.exec() == QDialog.DialogCode.Accepted:
        selected = items.index(dialog.textValue())
        ok_pressed = True

    return selected, ok_pressed
