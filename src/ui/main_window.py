from typing import Optional
from PySide6 import QtWidgets, QtCore, QtGui
from ui.widgets import ImageWidget, LogWidget, TitleBar, ToolBar, StatusBar, InitWidget
from core.roi import ROIs
from utils.settings import Settings
from core.project_manager import ProjectManager
from core.temp_config_manager import TempConfigManager
from ui.dialogs.save_dialog import SaveDialog
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

        self.settings = Settings()
        self.temp_config_manager = TempConfigManager(self)
        self.project_manager = ProjectManager(self)
        self.image_widget = ImageWidget(self.ROIs, self)
        self.log_widget = LogWidget(self.ROIs)

        self.init_ui()

        self.setup_window_properties()

    
    def init_ui(self):
        self.title_bar = TitleBar(self, project_manager=self.project_manager)
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
        
        self.init_widget = InitWidget(main_window=self, project_manager=self.project_manager)
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
        image_widget_width, log_widget_width = self.settings.get_project_view_widget_width()
        self.project_view_widget.setSizes([image_widget_width, log_widget_width])
        self.main_layout.addWidget(self.project_view_widget)

    def setup_window_properties(self):
        """윈도우의 기본 속성을 설정합니다."""
        # 윈도우 제목 설정
        self.setWindowTitle("AstroMapper")

        width, height, min_width, min_height = self.settings.get_window_size()
        self.setMinimumSize(min_width, min_height)
        self.resize(width, height)

    def initialize_project_config(self, project_config):
        self.project_config = project_config
        self.init_widget.project_config = self.project_config
        self.image_widget.project_config = self.project_config
        self.log_widget.project_config = self.project_config
        self.image_widget.tool_bar.project_config = self.project_config
        self.image_widget.tool_bar.update_tool_bar()

    def show_save_dialog(self) -> bool:
        """
        Shows the save confirmation dialog.
        
        Returns:
            bool: True if saved or discarded, False if cancelled
        """
        dialog = SaveDialog(self)
        result = [False]  # Wrap in list to allow modification in inner functions
        
        def on_save():
            self.temp_config_manager.save_config()
            result[0] = True
            dialog.accept()
            
        def on_discard():
            self.temp_config_manager.remove_temp_config()
            result[0] = True
            dialog.accept()
            
        def on_cancel():
            result[0] = False
            dialog.reject()
        
        dialog.save_clicked.connect(on_save)
        dialog.discard_clicked.connect(on_discard)
        dialog.cancel_clicked.connect(on_cancel)
        
        dialog.exec()
        return result[0]

    def closeEvent(self, event: QtGui.QCloseEvent):
        """
        윈도우가 닫힐 때 호출되는 이벤트 핸들러입니다.
        
        Args:
            event: 닫기 이벤트
        """
        if hasattr(self, 'temp_config_manager') and self.temp_config_manager.is_exist_temp_config():
            if not self.show_save_dialog():
                event.ignore()
                return
                
        super().closeEvent(event)

    def resizeEvent(self, event: QtGui.QResizeEvent):
        """
        윈도우 크기가 변경될 때 호출되는 이벤트 핸들러입니다.
        
        Args:
            event: 크기 변경 이벤트
        """
        # 부모 클래스의 resizeEvent 호출
        super().resizeEvent(event)
        
        # 현재 윈도우 크기 저장
        if hasattr(self, 'temp_config_manager') and self.temp_config_manager:
            size = self.size()
            self.temp_config_manager._set_window_size(size.width(), size.height())