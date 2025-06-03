from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from utils.helper import get_resource_path
import os

class ErrorDialog(QtWidgets.QDialog):
    """에러 메시지를 보여주는 커스텀 다이얼로그입니다."""
    def __init__(self, error_msg: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error")
        self.load_styles()
        self.init_ui(error_msg)

    def load_styles(self):
        style_path = get_resource_path(os.path.join("src", "ui", "styles", "dialog.qss"))
        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def init_ui(self, error_msg: str):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        label = QtWidgets.QLabel(error_msg)
        label.setWordWrap(False)
        label.setAlignment(Qt.AlignLeft)
        label.setStyleSheet("font-size: 12px; color: #fff; background: transparent;")
        layout.addWidget(label)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.adjustSize()
        self.setMinimumSize(self.size())
        self.setMaximumSize(self.size()) 