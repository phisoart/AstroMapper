from typing import Optional
from PySide6 import QtWidgets, QtCore, QtGui
import os
import sys
from ui.widgets import ImageWidget, LogWidget, TitleBar, ToolBar, StatusBar, InitView
from utils.helper import get_resource_path
from utils.settings import Settings
from utils.config import ProjectConfig
from core.roi import ROIs

class AstromapperMainWindow(QtWidgets.QMainWindow):
    """AstroMapper 애플리케이션의 메인 윈도우 클래스입니다."""
    
    def __init__(
        self,
        image_widget: ImageWidget = None,
        log_widget: LogWidget = None,
        parent: Optional[QtWidgets.QWidget] = None
    ):
        """
        메인 윈도우를 초기화합니다.
        
        Args:
            image_widget: 이미지 위젯
            log_widget: 로그 위젯
            parent: 부모 위젯
        """
        super().__init__(parent, QtCore.Qt.FramelessWindowHint)
        
        self.project_dir = None

        self.image_widget = image_widget if image_widget else ImageWidget()
        self.log_widget = log_widget if log_widget else LogWidget()

        self.init_ui()
        self.setup_window_properties()
        self.load_styles()
    
    def init_ui(self):
        """UI 컴포넌트들을 초기화하고 레이아웃을 설정합니다."""
        main_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 타이틀바 추가
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        

        # 중앙 위젯 영역 (윈도우 크기에 맞게 확장)
        self.central_widget = QtWidgets.QWidget()
        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)
        
        # InitView(400x400)를 중앙에 고정
        self.init_view = InitView(main_window=self)
        self.init_view.create_btn.clicked.connect(self.create_project)
        self.init_view.open_btn.clicked.connect(self.open_project)
        self.central_layout.addWidget(self.init_view, alignment=QtCore.Qt.AlignCenter)
        
        # 분할 위젯 생성 (초기에는 숨김)
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)  # 자식 위젯이 완전히 접히지 않도록 설정
        self.splitter.setHandleWidth(2)  # 핸들 너비 설정
        
        # 위젯 추가
        self.image_widget.setMinimumWidth(400)  # 최소 너비 설정
        self.log_widget.setMinimumWidth(280)  # 최소 너비 설정
        self.splitter.addWidget(self.image_widget)
        self.splitter.addWidget(self.log_widget)
        self.splitter.setSizes([600, 400])  # 초기 크기 설정


        self.splitter.hide()
        
        # 스타일시트 다시 로드
        self.image_widget.load_styles()
        self.log_widget.load_styles()
        
        self.central_layout.addWidget(self.splitter)
        main_layout.addWidget(self.central_widget)
        
        # 상태바 추가
        self.status_bar = StatusBar(self)
        main_layout.addWidget(self.status_bar)
        
        self.setCentralWidget(main_widget)

        self.ROIs = ROIs()
        self.ROIs.rois_changed.connect(self.log_widget.on_rois_changed)
        self.image_widget.tool_bar.sameWellToggled.connect(self.ROIs.set_is_same_well)
        self.image_widget.tool_bar.roiToggled.connect(self.image_widget.set_tool_bar_roi_on)
        self.image_widget.ROIs = self.ROIs
        self.log_widget.ROIs = self.ROIs

    
    def load_styles(self):
        """QSS 스타일시트를 로드합니다."""
        style_path = get_resource_path(os.path.join("src", "ui", "styles", "message_box", "critical.qss"))
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.message_box_style = f.read()

    def setup_window_properties(self):
        """윈도우의 기본 속성을 설정합니다."""
        # 윈도우 제목 설정
        self.setWindowTitle("AstroMapper")
        
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
    
    def restore_window_state(self):
        """저장된 윈도우 상태를 복원합니다."""
        settings = QtCore.QSettings("AstroMapper", "MainWindow")
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
    
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
            if hasattr(self, 'splitter'):
                sizes = self.splitter.sizes()
                if len(sizes) >= 2:
                    self.project_config.set_splitter_widths(sizes[0], sizes[1])
            self.project_config.update_last_modified()
            self.save_window_state()
        super().closeEvent(event)

    def open_project(self, _project_dir: str = None):
        # TODO:
        # 정상적인 프로젝트인지 확인하고 세팅값 로딩
        # 지금이 시작지점인지 확인
        # 시작지점 아니라면 저장여부 뭍고 초기화하고 그다음에 open_project
        
        if _project_dir:
            project_dir = _project_dir
        else:
            project_dir = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select Project Location",
                "",
                QtWidgets.QFileDialog.ShowDirsOnly
            )
        
        if not project_dir:  # 사용자가 취소한 경우
            return

        # project_config.yaml 파일이 이미 존재하는지 확인
        config_path = os.path.join(project_dir, "settings", "project_config.yaml")
        if not os.path.exists(config_path):
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Error")
            msg_box.setText("No project exists. Please create a new project.")
            msg_box.setStyleSheet(self.message_box_style)
            # 모든 자식 위젯에 스타일 강제 적용
            for child in msg_box.findChildren(QtWidgets.QWidget):
                child.setStyleSheet(self.message_box_style)
            msg_box.exec()
            return

        # 프로젝트 설정 초기화
        self.project_dir = project_dir
        self.image_widget.project_dir = project_dir

        self.project_config = ProjectConfig(project_dir)
        self.image_widget.project_config = self.project_config
        self.log_widget.project_config = self.project_config
        self.image_widget.tool_bar.project_config = self.project_config
        self.image_widget.tool_bar.update_color_combo()
        # 최근 프로젝트 목록에 추가
        settings = Settings()
        settings.add_recent_project(project_dir)

        # 윈도우/스플리터 크기 복원
        settings_dict = self.project_config.get_window_size()
        window_width = settings_dict.get("window_width", 1500)
        window_height = settings_dict.get("window_height", 1100)
        image_widget_width = settings_dict.get("image_widget_width", 899)
        log_widget_width = settings_dict.get("log_widget_width", 599)
        self.resize(window_width, window_height)
        self.splitter.setSizes([image_widget_width, log_widget_width])

        # InitView 제거
        self.init_view.deleteLater()
        
        # 분할 위젯 표시
        self.splitter.show()
        
        # 상태바에 프로젝트 경로 표시 (30자 초과시 앞부분을 ...으로 표시)
        display_path = project_dir
        if len(project_dir) > 30:
            display_path = "..." + project_dir[-30:]
        self.status_bar.showLeftMessage(f"Project: {display_path}")

        _has_img, _img_settings = self.project_config.get_image_settings()
        if _has_img:
            self.image_widget.load_image(_img_settings["path"])

        self.log_widget.update_log_frame()

    def create_project(self):
        # 지금이 시작지점인지 확인
        # 시작지점 아니라면 저장여부 뭍고 초기화하고 그다음에 create_project
        """새 프로젝트를 생성하고 메인 화면으로 전환합니다."""
        # 프로젝트 폴더 생성
        project_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Project Location",
            "",
            QtWidgets.QFileDialog.ShowDirsOnly
        )
        
        if not project_dir:  # 사용자가 취소한 경우
            return
        
        # project_config.yaml 파일이 이미 존재하는지 확인
        config_path = os.path.join(project_dir, "settings", "project_config.yaml")
        if os.path.exists(config_path):
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Error")
            msg_box.setText("A project already exists in this directory.")
            msg_box.setStyleSheet(self.message_box_style)
            # 모든 자식 위젯에 스타일 강제 적용
            for child in msg_box.findChildren(QtWidgets.QWidget):
                child.setStyleSheet(self.message_box_style)
            msg_box.exec()
            return
            
        # 프로젝트 설정 초기화
        self.project_dir = project_dir
        self.image_widget.project_dir = project_dir

        folder_path = os.path.join(project_dir, "settings")
        os.makedirs(folder_path, exist_ok=True)

        self.project_config = ProjectConfig(project_dir)
        self.image_widget.project_config = self.project_config
        self.log_widget.project_config = self.project_config
        # 프로젝트 하위 폴더 생성
        settings = self.project_config.get_settings("settings")
        for folder in settings.values():
            if folder == "settings":
                continue
            folder_path = os.path.join(project_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
        
        # 최근 프로젝트 목록에 추가
        settings = Settings()
        settings.add_recent_project(project_dir)
        
        # InitView 제거
        self.init_view.deleteLater()
        
        # 분할 위젯 표시
        self.splitter.show()
        
        # 상태바에 프로젝트 정보 표시
        project_info = self.project_config.get_settings("project")
        display_path = project_info["path"]
        if len(display_path) > 30:
            display_path = "..." + display_path[-30:]
        self.status_bar.showLeftMessage(f"Project: {display_path}")

        self.log_widget.update_log_frame()
