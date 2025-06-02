import os
from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path
from utils.settings import Settings
from .icon_button import IconButton
import logging
from utils.config import ProjectConfig


class InitWidget(QtWidgets.QWidget):
    """AstroMapper 스타일의 런처 초기화 화면."""
    
    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.setObjectName("initContainer")
        self.project_config = None
        # TODO: 이것도 윈도우 맥 다르게 가야할지 확인
        self.setFixedSize(500, 500)
        self.main_window = main_window 
        self.load_styles(get_resource_path(os.path.join("src", "ui", "styles", "init_widget", "init_widget.qss")))
        self.init_ui()

    def load_styles(self, style_path: str):
        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def init_ui(self):
        """UI 컴포넌트들을 초기화합니다."""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        main_layout.addLayout(self.create_top_layout())
        main_layout.addLayout(self.create_btn_layout())

        recent_label = QtWidgets.QLabel("Recent Projects")
        recent_label.setObjectName("recentTitle")
        self.recent_list = QtWidgets.QListWidget()
        self.recent_list.setObjectName("recentList")
        self.recent_list.itemClicked.connect(self.on_recent_item_clicked)  # 클릭 이벤트 연결
        self.refresh_recent_list()

        main_layout.addWidget(recent_label)

        main_layout.addWidget(self.recent_list)
        main_layout.addStretch(1)

    def create_top_layout(self):
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setSpacing(20)
        # logo
        logo_label = QtWidgets.QLabel()
        logo_path = get_resource_path(os.path.join("res", "images", "Astro.png"))
        logo_pixmap = QtGui.QPixmap(logo_path)
        logo_label.setPixmap(logo_pixmap.scaled(80, 80, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        top_layout.addWidget(logo_label)
        # text
        name_label = QtWidgets.QLabel("AstroMapper")
        name_label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        name_label.setObjectName("appName")
        font = name_label.font()
        font.setPointSize(28)
        font.setBold(True)
        name_label.setFont(font)
        top_layout.addWidget(name_label)
        top_layout.addStretch(1)
        return top_layout

    def create_btn_layout(self):
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(16)
        create_icon = get_resource_path(os.path.join("res", "images", "create_project.png"))
        open_icon = get_resource_path(os.path.join("res", "images", "open_project.png"))
        create_btn = IconButton(create_icon, "Create Project")
        create_btn.clicked.connect(lambda: self.open_project(is_new=True))
        open_btn = IconButton(open_icon, "Open Project")
        open_btn.clicked.connect(lambda: self.open_project(is_new=False))
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(open_btn)
        return btn_layout        

    def refresh_recent_list(self):
        """최근 프로젝트 목록을 새로고침합니다."""
        self.recent_list.clear()
        settings = Settings()
        recent_projects = settings.get_recent_projects()
        for project_dir in recent_projects:
            folder_name = os.path.basename(project_dir)
            parent_path = os.path.dirname(project_dir)
            # 경로 길이 처리
            if len(parent_path) > 30:
                parent_path_display = "..." + parent_path[-30:]
            else:
                parent_path_display = parent_path

            # 커스텀 위젯 생성
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(widget)
            layout.setContentsMargins(8, 2, 8, 2)
            layout.setSpacing(16)

            name_label = QtWidgets.QLabel(folder_name)
            name_label.setObjectName("recentFolder")
            name_label.setProperty("class", "recent-folder")

            path_label = QtWidgets.QLabel(parent_path_display)
            path_label.setObjectName("recentPath")
            path_label.setProperty("class", "recent-path")
            path_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

            layout.addWidget(name_label, 1)
            layout.addWidget(path_label, 2)
            widget.setLayout(layout)

            item = QtWidgets.QListWidgetItem(self.recent_list)
            item.setSizeHint(widget.sizeHint())
            self.recent_list.addItem(item)
            self.recent_list.setItemWidget(item, widget)
            # 실제 경로를 item에 저장
            item.setData(QtCore.Qt.UserRole, project_dir)

    def save_current_project(self):
        # TODO: 여기서 init view가 아닌경우에는 현재 프로젝트 저장할건지 묻기
        if not self.main_window.is_init_view:
            pass
        pass

    def check_project_config(self, project_dir: str, error_msg: str):
        config_path = os.path.join(project_dir, "settings", "project_config.yaml")
        if os.path.exists(config_path):
            self.show_error_msg(error_msg)
            return True
        return False
    
    def check_project_version(self, project_dir: str):
        default_config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "default_config.yaml"))
        config_path = os.path.join(project_dir, "settings", "project_config.yaml")

        with open(default_config_path, 'r', encoding='utf-8') as f:
            default_config = yaml.safe_load(f)
        default_version = default_config.get('project', {}).get('version')
        with open(config_path, 'r', encoding='utf-8') as f:
            loaded_config = yaml.safe_load(f)
        current_version = loaded_config.get('project', {}).get('version')
        if current_version != default_version:
            self.show_error_msg(f"Project version mismatch!\nCurrent: {current_version} / Required: {default_version}\nPlease create a new project.")
            return False
        return True
        
    def show_error_msg(self, error_msg: str):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Error")
        msg_box.setText(error_msg)
        msg_box.exec()

    def initialize_project(self, project_dir: str):
        self.main_window.project_dir = project_dir

        self.main_window.initialize_project_config(ProjectConfig(project_dir))

        # 최근 프로젝트 목록에 추가
        settings = Settings()
        settings.add_recent_project(project_dir)

        # 상태바에 프로젝트 경로 표시 (30자 초과시 앞부분을 ...으로 표시)
        display_path = project_dir
        if len(project_dir) > 30:
            display_path = "..." + project_dir[-30:]
        self.main_window.status_bar.showLeftMessage(f"Project: {display_path}")
        _has_img, _img_settings = self.main_window.project_config.get_image_settings()
        if _has_img:
            self.main_window.image_widget.load_image(_img_settings["path"])
        self.main_window.log_widget.update_log_frame()
        self.main_window.show_project_view_widget()

    def open_project(self, is_new: bool = False, _project_dir: str = None):
        logging.info(f"open_project: {is_new}, {_project_dir}")
        # TODO: make save_current_project
        # 이미 프로젝트가 열려있는 경우도 확인하자.

        # if not self.save_current_project():
            # return 

        if _project_dir and not is_new:
            project_dir = _project_dir
        else:
            project_dir = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select Project Location",
                "",
                QtWidgets.QFileDialog.ShowDirsOnly
            )

        if not project_dir:  # canceled
            return

        if is_new:
            if self.check_project_config(project_dir, "A project already exists in this directory."):
                return
        else:
            if not self.check_project_config(project_dir, "No project exists. Please create a new project."):
                return
            if not self.check_project_version(project_dir):
                return

        if is_new:
            # TODO: settings 폴더 없어지면서 없어질 부분..
            folder_path = os.path.join(project_dir, "settings")
            os.makedirs(folder_path, exist_ok=True)

        self.initialize_project(project_dir)

        if is_new:
            # 프로젝트 하위 폴더 생성
            settings = self.main_window.project_config.get_settings("settings")
            for folder in settings.values():
                if folder == "settings":
                    continue
                folder_path = os.path.join(project_dir, folder)
                os.makedirs(folder_path, exist_ok=True)
            logging.info(f"create project: {project_dir}")

        else:
            # 윈도우/스플리터 크기 복원
            settings_dict = self.main_window.project_config.get_window_size()
            window_width = settings_dict.get("window_width", 1500)
            window_height = settings_dict.get("window_height", 1100)
            image_widget_width = settings_dict.get("image_widget_width", 899)
            log_widget_width = settings_dict.get("log_widget_width", 599)
            self.resize(window_width, window_height)
            # InitView 제거 및 분할 위젯 표시
            self.main_window.project_view_widget.setSizes([image_widget_width, log_widget_width])
            logging.info(f"open project: {project_dir}")

    def on_recent_item_clicked(self, item):
        """최근 프로젝트 아이템 클릭 시 호출되는 메서드입니다."""
        project_dir = item.data(QtCore.Qt.UserRole)
        self.open_recent_project(project_dir)

    def open_recent_project(self, project_dir):
        """최근 프로젝트를 엽니다."""
        if os.path.exists(project_dir):
            self.main_window.open_project(project_dir)


