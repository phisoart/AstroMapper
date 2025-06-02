from typing import Optional
from PySide6 import QtWidgets, QtCore, QtGui
import os
import sys
import yaml
from ui.widgets import ImageWidget, LogWidget, TitleBar, ToolBar, StatusBar, InitWidget
from utils.helper import get_resource_path
from utils.settings import Settings
from utils.config import ProjectConfig
from core.roi import ROIs
import logging

class AstromapperMainWindow(QtWidgets.QMainWindow):
    
    def __init__(
        self,
        parent: Optional[QtWidgets.QWidget] = None
    ):
        super().__init__(parent, QtCore.Qt.FramelessWindowHint)
        self.is_init_view = True
        self.is_saved = True
        self.is_project = False

        self.project_dir = None
        self.ROIs = ROIs()
        self.project_config = None

        self.image_widget = ImageWidget(self.ROIs)
        self.log_widget = LogWidget(self.ROIs)

        self.init_ui()

        self.setup_window_properties()

    
    def init_ui(self):
        self.title_bar = TitleBar(self)
        self.setMenuBar(self.title_bar)
        
        self.main_widget, self.main_layout = self.create_main_widget()
        self.setCentralWidget(self.main_widget)

        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

    def create_main_widget(self):
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.init_widget = InitWidget(main_window=self)
        main_layout.addWidget(self.init_widget, alignment=QtCore.Qt.AlignCenter)
        
        return main_widget, main_layout

    def create_project_view_widget(self):
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setChildrenCollapsible(False)  # 자식 위젯이 완전히 접히지 않도록 설정
        splitter.setHandleWidth(2)  # 핸들 너비 설정
        splitter.addWidget(self.image_widget)
        splitter.addWidget(self.log_widget)
        return splitter

    def show_project_view_widget(self):
        # 1. main_layout에서 모든 위젯 제거
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        self.is_init_view = False
        self.project_view_widget = self.create_project_view_widget()
        self.main_layout.addWidget(self.project_view_widget)

    def setup_window_properties(self):
        """윈도우의 기본 속성을 설정합니다."""
        # 윈도우 제목 설정
        self.setWindowTitle("AstroMapper")
        
        # TODO: Widget별 window 최소 width도 지정
        if sys.platform == "darwin":
            # 최소 크기 설정
            self.setMinimumSize(1000, 800)
        else:
            # 최소 크기 설정
            self.setMinimumSize(1500, 1100)
        
        # 윈도우 상태 저장
        self.save_window_state()
    
    def save_window_state(self):
        """윈도우의 상태를 저장합니다."""
        settings = QtCore.QSettings("AstroMapper", "MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
    
    def initialize_project_config(self, project_config):
        self.project_config = project_config
        self.init_widget.project_config = self.project_config
        self.image_widget.project_config = self.project_config
        self.log_widget.project_config = self.project_config
        self.image_widget.tool_bar.project_config = self.project_config
        self.image_widget.tool_bar.update_color_combo()

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        윈도우가 닫힐 때 호출되는 이벤트 핸들러입니다.
        
        Args:
            event: 닫기 이벤트
        """
        # 현재 윈도우 사이즈 및 splitter width 저장
        # TODO 저장 기능 추가
        if hasattr(self, 'project_config') and self.project_config:
            size = self.size()
            self.project_config.set_window_size(size.width(), size.height())
            # splitter 각 위젯 width 저장
            if hasattr(self, 'project_view_widget'):
                sizes = self.project_view_widget.sizes()
                if len(sizes) >= 2:
                    self.project_config.set_splitter_widths(sizes[0], sizes[1])
            self.project_config.update_last_modified()
            self.save_window_state()
        super().closeEvent(event)