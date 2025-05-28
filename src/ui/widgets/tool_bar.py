from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path
import os
import json

class ToolBar(QtWidgets.QToolBar):
    """메인 툴바 위젯입니다."""
    
    crossToggled = QtCore.Signal(bool)
    sameWellToggled = QtCore.Signal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolBar")
        self.setMovable(False)
        self.cross_on = False
        self.project_config = None
        self.same_well_on = False
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

        self.color_combo = self.create_color_combo()
        self.addWidget(self.color_combo)
        self.color_combo.currentTextChanged.connect(self.on_color_changed)

        self.addSeparator()
        self.same_well_action = self.addAction("Same Well")
        self.same_well_action.triggered.connect(self.toggle_same_well)
        self.same_well_action.setCheckable(self.same_well_on)

    def toggle_same_well(self):
        self.same_well_on = not self.same_well_on
        self.sameWellToggled.emit(self.same_well_on)

    def toggle_cross(self):
        self.cross_on = not self.cross_on
        self.crossToggled.emit(self.cross_on)
    
    def create_color_combo(self):
        # color_combo 추가
        try:
            color_info_path = get_resource_path(os.path.join("res", "data", "color.json"))
            with open(color_info_path, "r", encoding="utf-8") as f:
                self.color_dict = json.load(f)
        except Exception:
            self.color_dict = {
                "Red": "#FF0000",
                "Green": "#00FF00",
                "Blue": "#0000FF"
            }
        color_combo = QtWidgets.QComboBox()
        color_combo.setMinimumWidth(90)
        color_name = None
        # config에서 현재 색상 가져오기
        current_color_hex = "#FF0000"
        current_color_name = "Red"
        if self.project_config is not None:
            if hasattr(self.project_config, "get_color"):
                current_color_hex = self.project_config.get_color()
            if hasattr(self.project_config, "get_color_name"):
                current_color_name = self.project_config.get_color_name()
        for name, hex_code in self.color_dict.items():
            pixmap = QtGui.QPixmap(24, 16)
            pixmap.fill(QtCore.Qt.transparent)
            color_rect = QtGui.QPixmap(16, 16)
            color_rect.fill(QtGui.QColor(hex_code))
            painter = QtGui.QPainter(pixmap)
            painter.drawPixmap(8, 0, color_rect)
            painter.end()
            icon = QtGui.QIcon(pixmap)
            color_combo.addItem(icon, name)
            if hex_code.upper() == current_color_hex.upper() or name == current_color_name:
                color_name = name
        if color_name:
            color_combo.setCurrentText(color_name)
        color_combo.setStyleSheet("""
            QComboBox { 
                border: none !important; 
                background: transparent !important; 
                color: #aaa !important;
                text-align: center !important;
                padding-left: 0px !important;
            }
            QComboBox QAbstractItemView {
                background: #333333 !important;
                color: #aaa !important;
                text-align: center !important;
                selection-background-color: #333333 !important;
                selection-color: #aaa !important;
            }
        """)
        return color_combo

    def update_color_combo(self):
        if not hasattr(self, "color_combo") or not hasattr(self, "color_dict"):
            return

        color_name = None
        current_color_hex = "#FF0000"
        current_color_name = "Red"
        if self.project_config is not None:
            if hasattr(self.project_config, "get_color"):
                current_color_hex = self.project_config.get_color()
            if hasattr(self.project_config, "get_color_name"):
                current_color_name = self.project_config.get_color_name()

        # 콤보박스에서 해당 색상 이름을 찾아 선택
        for name, hex_code in self.color_dict.items():
            if hex_code.upper() == current_color_hex.upper() or name == current_color_name:
                color_name = name
                break
        if color_name:
            self.color_combo.setCurrentText(color_name)

    def on_color_changed(self, color_name):
        hex_code = self.color_dict.get(color_name, "#FF0000")
        if self.project_config is not None:
            if hasattr(self.project_config, "set_color"):
                self.project_config.set_color(hex_code)
            if hasattr(self.project_config, "set_color_name"):
                self.project_config.set_color_name(color_name)

    