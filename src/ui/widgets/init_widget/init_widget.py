import os
from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path
from utils.settings import Settings
from .icon_button import IconButton
from typing import Optional

class InitWidget(QtWidgets.QWidget):
    """AstroMapper 스타일의 런처 초기화 화면."""
    
    def __init__(self, main_window: Optional["AstromapperMainWindow"] = None, project_manager=None, parent=None):
        super().__init__(parent)
        self.setObjectName("initContainer")
        self.project_config = None
        # TODO: 이것도 윈도우 맥 다르게 가야할지 확인
        self.setFixedSize(500, 500)
        self.main_window = main_window
        self.project_manager = project_manager
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
        create_btn.clicked.connect(lambda: self.project_manager.open_project(is_new=True))
        open_btn = IconButton(open_icon, "Open Project")
        open_btn.clicked.connect(lambda: self.project_manager.open_project(is_new=False))
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

    def on_recent_item_clicked(self, item):
        """최근 프로젝트 아이템 클릭 시 호출되는 메서드입니다."""
        project_dir = item.data(QtCore.Qt.UserRole)
        self.project_manager.open_recent_project(project_dir)


