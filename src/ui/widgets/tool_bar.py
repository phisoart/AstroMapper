from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path
import os

class ToolBar(QtWidgets.QToolBar):
    """메인 툴바 위젯입니다."""
    
    crossToggled = QtCore.Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolBar")
        self.setMovable(False)
        self.cross_on = False
        self.init_ui()
    
    def init_ui(self):
        """UI 컴포넌트들을 초기화합니다."""
        # 이미지 열기 버튼
        cross_action = self.addAction("Cross")
        icon_path = get_resource_path(os.path.join("res", "images", "icons", "icon_cross.png"))
        cross_action.setIcon(QtGui.QIcon(icon_path))
        self.setIconSize(QtCore.QSize(20, 20))

        self.addSeparator()
        cross_action.triggered.connect(self.toggle_cross)
    
    def toggle_cross(self):
        self.cross_on = not self.cross_on
        self.crossToggled.emit(self.cross_on)
    