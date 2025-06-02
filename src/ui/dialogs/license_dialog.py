from PySide6 import QtWidgets, QtCore
from utils.helper import get_resource_path
import os
import logging


class LicenseDialog(QtWidgets.QDialog):
    """라이선스 정보를 보여주는 다이얼로그입니다."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("License")
        self.setFixedSize(600, 400)
        logging.info("Open LicenseDialog")
        self.load_styles()
        self.init_ui()

    def load_styles(self):
        """QSS 스타일시트를 로드합니다."""
        style_path = get_resource_path(os.path.join("src", "ui", "styles", "license_dialog.qss"))
        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
    
    def init_ui(self):
        """UI 컴포넌트들을 초기화합니다."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # 라이선스 텍스트 에디터
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

        # 라이선스 텍스트 로드
        self.load_license_text()
        
        # 확인 버튼
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok
        )
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
    
    def load_license_text(self):
        """라이선스 텍스트를 로드합니다."""
        try:
            license_path = get_resource_path(os.path.join("res", "license.txt"))
            with open(license_path, "r", encoding="utf-8") as f:
                self.text_edit.setText(f.read())
        except Exception as e:
            logging.error(f"cannot load license text: {e}")
            self.text_edit.setText("The license file could not be loaded.\nFor assistance, please contact support@meteorbiotech.com.") 