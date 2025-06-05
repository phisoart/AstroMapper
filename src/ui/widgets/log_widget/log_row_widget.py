from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path
import os
import json


class LogRowWidget(QtWidgets.QWidget):
    selectedChanged = QtCore.Signal(object, object)  # (self, modifiers)
    centerToROI = QtCore.Signal(int, int)  # x, y 중심 좌표
    def __init__(self, order, ROI, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.ROI = ROI  # ROI 객체를 멤버로 저장
        self.selected = False
        self.setMinimumHeight(28)
        self.setObjectName("logRowWidget")
        self.setCursor(QtCore.Qt.PointingHandCursor)
        # 호버 효과를 위한 스타일시트 추가
        self.setStyleSheet("""
            QWidget#logRowWidget {
                background: #222222 !important;
                border: none !important;
            }
            QWidget#logRowWidget:hover {
                background: #333333 !important;
            }
        """)

        # Well/Color 옵션 로드
        try:
            well_info_path = get_resource_path(os.path.join("res", "data", "well_info.json"))
            with open(well_info_path, "r", encoding="utf-8") as f:
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
            color_info_path = get_resource_path(os.path.join("res", "data", "color.json"))
            with open(color_info_path, "r", encoding="utf-8") as f:
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
        del_btn = QtWidgets.QPushButton()
        del_btn.setFixedWidth(24)
        del_btn.setStyleSheet("""
            QPushButton {
                border: none !important;
                background: #444 !important;
                color: #fff !important;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: #666 !important;
            }
            QPushButton:pressed {
                background: #222 !important;
            }
        """)
        del_btn.setIcon(QtGui.QIcon(get_resource_path(os.path.join("res", "images", "icons", "cross-circle.svg"))))
        del_btn.setIconSize(QtCore.QSize(20, 15))
        del_btn.clicked.connect(lambda: self.on_delete_clicked(order-1))
        # splitter에 가운데 정렬로 추가
        del_btn_container = QtWidgets.QWidget()
        del_btn_layout = QtWidgets.QHBoxLayout(del_btn_container)
        del_btn_layout.setContentsMargins(0, 0, 0, 0)
        del_btn_layout.setAlignment(QtCore.Qt.AlignCenter)
        del_btn_layout.addWidget(del_btn)
        splitter.addWidget(del_btn_container)
        self.splitter_widgets.append(del_btn)

        layout.addWidget(splitter)
        self.splitter = splitter

    def on_check_changed(self, state):
        self.ROI.checked = bool(state)
        if self.parent_widget is not None and hasattr(self.parent_widget, "appendROISignal") and hasattr(self.parent_widget, "removeROISignal"):
            if bool(state):
                self.parent_widget.appendROISignal.emit(self.ROI)
            else:
                self.parent_widget.removeROISignal.emit(self.ROI)
                
        if self.parent_widget is not None and hasattr(self.parent_widget, "updateImgSignal"):
            self.parent_widget.updateImgSignal.emit(True)
        self.parent_widget.save_rois()


    def on_well_changed(self, text):
        self.ROI.well = text
        self.parent_widget.save_rois()


    def on_note_changed(self, text):
        self.ROI.note = text
        self.parent_widget.save_rois()


    def on_color_changed(self, color_name):
        hex_code = self.color_dict.get(color_name, "#FF0000")
        self.ROI.color = QtGui.QColor(hex_code)
        self.ROI.color_name = color_name
        if self.parent_widget is not None and hasattr(self.parent_widget, "appendROISignal") and hasattr(self.parent_widget, "removeROISignal"):
            self.parent_widget.removeROISignal.emit(self.ROI)
            self.parent_widget.appendROISignal.emit(self.ROI)

        if self.parent_widget is not None and hasattr(self.parent_widget, "updateImgSignal"):
            self.parent_widget.updateImgSignal.emit(True)
        self.parent_widget.save_rois()

    def on_delete_clicked(self, order):
        if self.parent_widget is not None and hasattr(self.parent_widget, "ROIs"):
            self.parent_widget.ROIs.removeROI(order)
            if self.parent_widget is not None and hasattr(self.parent_widget, "removeROISignal"):
                self.parent_widget.removeROISignal.emit(self.ROI)
            if self.parent_widget is not None and hasattr(self.parent_widget, "updateImgSignal"):
                self.parent_widget.updateImgSignal.emit(True)

    def set_selected(self, selected: bool):
        self.selected = selected
        # if selected:
        #     self.setStyleSheet("""
        #         QWidget#logRowWidget {
        #             background: #222222 !important;
        #             border: 2px solid #FFA726 !important;
        #         }
        #         QWidget#logRowWidget:hover {
        #             background: #ffffff !important;
        #         }
        #     """)
        # else:
        #     self.setStyleSheet("""
        #         QWidget#logRowWidget {
        #             background: #222222 !important;
        #             border: none !important;
        #         }
        #         QWidget#logRowWidget:hover {
        #             background: #ffffff !important;
        #         }
        #     """)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            self.selectedChanged.emit(self, modifiers)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        # ROI 중심 좌표 계산 후 시그널 emit
        cx = int(self.ROI.x + self.ROI.width / 2)
        cy = int(self.ROI.y + self.ROI.height / 2)
        self.centerToROI.emit(cx, cy)
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        self.parent_widget.show_row_context_menu(self, event.globalPos())

    def update_from_roi(self, roi, order=None):
        """
        ROI 객체의 값으로 row의 각 위젯을 갱신합니다.
        order: 순서(인덱스)가 바뀌었을 경우 갱신할 값(옵션)
        """
        self.ROI = roi
        # 0. 체크박스
        self.splitter_widgets[0].blockSignals(True)
        self.splitter_widgets[0].setChecked(roi.checked)
        self.splitter_widgets[0].blockSignals(False)
        # 1. 순서 라벨
        if order is not None:
            self.splitter_widgets[1].setText(str(order))
        # 2~5. X, Y, W, H
        self.splitter_widgets[2].setText(str(roi.x))
        self.splitter_widgets[3].setText(str(roi.y))
        self.splitter_widgets[4].setText(str(roi.width))
        self.splitter_widgets[5].setText(str(roi.height))
        # 6. Well 콤보박스
        self.splitter_widgets[6].blockSignals(True)
        self.splitter_widgets[6].setCurrentText(roi.well)
        self.splitter_widgets[6].blockSignals(False)
        # 7. Color 콤보박스
        self.splitter_widgets[7].blockSignals(True)
        color_name = roi.color_name
        if color_name is None and hasattr(self, 'color_dict'):
            # hex로부터 이름 역추적
            roi_color_hex = roi.color.name().upper()
            for name, hex_code in self.color_dict.items():
                if hex_code.upper() == roi_color_hex:
                    color_name = name
                    break
        if color_name:
            self.splitter_widgets[7].setCurrentText(color_name)
        self.splitter_widgets[7].blockSignals(False)
        # 8. Note QLineEdit
        self.splitter_widgets[8].blockSignals(True)
        self.splitter_widgets[8].setText(roi.note)
        self.splitter_widgets[8].blockSignals(False)
        # 9. 삭제 버튼은 갱신 불필요