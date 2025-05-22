import os
from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path, open_webpage
from ui.dialogs.license_dialog import LicenseDialog

class TitleBar(QtWidgets.QWidget):
    """커스텀 타이틀바 위젯입니다."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(30)
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
        
        # 아이콘 추가
        icon_label = QtWidgets.QLabel()
        icon_path = get_resource_path(os.path.join("res", "images", "Astromapper.ico"))
        icon = QtGui.QIcon(icon_path)
        icon_label.setPixmap(icon.pixmap(20, 20))
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        icon_label.setFixedWidth(30)
        layout.addWidget(icon_label)
        
        # 메뉴바 추가
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setObjectName("menuBar")
        self.menubar.installEventFilter(self)  # 메뉴바에 이벤트 필터 설치
        self.setup_menus()
        layout.addWidget(self.menubar)
        layout.addStretch()
        
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
        
        layout.addLayout(button_layout)
    
    def setup_menus(self):
        """메뉴바의 메뉴들을 설정합니다."""
        # 파일 메뉴
        file_menu = self.menubar.addMenu("Project")
        new_action = file_menu.addAction("Create Project")
        new_action.setShortcut("Ctrl+N")
        open_action = file_menu.addAction("Open Project")
        open_action.setShortcut("Ctrl+O")
        file_menu.addSeparator()
        save_action = file_menu.addAction("Save Project")
        save_action.setShortcut("Ctrl+S")
        save_as_action = file_menu.addAction("Save Project As")
        save_as_action.setShortcut("Ctrl+Shift+S")
        # TODO 추후에는 window도 여러개, close window는 윈도우 하나만, Exit은 프로그램 종료
        # exit_action = file_menu.addAction("New Window")
        # exit_action = file_menu.addAction("Close Window")

        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.window().close)
        
        # 도움말 메뉴
        help_menu = self.menubar.addMenu("Help")
        report_action = help_menu.addAction("Report Issue")
        report_action.triggered.connect(lambda: open_webpage("https://meteorbiotech.com/contact-us"))
        license_action = help_menu.addAction("View License")
        license_action.triggered.connect(self.show_license_dialog)
    
    def show_license_dialog(self):
        """라이선스 다이얼로그를 표시합니다."""
        dialog = LicenseDialog(self)
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