from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal
from utils.helper import get_resource_path
import os

class SaveDialog(QtWidgets.QDialog):
    """Custom dialog for save confirmation."""
    # Custom signals
    save_clicked = Signal()
    discard_clicked = Signal()
    cancel_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save")
        self.load_styles()
        self.init_ui()

    def load_styles(self):
        style_path = get_resource_path(os.path.join("src", "ui", "styles", "dialog.qss"))
        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        label = QtWidgets.QLabel("Do you want to save your changes?")
        label.setWordWrap(False)
        label.setAlignment(Qt.AlignLeft)
        label.setStyleSheet("font-size: 12px; color: #fff; background: transparent;")
        layout.addWidget(label)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | 
            QtWidgets.QDialogButtonBox.Discard | 
            QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.button(QtWidgets.QDialogButtonBox.Save).setText("Save")
        button_box.button(QtWidgets.QDialogButtonBox.Discard).setText("Discard")
        button_box.button(QtWidgets.QDialogButtonBox.Cancel).setText("Cancel")
        
        # Connect custom signals to buttons
        button_box.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.save_clicked.emit)
        button_box.button(QtWidgets.QDialogButtonBox.Discard).clicked.connect(self.discard_clicked.emit)
        button_box.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.cancel_clicked.emit)
        
        layout.addWidget(button_box)

        self.adjustSize()
        self.setMinimumSize(self.size())
        self.setMaximumSize(self.size())