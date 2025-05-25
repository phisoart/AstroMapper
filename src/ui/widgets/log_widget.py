from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path
import os
import json
from core.roi.ROI import ROIs  # ROI 클래스도 import
from ui.dialogs.settings_dialog import SettingsDialog

class LogRowWidget(QtWidgets.QWidget):
    def __init__(self, order, ROI, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.ROI = ROI  # ROI 객체를 멤버로 저장
        self.setMinimumHeight(28)
        self.setObjectName("logRowWidget")
        # 호버 효과를 위한 스타일시트 추가
        self.setStyleSheet("""
            QWidget#logRowWidget {
                background: #222222 !important;
            }
            QWidget#logRowWidget:hover {
                background: #333333 !important;
            }
        """)

        # Well/Color 옵션 로드
        try:
            with open("res/data/well_info.json", "r", encoding="utf-8") as f:
                well_data = json.load(f)
                well_options = well_data.get("96well", [])
        except Exception:
            well_options = ["A01", "B01", "C01", "D01", "E01", "F01", "G01", "H01"]

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setStyleSheet("""
            QSplitter { 
                background: transparent !important; 
                border: none !important; 
            } 
            QSplitter::handle { 
                background: #fff !important; 
                border: none !important; 
                width: 2px; 
            }
        """)

        self.splitter_widgets = []
        # 1. 체크박스
        checkbox = QtWidgets.QCheckBox()
        checkbox.setChecked(ROI.checked)
        checkbox.setStyleSheet("QCheckBox { border: none !important; background: transparent !important; color: #fff !important; }")
        checkbox.setFixedWidth(20)
        splitter.addWidget(checkbox)
        self.splitter_widgets.append(checkbox)
        # 체크박스 변경 시 ROI 데이터에 반영
        checkbox.stateChanged.connect(self.on_check_changed)

        # 2. 정렬 순서
        order_label = QtWidgets.QLabel(str(order))
        order_label.setAlignment(QtCore.Qt.AlignCenter)
        order_label.setStyleSheet("QLabel { border: none !important; background: transparent !important; color: #aaa !important; font-size: 12px !important; font-weight: normal !important; }")
        splitter.addWidget(order_label)
        self.splitter_widgets.append(order_label)

        # 3~6. X, Y, W, H
        x_label = QtWidgets.QLabel(str(ROI.x))
        y_label = QtWidgets.QLabel(str(ROI.y))
        w_label = QtWidgets.QLabel(str(ROI.width))
        h_label = QtWidgets.QLabel(str(ROI.height))
        for num_label in [x_label, y_label, w_label, h_label]:
            num_label.setAlignment(QtCore.Qt.AlignCenter)
            num_label.setStyleSheet("QLabel { border: none !important; background: transparent !important; color: #aaa !important; font-size: 12px !important; font-weight: normal !important; }")
            splitter.addWidget(num_label)
            self.splitter_widgets.append(num_label)

        # 7. Well 콤보박스
        well_combo = QtWidgets.QComboBox()
        well_combo.addItems(well_options)
        well_combo.setCurrentText(ROI.well)
        well_combo.setStyleSheet("""
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
        well_combo.setEditable(True)
        well_combo.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
        self.last_valid_well = ROI.well if ROI.well else well_options[0]
        def validate_well():
            current_text = well_combo.currentText()
            if current_text not in well_options:
                well_combo.blockSignals(True)
                well_combo.setCurrentText(self.last_valid_well)
                well_combo.blockSignals(False)
            else:
                self.last_valid_well = current_text
        well_combo.lineEdit().editingFinished.connect(validate_well)
        def on_text_changed(text):
            if text in well_options:
                self.last_valid_well = text
        well_combo.currentTextChanged.connect(on_text_changed)
        splitter.addWidget(well_combo)
        self.splitter_widgets.append(well_combo)
        # well 변경 시 ROI 데이터에 반영
        well_combo.currentTextChanged.connect(self.on_well_changed)

        # 8. Color 콤보박스
        try:
            with open("res/data/color.json", "r", encoding="utf-8") as f:
                self.color_dict = json.load(f)
        except Exception:
            self.color_dict = {
                "Red": "#FF0000",
                "Green": "#00FF00",
                "Blue": "#0000FF"
            }
        color_combo = QtWidgets.QComboBox()
        color_combo.setMinimumWidth(115)
        color_name = None
        roi_color_hex = ROI.color.name().upper()  # QColor를 hex로 변환
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
            if hex_code.upper() == roi_color_hex:
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
        splitter.addWidget(color_combo)
        self.splitter_widgets.append(color_combo)
        # color 변경 시 ROI.color에 반영
        color_combo.currentTextChanged.connect(self.on_color_changed)

        # 9. Note (QLineEdit)
        note_edit = QtWidgets.QLineEdit(ROI.note)
        note_edit.setStyleSheet("QLineEdit { border: none !important; background: transparent !important; color: #fff !important; }")
        splitter.addWidget(note_edit)
        self.splitter_widgets.append(note_edit)
        # note 변경 시 ROI 데이터에 반영
        note_edit.textChanged.connect(self.on_note_changed)

        # 10. X(삭제) 버튼
        del_btn = QtWidgets.QPushButton("X")
        del_btn.setFixedWidth(24)
        del_btn.setStyleSheet("QPushButton { border: none !important; background: transparent !important; color: #fff !important; }")
        splitter.addWidget(del_btn)
        self.splitter_widgets.append(del_btn)

        layout.addWidget(splitter)
        self.splitter = splitter

    def on_check_changed(self, state):
        self.ROI.checked = bool(state)
        if self.parent_widget is not None and hasattr(self.parent_widget, "updateImgSignal"):
            self.parent_widget.updateImgSignal.emit(True)

    def on_well_changed(self, text):
        self.ROI.well = text

    def on_note_changed(self, text):
        self.ROI.note = text

    def on_color_changed(self, color_name):
        hex_code = self.color_dict.get(color_name, "#FF0000")
        self.ROI.color = QtGui.QColor(hex_code)
        self.ROI.color_name = color_name
        if self.parent_widget is not None and hasattr(self.parent_widget, "updateImgSignal"):
            self.parent_widget.updateImgSignal.emit(True)

class LogWidget(QtWidgets.QWidget):
    openImgSignal = QtCore.Signal(bool)  # 사용자 정의 시그널
    subImageChecked = QtCore.Signal(bool)
    subImageSliderChanged = QtCore.Signal(int)
    updateImgSignal = QtCore.Signal(bool)


    # setImgSignal = QtCore.Signal(str)  # 사용자 정의 시그널
    # updateLogSignal = QtCore.Signal()
    # connectSignal = QtCore.Signal(bool)

    def __init__(self):
        super().__init__()
        self.ROIs = ROIs()        
        
        self.project_config = None
        self.legend_widgets = []
        self.log_rows = []

        # 전체 위젯 및 주요 성분 테두리 제거 스타일 적용
        self.setStyleSheet('''
            QWidget#logWidget, QFrame, QSplitter, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox {
                border: none !important;
                outline: none !important;
                background: transparent;
            }
            QSplitter::handle {
                background: #fff !important;
                border: none !important;
            }
            QWidget#logRowWidget {
                background: transparent;
            }
            QWidget#logRowWidget:hover {
                background: #333333;
            }
        ''')
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
        log_frame = QtWidgets.QFrame()
        log_frame.setStyleSheet("border: 2px solid #FFA726; border-radius: 2px; background: #222;")
        log_frame_layout = QtWidgets.QVBoxLayout(log_frame)
        log_frame_layout.setContentsMargins(4, 4, 4, 4)
        log_frame_layout.setAlignment(QtCore.Qt.AlignTop)

        self.legend_layout = self.create_legend_layout()
        log_frame_layout.addLayout(self.legend_layout)

        # 로그 row 영역 (스크롤)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none !important; background: transparent !important; } QScrollBar { border: none !important; background: #222 !important; }")
        scroll_widget = QtWidgets.QWidget()
        scroll_widget.setStyleSheet("QWidget { border: none !important; background: transparent !important; }")

        self.scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)
        self.scroll_layout.addStretch()
        scroll_widget.setLayout(self.scroll_layout)
        scroll_area.setWidget(scroll_widget)
        log_frame_layout.addWidget(scroll_area)

        # 스크롤바 이벤트 연결
        scroll_area.verticalScrollBar().rangeChanged.connect(self.on_scrollbar_range_changed)

        return log_frame

    def create_legend_layout(self):
        legend_layout = QtWidgets.QVBoxLayout()
        legend_layout.setContentsMargins(0, 0, 0, 0)
        legend_layout.setSpacing(0)
        try:
            with open("res/data/point_info.json", "r", encoding="utf-8") as f:
                point_info = json.load(f)["point_info"]
        except Exception:
            point_info = ["checkbox", "#", "X", "Y", "Width", "Height", "Well", "Color", "Note", "Delete"]
        # 오른쪽에 더미 성분 추가
        point_info = point_info
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

        self.legend_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.legend_splitter.setStyleSheet("""
            QSplitter {
                background: transparent !important;
                border: none !important;
            }
            QSplitter::handle {
                background: #fff !important;
                width: 2px !important;
                margin: 0px !important;
            }
        """)
        for label in legend_labels:
            if label == "checkbox":
                l = QtWidgets.QLabel()
                l.setFixedWidth(20)
                l.setStyleSheet(
                "QLabel {"
                "  color: #aaa !important;"
                "  font-size: 12px !important;"
                "  font-weight: normal !important;"
                "  background: transparent !important;"
                "  border: none !important;"
                "  min-height: 22px !important;"
                "}"
            )
            elif label == "Delete":
                l = QtWidgets.QLabel()
                l.setFixedWidth(24)
                l.setStyleSheet(
                "QLabel {"
                "  color: #aaa !important;"
                "  font-size: 12px !important;"
                "  font-weight: normal !important;"
                "  background: transparent !important;"
                "  border: none !important;"
                "  min-height: 22px !important;"
                "}"
            )
            elif label == "Color":
                l = QtWidgets.QLabel(label)
                l.setAlignment(QtCore.Qt.AlignCenter)
                l.setStyleSheet(
                "QLabel {"
                "  color: #aaa !important;"
                "  font-size: 12px !important;"
                "  font-weight: normal !important;"
                "  background: transparent !important;"
                "  border: none !important;"
                "  min-width: 115px !important;"
                "  min-height: 22px !important;"
                "}"
            )
            else:
                l = QtWidgets.QLabel(label)
                l.setAlignment(QtCore.Qt.AlignCenter)
                l.setStyleSheet(
                "QLabel {"
                "  color: #aaa !important;"
                "  font-size: 12px !important;"
                "  font-weight: normal !important;"
                "  background: transparent !important;"
                "  border: none !important;"
                "  min-width: 40px !important;"
                "  min-height: 22px !important;"
                "}"
            )

            self.legend_splitter.addWidget(l)
            self.legend_widgets.append(l)
        # splitter handle 비활성화(숨김) - 첫 번째, 마지막 한 구간
        handle_count = self.legend_splitter.count() - 1
        if handle_count > 0:
            # 첫 번째 handle (index=1)
            first_handle = self.legend_splitter.handle(1)
            first_handle.setEnabled(False)
            first_handle.setStyleSheet("background: transparent !important;")
            # 마지막 handle (index=handle_count)
            last_handle = self.legend_splitter.handle(handle_count)
            last_handle.setEnabled(False)
            last_handle.setStyleSheet("background: transparent !important;")
        legend_layout.addWidget(self.legend_splitter)
        # 아래쪽 얇은 흰색 선
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Plain)
        line.setStyleSheet("background: #fff !important; min-height: 1px !important; max-height: 1px !important; border: none !important;")
        legend_layout.addWidget(line)
        # splitter moved 시 row splitter 동기화
        self.legend_splitter.splitterMoved.connect(self.sync_row_splitters)
        self.legend_splitter.splitterMoved.connect(self.save_legend_widths)
        return legend_layout

    def sync_row_splitters(self, pos, index):
        sizes = self.legend_splitter.sizes()
        for row in getattr(self, 'log_rows', []):
            row.splitter.blockSignals(True)
        for row in getattr(self, 'log_rows', []):
            row.splitter.setSizes(sizes)
        for row in getattr(self, 'log_rows', []):
            row.splitter.blockSignals(False)

    def update_log_frame(self):
        self.apply_saved_legend_widths()
        self.update_legend_widget()
        self.update_rois_widget()

    def update_legend_widget(self):
        self.point_info_visible = self.project_config.get_point_info_visible()

        # legend 위젯들의 visible 상태 업데이트
        for i, (widget, is_visible) in enumerate(zip(self.legend_widgets, self.point_info_visible)):
            widget.setVisible(is_visible)
        
        self.legend_layout.update()
        QtWidgets.QApplication.processEvents()  # UI 갱신    

    def update_rois_widget(self):
        """
        legend splitter의 크기, log row splitter의 크기, visible 상태를 모두 동기화합니다.
        숨겨진 컬럼의 width는 0으로 강제합니다.
        """
        if hasattr(self, 'legend_splitter') and hasattr(self, 'log_rows'):
            sizes = self.legend_splitter.sizes()
            print(f"sizes: {sizes}")
            point_info_visible = self.project_config.get_point_info_visible() if self.project_config else [True] * len(self.legend_widgets)
            # 숨겨진 컬럼 width는 0으로
            adjusted_sizes = [size if vis else 0 for size, vis in zip(sizes, point_info_visible)]
            for row in self.log_rows:
                row.splitter.setSizes(adjusted_sizes)
                if hasattr(row, 'splitter_widgets'):
                    for i, (widget, is_visible) in enumerate(zip(row.splitter_widgets, point_info_visible)):
                        widget.setVisible(is_visible)
                row.splitter.update()

    def apply_saved_legend_widths(self):
        if self.project_config:
            widths = self.project_config.get_log_widget_widths()
            if widths:
                self.legend_splitter.setSizes(widths)
                sizes = self.legend_splitter.sizes()
                for row in getattr(self, 'log_rows', []):
                    row.splitter.setSizes(widths)

    def save_legend_widths(self):
        if self.project_config:
            # TODO: 저장 기능 추가
            self.project_config.set_log_widget_widths(self.legend_splitter.sizes())

    def create_btn_layout(self):
        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Save")
        self.load_btn = QtWidgets.QPushButton("Load")
        self.clear_btn = QtWidgets.QPushButton("Clear")
        for btn in [self.save_btn, self.load_btn, self.clear_btn]:
            btn.setStyleSheet("background: #333; color: #ccc; padding: 6px 18px; border-radius: 4px;")
            btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.on_save_clicked)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.clear_btn)
        return btn_layout

    def on_save_clicked(self):
        print(self.ROIs.getROIs())
        # self.save_legend_widths()
        # self.update_log_frame()

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
                # TODO: 저장 기능 추가
                self.project_config.save_config()
                self.update_log_frame()

    def on_scrollbar_range_changed(self, min_val, max_val):
        sizes = self.legend_splitter.sizes()
        if len(sizes) < 1:
            return
            
        last_widget = self.legend_widgets[-1]
        
        if min_val == max_val:
            # 스크롤바가 사라짐
            last_widget.setFixedWidth(24)
        else:
            # 스크롤바가 나타남
            last_widget.setFixedWidth(36)
            
    def resizeEvent(self, event):
        """위젯 크기가 변경될 때 호출되는 이벤트 핸들러"""
        super().resizeEvent(event)
        # 크기 변경 시 row splitter 동기화
        if hasattr(self, 'legend_splitter'):
            self.sync_row_splitters(0, 0)  # pos와 index는 사용하지 않으므로 0으로 설정
            
    def on_rois_changed(self):        
        # # 2. 로그 엔트리 업데이트
        self.update_log_entries() 
        # # 3. 변경 사항 저장 (필요한 경우)
        # self.save_rois_state()

    def update_log_entries(self):
        """ROIs의 정보로 로그 엔트리를 업데이트합니다."""
        # 1. 기존 위젯/스페이서 모두 제거
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.log_rows.clear()

        # 2. 새로운 로그 엔트리 추가
        for i, roi in enumerate(self.ROIs.getROIs()):
            row = LogRowWidget(i+1, roi, parent=self)
            for j in range(row.splitter.count() - 1):
                handle = row.splitter.handle(j + 1)
                handle.setEnabled(False)
                handle.setStyleSheet("background: transparent !important;")
            row.splitter.setSizes(self.legend_splitter.sizes())
            self.log_rows.append(row)
            self.scroll_layout.addWidget(row)

        # 3. 마지막에 stretch 한 번만 추가
        self.scroll_layout.addStretch()

    # def save_rois_state(self):
    #     # TODO: 저장 기능 추가
    #     self.project_config.set_rois(self.ROIs.getROIs())
    #     self.project_config.save_config()

    