from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path
import os
import json
from ui.widgets.log_widget import LogWidget, LogRowWidget, ClickableLabel
from typing import TYPE_CHECKING
import logging
if TYPE_CHECKING:
    from ui.widgets.image_widget import ImageWidget
    from core.temp_config_manager import TempConfigManager

class ToolBar(QtWidgets.QToolBar):
    """메인 툴바 위젯입니다."""
    
    crossToggled = QtCore.Signal(bool)
    sameWellToggled = QtCore.Signal(bool)
    roiToggled = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window: 'ImageWidget' = parent
        self.temp_config_manager: 'TempConfigManager' = self.main_window.temp_config_manager
        self.setObjectName("toolBar")
        self.setMovable(False)
        self.cross_visible = False
        self.project_config = None
        self.same_well_on = False
        self.roi_on = False
        self.init_ui()
    
    def init_ui(self):
        """UI 컴포넌트들을 초기화합니다."""
        # 이미지 열기 버튼
        cross_action = self.addAction("Cross")
        icon_path = get_resource_path(os.path.join("res", "images", "icons", "icon_cross.png"))
        cross_action.setIcon(QtGui.QIcon(icon_path))
        self.setIconSize(QtCore.QSize(20, 20))
        cross_action.setCheckable(True)
        cross_action.setChecked(self.cross_visible)
        cross_action.triggered.connect(self.toggle_cross)
        self.addSeparator()

        self.color_combo = self.create_color_combo()
        self.addWidget(self.color_combo)
        self.color_combo.currentTextChanged.connect(self.on_color_changed)

        self.addSeparator()
        self.same_well_action = self.addAction("Same Well")
        self.same_well_action.setCheckable(True)
        self.same_well_action.setChecked(self.same_well_on)
        self.same_well_action.triggered.connect(self.toggle_same_well)

        self.addSeparator()
        self.roi_action = self.addAction("Select ROI")
        self.roi_action.setCheckable(True)
        self.roi_action.setChecked(self.roi_on)
        self.roi_action.triggered.connect(self.toggle_roi)

    def toggle_same_well(self, _checked: bool = None):
        if _checked is not None:
            self.same_well_on = _checked
        else:
            self.same_well_on = not self.same_well_on
        self.same_well_action.setChecked(self.same_well_on)
        self.temp_config_manager.set("tool", "same_well_on", self.same_well_on)
        self.sameWellToggled.emit(self.same_well_on)

    def toggle_cross(self, _checked: bool = None):
        if _checked is not None:
            self.cross_visible = _checked
        else:
            self.cross_visible = not self.cross_visible
        logging.info(f"toggle_cross: {self.cross_visible}")
        self.temp_config_manager.set("tool", "cross_visible", self.cross_visible)
        self.crossToggled.emit(self.cross_visible)
    
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

    def initialize_tool_bar(self):
        cross_visible = self.project_config.get("tool", "cross_visible")
        same_well_on = self.project_config.get("tool", "same_well_on")
        roi_on = self.project_config.get("tool", "roi_on")
        self.toggle_cross(cross_visible)
        self.toggle_same_well(same_well_on)
        self.toggle_roi(roi_on)
        self.update_color_combo()

    def on_color_changed(self, color_name):
        hex_code = self.color_dict.get(color_name, "#FF0000")
        if self.temp_config_manager is not None:
            self.temp_config_manager.set("tool", "color", hex_code)
            self.temp_config_manager.set("tool", "color_name", color_name)

    def toggle_roi(self, _checked: bool = None):
        if _checked is not None:
            self.roi_on = _checked
        else:
            self.roi_on = not self.roi_on
        self.roi_action.setChecked(self.roi_on)
        self.temp_config_manager.set("tool", "roi_on", self.roi_on)
        self.roiToggled.emit(self.roi_on)