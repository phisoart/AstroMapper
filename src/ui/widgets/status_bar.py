from PySide6 import QtWidgets, QtCore
from utils.helper import get_resource_path
import os

class StatusBar(QtWidgets.QStatusBar):
    """메인 상태바 위젯입니다."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setFixedHeight(30)
        self.load_styles()
        self.init_ui()
    
    def load_styles(self):
        """QSS 스타일시트를 로드합니다."""
        style_path = get_resource_path(os.path.join("src", "ui", "styles", "status_bar.qss"))
        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
    
    def init_ui(self):
        """UI 컴포넌트들을 초기화합니다."""
        # 왼쪽 메시지용 라벨
        self.left_label = QtWidgets.QLabel()
        self.left_label.setAlignment(QtCore.Qt.AlignLeft)
        self.addWidget(self.left_label)
        
        # 가운데 메시지용 라벨
        self.center_label = QtWidgets.QLabel()
        self.center_label.setAlignment(QtCore.Qt.AlignCenter)
        self.addWidget(self.center_label, 1)  # stretch factor를 1로 설정
        
        # 오른쪽 버전 정보
        version_label = QtWidgets.QLabel("AstroMapper v1.0")
        self.addPermanentWidget(version_label)

    def showLeftMessage(self, message: str):
        """왼쪽 메시지를 표시합니다."""
        self.left_label.setText(message)

    def showCenterMessage(self, message: str):
        """가운데 메시지를 표시합니다."""
        self.center_label.setText(message)

    def clearCenterMessage(self):
        """가운데 메시지를 지웁니다."""
        self.center_label.clear() 