from PySide6.QtWidgets import QStyledItemDelegate, QApplication, QStyle, QStyleOptionButton
from PySide6.QtCore import QModelIndex, Signal, QEvent

# =====================
# BOTON TABLA EMPRESA
# =====================
class ButtonDelegate(QStyledItemDelegate):
    clicked = Signal(QModelIndex)

    def paint(self, painter, option, index):
        button_option = QStyleOptionButton()
        button_option.rect = option.rect
        button_option.text = "Entrar"
        button_option.state = QStyle.State_Enabled
        QApplication.style().drawControl(
            QStyle.CE_PushButton, button_option, painter
        )

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            if option.rect.contains(event.pos()):
                self.clicked.emit(index)
        return True