from PySide6 import QtWidgets, QtCore

class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.Signal(int)
    def __init__(self, text, index, parent=None):
        super().__init__(text, parent)
        self.index = index
        self.setCursor(QtCore.Qt.PointingHandCursor)
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit(self.index)
        super().mousePressEvent(event) 