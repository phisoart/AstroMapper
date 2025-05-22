from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path
import os
import json
from core.roi.ROI import ROIs
from ui.dialogs.settings_dialog import SettingsDialog

class LogWidget(QtWidgets.QWidget):
    openImgSignal = QtCore.Signal(bool)  # 사용자 정의 시그널
    subImageChecked = QtCore.Signal(bool)
    subImageSliderChanged = QtCore.Signal(int)
    
    # setImgSignal = QtCore.Signal(str)  # 사용자 정의 시그널
    # updateLogSignal = QtCore.Signal()
    # connectSignal = QtCore.Signal(bool)

    def __init__(self):
        super().__init__()
        self.ROIs = ROIs()
        self.project_config = None
        self.legend_widgets = []  # legend 위젯들을 저장할 리스트 추가

        self.setObjectName("logWidget")
        self.load_styles()
        self.init_ui()

        # openImgSignal이 True일 때 이미지 이름을 로그에 출력
        self.openImgSignal.connect(self.on_image_opened)
        self.sub_image_checkbox.stateChanged.connect(self.on_sub_image_checked)
        self.sub_image_slider.valueChanged.connect(self.on_sub_image_slider_changed)

    def load_styles(self):
        """QSS 스타일시트를 로드합니다."""
        style_path = get_resource_path(os.path.join("src", "ui", "styles", "log_widget.qss"))
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def init_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        main_layout.addLayout(self.create_form_layout())

        # Log Entries 라벨 + Setting 버튼 (오른쪽 끝)
        log_label_layout = QtWidgets.QHBoxLayout()
        log_label = QtWidgets.QLabel("ROIs")
        log_label.setObjectName("logLabel")
        log_label_layout.addWidget(log_label)
        log_label_layout.addStretch(1)
        settings_btn = QtWidgets.QPushButton()
        settings_btn.setIcon(QtGui.QIcon(get_resource_path(os.path.join("res", "images", "icons", "settings.svg"))))
        settings_btn.setIconSize(QtCore.QSize(20, 20))
        settings_btn.setFixedSize(28, 28)
        settings_btn.setStyleSheet("background: transparent; border: none;")
        settings_btn.clicked.connect(self.show_settings_dialog)  # 설정 다이얼로그 연결
        log_label_layout.addWidget(settings_btn)
        main_layout.addLayout(log_label_layout)

        main_layout.addWidget(self.create_log_frame(), stretch=1)

        main_layout.addLayout(self.create_btn_layout())

    def create_form_layout(self):
        # 상단 입력부
        form_layout = QtWidgets.QFormLayout()
        form_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        form_layout.setFormAlignment(QtCore.Qt.AlignLeft)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(8)

        self.image_name_edit = QtWidgets.QLineEdit()
        self.image_name_edit.setReadOnly(True)
        # 배경 투명, 테두리/글자색 조정
        self.image_name_edit.setStyleSheet("background: transparent; color: #fff; font-size: 12px;")

        # Image Name 라벨 및 입력창 테두리 완전 제거
        image_name_label = QtWidgets.QLabel("Image Name:")
        image_name_label.setStyleSheet("border: none; background: transparent; outline: none;")
        self.image_name_edit.setStyleSheet("background: transparent; color: #fff; font-size: 12px; border: none; border-radius: 0px; outline: none;")
        form_layout.addRow(image_name_label, self.image_name_edit)

        sub_image_layout = QtWidgets.QHBoxLayout()
        self.sub_image_checkbox = QtWidgets.QCheckBox()
        self.sub_image_checkbox.setObjectName("subImageCheckBox")
        self.sub_image_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sub_image_slider.setObjectName("subImageSlider")
        self.sub_image_slider.setMinimum(0)
        self.sub_image_slider.setMaximum(100)
        self.sub_image_slider.setValue(50)
        self.sub_image_checkbox.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.sub_image_slider.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        # 슬라이더 좌우 패딩
        sub_image_layout.addWidget(self.sub_image_checkbox)
        sub_image_layout.addSpacing(10)
        sub_image_layout.addWidget(self.sub_image_slider)
        sub_image_layout.addSpacing(10)

        # Sub Image 라벨 및 체크박스/슬라이더 테두리 완전 제거
        sub_image_label = QtWidgets.QLabel("Sub Image:")
        sub_image_label.setStyleSheet("border: none; background: transparent; outline: none;")
        form_layout.addRow(sub_image_label, sub_image_layout)
        return form_layout
    
    def create_log_frame(self):
        # 로그 출력부 (테두리 포함)
        log_frame = QtWidgets.QFrame()
        log_frame.setStyleSheet("border: 2px solid #FFA726; border-radius: 2px; background: #222;")
        log_frame_layout = QtWidgets.QVBoxLayout(log_frame)
        log_frame_layout.setContentsMargins(4, 4, 4, 4)
        log_frame_layout.setAlignment(QtCore.Qt.AlignTop)

        self.legend_layout = self.create_legend_layout()
        log_frame_layout.addLayout(self.legend_layout)

        return log_frame

    def create_legend_layout(self):
        legend_layout = QtWidgets.QVBoxLayout()
        legend_layout.setContentsMargins(0, 0, 0, 0)
        legend_layout.setSpacing(0)
        try:
            with open("res/data/point_info.json", "r", encoding="utf-8") as f:
                point_info = json.load(f)["point_info"]
        except Exception:
            point_info = ["","#", "X", "Y", "Width", "Height", "Well", "Color", "Note", ""]
        # 오른쪽에 더미 성분 추가
        point_info = point_info + [""]
        # Width, Height 이름 변경
        legend_labels = []
        for x in point_info:
            if x == "Width":
                legend_labels.append("W")
            elif x == "Height":
                legend_labels.append("H")
            else:
                legend_labels.append(x)
        self.column_count = len(legend_labels)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter {
                background: transparent !important;
                border: none !important;
            }
            QSplitter::handle {
                background: #aaa !important;
                width: 1px !important;
                margin: 0px !important;
            }
        """)
        self.legend_widgets = []
        for label in legend_labels:
            l = QtWidgets.QLabel(label)
            l.setAlignment(QtCore.Qt.AlignCenter)
            l.setStyleSheet(
                "QLabel {"
                "  color: #ddd !important;"
                "  font-size: 13px !important;"
                # "  font-weight: normal !important;"  # ← 이 줄 추가
                "  background: transparent !important;"
                "  border: none !important;"
                "  min-width: 40px !important;"
                "  min-height: 22px !important;"
                "}"
            )
            splitter.addWidget(l)
            self.legend_widgets.append(l)
        # splitter handle 비활성화(숨김) - 마지막 한 구간만
        handle_count = splitter.count() - 1
        if handle_count > 0:
            handle = splitter.handle(handle_count)
            handle.setEnabled(False)
            handle.setStyleSheet("background: transparent !important;")
        legend_widget_container = QtWidgets.QWidget()
        legend_widget_container.setStyleSheet("border: none !important; background: transparent !important;")
        legend_widget_container.setLayout(QtWidgets.QVBoxLayout())
        legend_widget_container.layout().setContentsMargins(0, 0, 0, 0)
        legend_widget_container.layout().setSpacing(0)
        legend_widget_container.layout().addWidget(splitter)
        legend_layout.addWidget(legend_widget_container)
        # 아래쪽 얇은 흰색 선
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Plain)
        line.setStyleSheet("background: #fff !important; min-height: 1px !important; max-height: 1px !important; border: none !important;")
        legend_layout.addWidget(line)
        return legend_layout

    def update_log_frame(self):
        self.update_legend_widget()
        self.update_rois_widget()

    def update_legend_widget(self):
        self.point_info_visible = self.project_config.get_point_info_visible()
        
        # legend 위젯들의 visible 상태 업데이트
        for i, (widget, is_visible) in enumerate(zip(self.legend_widgets, self.point_info_visible)):
            widget.setVisible(is_visible)
        
        self.legend_layout.update()
    
    def update_rois_widget(self):
        pass

    def create_btn_layout(self):
        # 하단 버튼부
        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Save")
        self.load_btn = QtWidgets.QPushButton("Load")
        self.clear_btn = QtWidgets.QPushButton("Clear")
        for btn in [self.save_btn, self.load_btn, self.clear_btn]:
            btn.setStyleSheet("background: #333; color: #ccc; padding: 6px 18px; border-radius: 4px;")
            btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Save 버튼 클릭 시 update_log_widget 함수 연결
        self.save_btn.clicked.connect(self.update_legend_widget)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.clear_btn)
        return btn_layout
    
    def on_image_opened(self, opened: bool):
        if opened:
            has_image, image_settings = self.project_config.get_image_settings()
            if has_image:
                self.image_name_edit.setText(image_settings['name'])
                # 이미지가 로드되면 체크박스도 자동 체크
                self.sub_image_checkbox.setChecked(True)

    def on_sub_image_checked(self, state):
        self.subImageChecked.emit(self.sub_image_checkbox.isChecked())

    def on_sub_image_slider_changed(self, value):
        self.subImageSliderChanged.emit(value)

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        # 현재 설정값으로 체크박스 상태 설정
        for col, checkbox in dialog.checkboxes.items():
            if self.project_config:
                log_widget_settings = self.project_config.get_settings("log_widget")
                checkbox.setChecked(log_widget_settings.get(col, True))
        
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            # 설정 저장
            if self.project_config:
                log_widget_settings = self.project_config.get_settings("log_widget")
                for col, checkbox in dialog.checkboxes.items():
                    log_widget_settings[col] = checkbox.isChecked()
                self.project_config.config["log_widget"] = log_widget_settings
                self.project_config.save_config()
                self.update_legend_widget()  # 설정 변경 후 레이아웃 업데이트
