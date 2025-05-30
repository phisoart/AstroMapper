from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path
import os
import json
from core.roi.ROI import ROIs, ROI  # ROI 클래스도 import
from ui.dialogs.settings_dialog import SettingsDialog
from .clickable_label import ClickableLabel
from .log_row_widget import LogRowWidget
from ui.dialogs.reference_point_dialog import ReferencePointDialog

class LogWidget(QtWidgets.QWidget):
    openImgSignal = QtCore.Signal(bool)  # 사용자 정의 시그널
    subImageChecked = QtCore.Signal(bool)
    subImageSliderChanged = QtCore.Signal(int)
    updateImgSignal = QtCore.Signal(bool)
    appendROISignal = QtCore.Signal(ROI)
    removeROISignal = QtCore.Signal(ROI)
    clearROISignal = QtCore.Signal()
    moveImageSignal = QtCore.Signal(int, int)

    # setImgSignal = QtCore.Signal(str)  # 사용자 정의 시그널
    # updateLogSignal = QtCore.Signal()
    # connectSignal = QtCore.Signal(bool)

    def __init__(self, ROIs):
        super().__init__()
        self.ROIs = ROIs      
        
        self.project_config = None
        self.legend_widgets = []
        self.log_rows = []
        self.selected_rows = []
        self.sort_states = {}  # {col_idx: True(asc)/False(desc)}
        self.sort_col = None
        style_path = get_resource_path(os.path.join("src", "ui", "styles", "message_box", "critical.qss"))
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.message_box_style = f.read()

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


        reference_point_layout = QtWidgets.QHBoxLayout()
        reference_point_label = QtWidgets.QLabel("Reference Points:")
        reference_point_label.setStyleSheet("border: none; background: transparent; outline: none;")
        reference_point_set_btn = QtWidgets.QPushButton("Set")
        reference_point_set_btn.setFixedHeight(28)
        reference_point_set_btn.setFixedWidth(50)
        reference_point_set_btn.setStyleSheet("""
            QPushButton {
                background: #444; color: #fff; border-radius: 6px; padding: 0 16px 0 12px !important; border: none;
            }
            QPushButton:hover {
                background: #666;
            }
            QPushButton:pressed {
                background: #222;
            }
        """)
        reference_point_set_btn.clicked.connect(self.show_reference_point_dialog)
        reference_point_status = QtWidgets.QLabel("Status: X")  
        # reference_point_status.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        reference_point_status.setStyleSheet("color: #fff; border: none; background: transparent;")
        reference_point_layout.addWidget(reference_point_set_btn)
        reference_point_layout.addWidget(reference_point_status)
        form_layout.addRow(reference_point_label, reference_point_layout)

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
            point_info_path = get_resource_path(os.path.join("res", "data", "point_info.json"))
            with open(point_info_path, "r", encoding="utf-8") as f:
                point_info = json.load(f)["point_info"]
        except Exception:
            point_info = ["checkbox", "#", "X", "Y", "Width", "Height", "Well", "Color", "Note", "Delete"]

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
        sortable_indices = [0, 2, 3, 4, 5, 6, 7, 8]  # checkbox, x, y, w, h, well, color, note
        self.legend_widgets = []
        for idx, label in enumerate(legend_labels):
            if idx in sortable_indices:
                if label == "checkbox" or label == "Delete":
                    l = ClickableLabel("", idx)
                else:
                    l = ClickableLabel(label, idx)
                l.clicked.connect(self.on_legend_clicked)
            else:
                if label == "checkbox" or label == "Delete":
                    l = QtWidgets.QLabel("")
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
                "  min-height: 22px !important;"
                "}"
            )
            if label == "checkbox":
                l.setFixedWidth(20)
            elif label == "Delete":
                l.setFixedWidth(24)
            elif label == "Color":
                l.setMinimumWidth(115)
            else:
                l.setMinimumWidth(40)
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
                for row in getattr(self, 'log_rows', []):
                    row.splitter.setSizes(widths)

    def save_legend_widths(self):
        if self.project_config:
            # TODO: 저장 기능 추가
            self.project_config.set_log_widget_widths(self.legend_splitter.sizes())

    def create_btn_layout(self):
        btn_layout = QtWidgets.QHBoxLayout()
        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.clicked.connect(self.on_save_clicked)
        self.load_btn = QtWidgets.QPushButton("Load")
        self.load_btn.clicked.connect(self.on_load_clicked)
        self.clear_btn = QtWidgets.QPushButton("Clear")
        self.clear_btn.clicked.connect(self.on_clear_clicked)
        for btn in [self.save_btn, self.load_btn, self.clear_btn]:
            btn.setStyleSheet("background: #333; color: #ccc; padding: 6px 18px; border-radius: 4px;")
            btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.clear_btn)
        return btn_layout

    def on_save_clicked(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        # project_path를 기본 경로로 사용
        default_dir = ""
        if self.project_config is not None:
            if hasattr(self.project_config, 'project_path'):
                default_dir = self.project_config.project_path
            elif hasattr(self.project_config, 'get'):
                default_dir = self.project_config.get('project_path', "")
        default_dir = os.path.join(default_dir, "results")
        # results/tmp 폴더가 없으면 생성
        tmp_dir = os.path.join(default_dir, "tmp")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir, exist_ok=True)
        default_dir = tmp_dir
        _file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save file",
            default_dir,
            "Temp Protocol File (*.tmpprotocol);",
            options=options,
        )
        if _file_name:
            with open(_file_name, "w") as file:
                # 이미지 정보 저장
                has_image, image_settings = self.project_config.get_image_settings() if self.project_config else (False, None)
                if has_image and image_settings:
                    file.write("[IMG]\n")
                    file.write(f"name = {image_settings.get('name', '')}\n")
                    file.write(f"size = {image_settings.get('width', '')}x{image_settings.get('height', '')}\n")
                    file.write(f"format = {image_settings.get('format', '')}\n")
                    file.write(f"filesize = {image_settings.get('size', '')}\n\n")

                file.write("[ROIs]\n")
                _l = self.ROIs.__len__()
                _str = "n = " + str(_l) + "\n"
                file.write(_str)
                for i in range(_l):
                    # P_51 = "7.975;10.975;8.025;11.025;E04;Red;TNBC;1"
                    _roi = self.ROIs.getROI(i)
                    _str = "P_"
                    _str += str(i) + " = "
                    _str += str(_roi.x) + ";"
                    _str += str(_roi.y) + ";"
                    _str += str(_roi.width) + ";"
                    _str += str(_roi.height) + ";"
                    _str += str(_roi.well) + ";"
                    _str += str(_roi.color_name) + ";"
                    _str += str(_roi.note) + ";"
                    _str += "1" if _roi.checked else "0"
                    _str += ";\n"

                    file.write(_str)

    def on_load_clicked(self):
        default_dir = ""
        if self.project_config is not None:
            if hasattr(self.project_config, 'project_path'):
                default_dir = self.project_config.project_path
            elif hasattr(self.project_config, 'get'):
                default_dir = self.project_config.get('project_path', "")
        default_dir = os.path.join(default_dir, "results")
        # results/tmp 폴더가 없으면 생성
        tmp_dir = os.path.join(default_dir, "tmp")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir, exist_ok=True)

        # Show the file dialog to select a file
        self.file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open tmp protocol", tmp_dir, "tmp protocol Files (*.tmpprotocol)"
        )
        if self.file_name:
            try:
                with open(self.file_name, "r", encoding="utf-8") as file:
                    content = file.read()
                # [IMG] 섹션 파싱
                img_section = content.split('[IMG]')[1].split('[ROIs]')[0].strip()
                img_info = {}
                for line in img_section.splitlines():
                    if '=' in line:
                        k, v = line.split('=', 1)
                        img_info[k.strip()] = v.strip()
                # 현재 이미지 정보와 비교
                has_image, image_settings = self.project_config.get_image_settings() if self.project_config else (False, None)
                if not has_image or not image_settings:
                    msg_box = QtWidgets.QMessageBox(self)
                    msg_box.setWindowTitle("Error")
                    msg_box.setText("No image loaded in project.")
                    msg_box.setStyleSheet(self.message_box_style)
                    # 모든 자식 위젯에 스타일 강제 적용
                    for child in msg_box.findChildren(QtWidgets.QWidget):
                        child.setStyleSheet(self.message_box_style)
                    msg_box.exec()
                    return
                # 비교: 이름, 사이즈, 포맷, 용량
                cur_name = str(image_settings.get('name', ''))
                cur_size = f"{image_settings.get('width', '')}x{image_settings.get('height', '')}"
                cur_format = str(image_settings.get('format', ''))
                cur_filesize = str(image_settings.get('size', ''))
                if not (img_info.get('name') == cur_name and img_info.get('size') == cur_size and img_info.get('format') == cur_format and img_info.get('filesize') == cur_filesize):
                    msg_box = QtWidgets.QMessageBox(self)
                    msg_box.setWindowTitle("Error")
                    msg_box.setText("Image info in protocol file does not match current project!\n\nCurrent: {} {} {} {}\nFile: {} {} {} {}".format(cur_name, cur_size, cur_format, cur_filesize, img_info.get('name'), img_info.get('size'), img_info.get('format'), img_info.get('filesize')))
                    msg_box.setStyleSheet(self.message_box_style)
                    # 모든 자식 위젯에 스타일 강제 적용
                    for child in msg_box.findChildren(QtWidgets.QWidget):
                        child.setStyleSheet(self.message_box_style)
                    msg_box.exec()
                    return
                # [ROIs] 섹션 파싱
                rois_section = content.split('[ROIs]')[1].strip()
                lines = rois_section.splitlines()
                n = 0
                for line in lines:
                    if line.startswith('n ='):
                        n = int(line.split('=')[1].strip())
                        break
                self.ROIs.clearROIs()
                for line in lines:
                    if line.startswith('P_'):
                        # P_0 = 157;135;90;90;A01;Red;1;1;
                        parts = line.split('=', 1)[1].strip().split(';')
                        if len(parts) < 8:
                            continue
                        x = int(parts[0])
                        y = int(parts[1])
                        w = int(parts[2])
                        h = int(parts[3])
                        well = parts[4]
                        color_name = parts[5]
                        note = parts[6]
                        checked = parts[7] == '1'
                        roi = ROI()
                        roi.x = x
                        roi.y = y
                        roi.width = w
                        roi.height = h
                        roi.rect = QtCore.QRect(x, y, w, h)
                        roi.well = well
                        roi.color_name = color_name
                        roi.color = QtGui.QColor(self.color_dict.get(color_name, "#FF0000"))
                        roi.note = note
                        roi.checked = checked
                        self.ROIs.appendROI(roi)
                # self.update_log_entries()
                self.updateImgSignal.emit(True)
            except Exception as e:
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle("Error")
                msg_box.setText(f"Failed to load protocol file: {e}")
                msg_box.setStyleSheet(self.message_box_style)
                msg_box.exec()

    def on_clear_clicked(self):
        self.clearROISignal.emit()
        self.ROIs.clearROIs()
        self.updateImgSignal.emit(True)

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
            row.selectedChanged.connect(self.on_row_selected)
            row.centerToROI.connect(self.on_center_to_roi)
            self.log_rows.append(row)
            self.scroll_layout.addWidget(row)

        # 3. 마지막에 stretch 한 번만 추가
        self.scroll_layout.addStretch()

    # def save_rois_state(self):
    #     # TODO: 저장 기능 추가
    #     self.project_config.set_rois(self.ROIs.getROIs())
    #     self.project_config.save_config()

    def show_reference_point_dialog(self):
        dialog = ReferencePointDialog(self)
        dialog.exec()

    def on_row_selected(self, row_widget, modifiers):
        if modifiers == QtCore.Qt.ControlModifier:
            # Ctrl: 토글 선택
            if row_widget in self.selected_rows:
                self.selected_rows.remove(row_widget)
                row_widget.set_selected(False)
            else:
                self.selected_rows.append(row_widget)
                row_widget.set_selected(True)
        elif modifiers == QtCore.Qt.ShiftModifier and self.selected_rows:
            # Shift: 범위 선택
            last_idx = self.log_rows.index(self.selected_rows[-1])
            this_idx = self.log_rows.index(row_widget)
            start, end = sorted([last_idx, this_idx])
            for i in range(start, end+1):
                r = self.log_rows[i]
                if r not in self.selected_rows:
                    self.selected_rows.append(r)
                    r.set_selected(True)
        else:
            # 단일 선택
            for r in self.selected_rows:
                r.set_selected(False)
            self.selected_rows = [row_widget]
            row_widget.set_selected(True)
        # 선택된 row들의 index 출력
        selected_indices = [self.log_rows.index(r) for r in self.selected_rows]
        print(f"선택된 row index: {selected_indices}")

    def show_row_context_menu(self, clicked_row, global_pos):
        # If the right-clicked row is not selected, select only that row
        if clicked_row not in self.selected_rows:
            for r in self.selected_rows:
                r.set_selected(False)
            self.selected_rows = [clicked_row]
            clicked_row.set_selected(True)
        if clicked_row and clicked_row in self.selected_rows:
            menu = QtWidgets.QMenu(self)
            # 0. Check/Uncheck (based on first row)
            first_checked = self.selected_rows[0].ROI.checked
            check_action = menu.addAction("Check" if not first_checked else "Uncheck")
            # 1. Delete
            delete_action = menu.addAction("Delete selected ROI(s)")
            # 2. Color change (from color_dict)
            color_menu = menu.addMenu("Change Color")
            color_action_map = {}
            for color_name, color_hex in self.color_dict.items():
                color_action = QtGui.QAction(color_name, self)
                pixmap = QtGui.QPixmap(16, 16)
                pixmap.fill(QtGui.QColor(color_hex))
                color_action.setIcon(QtGui.QIcon(pixmap))
                color_menu.addAction(color_action)
                color_action_map[color_action] = (color_name, color_hex)
            # 3. Well change (from well list)
            well_menu = menu.addMenu("Change Well")
            try:
                from utils.helper import get_resource_path
                import os, json
                well_info_path = get_resource_path(os.path.join("res", "data", "well_info.json"))
                with open(well_info_path, "r", encoding="utf-8") as f:
                    well_data = json.load(f)
                    well_options = well_data.get("96well", [])
            except Exception:
                well_options = ["A01", "B01", "C01", "D01", "E01", "F01", "G01", "H01"]
            well_action_map = {}
            for well in well_options:
                well_action = QtGui.QAction(well, self)
                well_menu.addAction(well_action)
                well_action_map[well_action] = well
            # 4. Note change (input dialog)
            note_action = menu.addAction("Change Note...")
            action = menu.exec(global_pos)
            # 0. Check/Uncheck
            if action == check_action:
                new_checked = not first_checked
                for row in self.selected_rows:
                    row.ROI.checked = new_checked
                    if hasattr(row.splitter_widgets[0], 'setChecked'):
                        row.splitter_widgets[0].setChecked(new_checked)
            # 1. Delete
            elif action == delete_action:
                for row in list(self.selected_rows):
                    idx = self.log_rows.index(row)
                    self.ROIs.removeROI(idx)
                self.update_log_entries()
            # 2. Color change
            elif action in color_action_map:
                color_name, color_hex = color_action_map[action]
                for row in self.selected_rows:
                    row.ROI.color = QtGui.QColor(color_hex)
                    row.ROI.color_name = color_name
                    if hasattr(row.splitter_widgets[7], 'setCurrentText'):
                        row.splitter_widgets[7].setCurrentText(color_name)
            # 3. Well change
            elif action in well_action_map:
                well_name = well_action_map[action]
                for row in self.selected_rows:
                    row.ROI.well = well_name
                    if hasattr(row.splitter_widgets[6], 'setCurrentText'):
                        row.splitter_widgets[6].setCurrentText(well_name)
            # 4. Note change
            elif action == note_action:
                text, ok = QtWidgets.QInputDialog.getText(self, "Batch Change Note", "Enter new note value:")
                if ok:
                    for row in self.selected_rows:
                        row.ROI.note = text
                        if hasattr(row.splitter_widgets[8], 'setText'):
                            row.splitter_widgets[8].setText(text)

    def on_center_to_roi(self, x, y):
        # TODO: 실제 이미지 이동 함수와 연결
        print(f"Move image center to: ({x}, {y})")
        self.moveImageSignal.emit(x, y)

    def on_legend_clicked(self, col_idx):
        # 정렬 방향 토글
        prev_state = self.sort_states.get(col_idx, False)
        self.sort_states[col_idx] = not prev_state
        self.sort_col = col_idx
        self.sort_and_update_rows()
        self.update_legend_sort_indicator()

    def sort_and_update_rows(self):
        # 정렬 기준 매핑: idx -> ROI 속성
        idx_to_attr = {
            0: lambda roi: roi.checked,  # checkbox
            2: lambda roi: roi.x,
            3: lambda roi: roi.y,
            4: lambda roi: roi.width,
            5: lambda roi: roi.height,
            6: lambda roi: roi.well,
            7: lambda roi: roi.color_name,
            8: lambda roi: roi.note,
        }
        if self.sort_col not in idx_to_attr:
            return
        reverse = not self.sort_states[self.sort_col]
        # ROIs 내부 리스트를 직접 정렬하고, 그 결과를 받아 row 재생성
        self.ROIs.sort(key_func=idx_to_attr[self.sort_col], reverse=reverse)
        self.update_log_entries()
        # splitter width 동기화
        self.sync_row_splitters(0, 0)

    def update_legend_sort_indicator(self):
        # 정렬 방향 표시(▲/▼)
        for idx, label in enumerate(self.legend_widgets):
            if isinstance(label, ClickableLabel):
                base_text = label.text().replace(" ▲", "").replace(" ▼", "")
                if idx == self.sort_col:
                    arrow = " ▲" if self.sort_states.get(idx, True) else " ▼"
                    label.setText(base_text + arrow)
                else:
                    label.setText(base_text)

    