import os
from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path

class IconButton(QtWidgets.QPushButton):
    def __init__(self, icon_path, text, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.setObjectName("iconButton")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        # icon
        icon_label = QtWidgets.QLabel()
        icon_pixmap = QtGui.QPixmap(icon_path)
        icon_label.setPixmap(icon_pixmap.scaled(32, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        icon_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layout.addWidget(icon_label)
        # text
        text_label = QtWidgets.QLabel(text)
        text_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        text_label.setObjectName("buttonText")
        layout.addWidget(text_label)
        layout.addStretch(1)
        self.setLayout(layout) 