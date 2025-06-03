import os
from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path, open_webpage
from ui.dialogs.license_dialog import LicenseDialog
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu
import logging

class TitleBar(QtWidgets.QMenuBar):
    """커스텀 타이틀바 위젯입니다."""
    
    def __init__(self, parent=None, project_manager=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.project_manager = project_manager
        self.load_styles()
        self.init_ui()
        self.drag_position = None
        self.installEventFilter(self)
    
    def load_styles(self):
        """QSS 스타일시트를 로드합니다."""
        style_path = get_resource_path(os.path.join("src", "ui", "styles", "title_bar.qss"))
        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
    
    def init_ui(self):
        """UI 컴포넌트들을 초기화합니다."""
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)
        
        layout.addWidget(self.create_icon_label())
        
        self.create_menusbar()

        layout.addWidget(self.menubar)
        layout.addStretch()

        layout.addLayout(self.create_button_layout())
    
    def create_icon_label(self):
        # 아이콘 추가
        icon_label = QtWidgets.QLabel()
        icon_path = get_resource_path(os.path.join("res", "images", "Astromapper.ico"))
        icon = QtGui.QIcon(icon_path)
        icon_label.setPixmap(icon.pixmap(20, 20))
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        icon_label.setFixedWidth(30)
        return icon_label

    def create_menusbar(self):
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setObjectName("menuBar")
        self.menubar.installEventFilter(self)  # 메뉴바에 이벤트 필터 설치

        # TODO 추후에는 window도 여러개, close window는 윈도우 하나만, Exit은 프로그램 종료
        # exit_action = file_menu.addAction("New Window")
        # exit_action = file_menu.addAction("Close Window")

        self.menubar.addMenu(self.create_project_menu())
        self.menubar.addMenu(self.create_edit_menu())
        self.menubar.addMenu(self.create_protocol_menu())
        self.menubar.addMenu(self.create_view_menu())
        self.menubar.addMenu(self.create_tools_menu())
        self.menubar.addMenu(self.create_help_menu())

    
    def create_project_menu(self):
        self.project_menu = QMenu("Project", self)
        self.create_project_action = QAction("Create Project", self)
        self.create_project_action.setShortcut("Ctrl+N")
        self.project_menu.addAction(self.create_project_action)
        self.create_project_action.triggered.connect(lambda: self.project_manager.open_project(is_new=True))

        self.open_project_action = QAction("Open Project", self)
        self.open_project_action.setShortcut("Ctrl+O")
        self.project_menu.addAction(self.open_project_action)
        self.open_project_action.triggered.connect(lambda: self.project_manager.open_project(is_new=False))

        # Recent Project를 QMenu로 서브메뉴화
        self.recent_project_menu = QMenu("Recent Project", self)
        self.recent_project_menu.aboutToShow.connect(self.update_recent_project_menu)
        self.project_menu.addMenu(self.recent_project_menu)

        self.project_menu.addSeparator()

        self.save_project_action = QAction("Save Project", self)
        self.save_project_action.setShortcut("Ctrl+S")
        self.project_menu.addAction(self.save_project_action)
        self.save_project_action.setEnabled(True)
        self.save_project_action.triggered.connect(self.project_manager.save_current_project)

        self.save_project_as_action = QAction("Save Project As", self)
        self.save_project_as_action.setShortcut("Ctrl+Shift+S")
        self.project_menu.addAction(self.save_project_as_action)
        self.save_project_as_action.setEnabled(False)

        self.project_menu.addSeparator()

        self.exit_action = QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self.window().close)
        self.project_menu.addAction(self.exit_action)

        return self.project_menu

    def update_recent_project_menu(self):
        self.recent_project_menu.clear()
        recent_projects = self.project_manager.settings.get_recent_projects()
        if not recent_projects:
            self.recent_project_menu.addAction("No recent projects found.").setEnabled(False)
        else:
            for project in recent_projects:
                action = QAction(project, self)
                action.triggered.connect(lambda checked, p=project: self.project_manager.open_recent_project(p))
                self.recent_project_menu.addAction(action)

    def create_edit_menu(self):
        self.edit_menu = QMenu("Edit", self)
        
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.edit_menu.addAction(self.undo_action)
        self.undo_action.setEnabled(False)

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut("Ctrl+Y")
        self.edit_menu.addAction(self.redo_action)
        self.redo_action.setEnabled(False)

        self.edit_menu.addSeparator()

        self.cut_action = QAction("Cut", self)
        self.cut_action.setShortcut("Ctrl+X")
        self.edit_menu.addAction(self.cut_action)
        self.cut_action.setEnabled(False)

        self.copy_action = QAction("Copy", self)
        self.copy_action.setShortcut("Ctrl+C")
        self.edit_menu.addAction(self.copy_action)
        self.copy_action.setEnabled(False)

        self.paste_action = QAction("Paste", self)
        self.paste_action.setShortcut("Ctrl+V")
        self.edit_menu.addAction(self.paste_action)
        self.paste_action.setEnabled(False)

        return self.edit_menu

    def create_protocol_menu(self):
        self.protocol_menu = QMenu("Protocol", self)

        self.save_tmp_protocol_action = QAction("Save tmp Protocol", self)
        self.save_tmp_protocol_action.setShortcut("Ctrl+Shift+S")
        self.protocol_menu.addAction(self.save_tmp_protocol_action)
        self.save_tmp_protocol_action.setEnabled(False)

        self.load_tmp_protocol_action = QAction("Load tmp Protocol", self)
        self.load_tmp_protocol_action.setShortcut("Ctrl+Shift+L")
        self.protocol_menu.addAction(self.load_tmp_protocol_action)
        self.load_tmp_protocol_action.setEnabled(False)

        self.protocol_menu.addSeparator()

        self.save_cx_protocol_action = QAction("Save cxProtocol", self)
        self.save_cx_protocol_action.setShortcut("Ctrl+Shift+S")
        self.protocol_menu.addAction(self.save_cx_protocol_action)
        self.save_cx_protocol_action.setEnabled(False)

        self.load_cx_protocol_action = QAction("Load cxProtocol", self)
        self.load_cx_protocol_action.setShortcut("Ctrl+Shift+L")
        self.protocol_menu.addAction(self.load_cx_protocol_action)
        self.load_cx_protocol_action.setEnabled(False)

        return self.protocol_menu

    def create_view_menu(self):
        self.view_menu = QMenu("View", self)
        self.go_to_ref1_action = QAction("Go to Reference Point 1", self)
        self.go_to_ref1_action.setEnabled(False)
        self.view_menu.addAction(self.go_to_ref1_action)

        self.go_to_ref2_action = QAction("Go to Reference Point 2", self)
        self.go_to_ref2_action.setEnabled(False)
        self.view_menu.addAction(self.go_to_ref2_action)

        self.view_menu.addSeparator()

        self.show_ref_points_action = QAction("Show Refererence Points", self)
        self.show_ref_points_action.setEnabled(False)
        self.view_menu.addAction(self.show_ref_points_action)

        return self.view_menu

    def create_tools_menu(self):
        self.tools_menu = QMenu("Tools", self)
        self.tools_menu.setEnabled(False)
        return self.tools_menu

    def create_help_menu(self):
        self.help_menu = QMenu("Help", self)
        self.report_issue_action = QAction("Report Issue", self)
        self.report_issue_action.triggered.connect(lambda: open_webpage("https://meteorbiotech.com/contact-us"))
        self.report_issue_action.setEnabled(False)
        self.help_menu.addAction(self.report_issue_action)

        self.license_action = QAction("View License", self)
        self.license_action.triggered.connect(self.show_license_dialog)
        # self.license_action.setEnabled(False)
        self.help_menu.addAction(self.license_action)
        
        return self.help_menu

    def create_button_layout(self):
        # 우측 버튼들
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(5)
        
        # 최소화 버튼
        min_button = QtWidgets.QPushButton("─")
        min_button.setFixedSize(30, 30)
        min_button.clicked.connect(self.window().showMinimized)
        button_layout.addWidget(min_button)
        
        # 최대화/복원 버튼
        max_button = QtWidgets.QPushButton("□")
        max_button.setFixedSize(30, 30)
        max_button.clicked.connect(self.toggle_maximize)
        button_layout.addWidget(max_button)
        
        # 닫기 버튼
        close_button = QtWidgets.QPushButton("X")
        close_button.setObjectName("closeButton")  # QSS에서 특정 스타일을 적용하기 위한 ID
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.window().close)
        button_layout.addWidget(close_button)
        return button_layout

    def show_license_dialog(self):
        """라이선스 다이얼로그를 표시합니다."""
        logging.info("show_license_dialog")
        dialog = LicenseDialog(self)
        logging.info("end show_license_dialog")

        dialog.exec()
    
    def toggle_maximize(self):
        """윈도우 최대화/복원을 토글합니다."""
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()
    
    def eventFilter(self, obj, event):
        """이벤트 필터를 통해 자식 위젯들의 마우스 이벤트를 처리합니다."""
        # TitleBar와 그 자식 위젯에서만 이벤트 처리
        if obj != self and not self.isAncestorOf(obj):
            return super().eventFilter(obj, event)
            
        if isinstance(obj, QtWidgets.QMenuBar):
            # 메뉴바의 경우, 메뉴가 열려있지 않을 때만 드래그 허용
            if event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() == QtCore.Qt.LeftButton and not self.menubar.activeAction():
                    self.drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
                    return True
            elif event.type() == QtCore.QEvent.MouseMove:
                if event.buttons() == QtCore.Qt.LeftButton and self.drag_position is not None and not self.menubar.activeAction():
                    self.window().move(event.globalPosition().toPoint() - self.drag_position)
                    return True
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                if event.button() == QtCore.Qt.LeftButton:
                    self.drag_position = None
                    return True
        else:
            # 다른 위젯들의 경우 기존 동작 유지
            if event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() == QtCore.Qt.LeftButton:
                    self.drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
                    return True
            elif event.type() == QtCore.QEvent.MouseMove:
                if event.buttons() == QtCore.Qt.LeftButton and self.drag_position is not None:
                    self.window().move(event.globalPosition().toPoint() - self.drag_position)
                    return True
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                if event.button() == QtCore.Qt.LeftButton:
                    self.drag_position = None
                    return True
        return super().eventFilter(obj, event)
