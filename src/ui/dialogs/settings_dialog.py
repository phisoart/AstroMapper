from PySide6 import QtWidgets, QtCore, QtGui
import json

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Column Settings")
        self.setModal(True)
        self.setFixedSize(600, 180)

        # 메인 레이아웃
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(18, 18, 18, 18)

        # 컬럼별(라벨+체크박스) 가로 배치
        columns_layout = QtWidgets.QHBoxLayout()
        columns_layout.setSpacing(24)
        columns_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.checkboxes = {}

        # point_info에서 빈 문자열이 아닌 항목들만 가져오기
        try:
            with open("res/data/point_info.json", "r", encoding="utf-8") as f:
                point_info = json.load(f)["point_info"]
        except Exception:
            point_info = ["checkbox", "X", "Y", "Width", "Height", "Well", "Color", "Note", "Delete"]

        for col in point_info:
            if col != "checkbox" and col != "Delete":
                col_widget = QtWidgets.QWidget()
                col_vbox = QtWidgets.QVBoxLayout(col_widget)
                col_vbox.setContentsMargins(0, 0, 0, 0)
                col_vbox.setSpacing(8)
                col_vbox.setAlignment(QtCore.Qt.AlignCenter)

                label = QtWidgets.QLabel(col)
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setFixedHeight(22)
                label.setStyleSheet(
                    "QLabel {"
                    "  color: #fff !important;"
                    "  font-size: 13px !important;"
                    "  min-width: 40px !important;"
                    "  border: none !important;"
                    "  background: transparent !important;"
                    "}"
                )
                checkbox = QtWidgets.QCheckBox()
                checkbox.setFixedSize(20, 20)
                checkbox.setStyleSheet(
                    "QCheckBox {"
                    "  color: #fff !important;"
                    "  min-width: 20px !important;"
                    "  max-width: 20px !important;"
                    "  min-height: 20px !important;"
                    "  max-height: 20px !important;"
                    "  border: 2px solid #888 !important;"
                    "  border-radius: 4px !important;"
                    "  background: transparent !important;"
                    "  margin: 0px !important;"
                    "  padding: 0px !important;"
                    "}"
                    "QCheckBox::indicator {"
                    "  width: 18px !important;"
                    "  height: 18px !important;"
                    "}"
                )
                col_vbox.addWidget(label, alignment=QtCore.Qt.AlignHCenter)
                col_vbox.addWidget(checkbox, alignment=QtCore.Qt.AlignHCenter)
                self.checkboxes[col] = checkbox
                columns_layout.addWidget(col_widget)

        layout.addLayout(columns_layout)

        # 버튼 레이아웃
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        save_btn = QtWidgets.QPushButton("Save")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        for btn in [save_btn, cancel_btn]:
            btn.setStyleSheet(
                "QPushButton {"
                "  background-color: #3b3b3b !important;"
                "  color: #ffffff !important;"
                "  border: none !important;"
                "  padding: 5px 18px !important;"
                "  border-radius: 3px !important;"
                "  min-width: 80px !important;"
                "}"
                "QPushButton:hover {"
                "  background-color: #4b4b4b !important;"
                "}"
            )
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # 다이얼로그 배경
        self.setStyleSheet(
            "QDialog {"
            "  background-color: #2b2b2b !important;"
            "  color: #ffffff !important;"
            "}"
        ) 