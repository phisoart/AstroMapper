from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QPoint, QPointF
class ReferencePointDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.is_reference_point_1_set = False
        self.is_reference_point_2_set = False
        self.reference_point_image_1 = QPoint(0, 0)
        self.reference_point_image_2 = QPoint(0, 0)
        self.reference_point_cosmosort_1 = QPointF(0, 0)
        self.reference_point_cosmosort_2 = QPointF(0, 0)

        self.setWindowTitle("Set reference points")
        self.setModal(True)
        self.setFixedSize(500, 350)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(20)

        # Point 1
        point1_label = QtWidgets.QPushButton("Set")
        point1_label.clicked.connect(self.set_reference_point_1)
        main_layout.addWidget(point1_label)
        point1_row = QtWidgets.QHBoxLayout()
        point1_x_label = QtWidgets.QLabel("X:")
        self.point1_x_edit = QtWidgets.QLineEdit("13.546")
        point1_y_label = QtWidgets.QLabel("Y:")
        self.point1_y_edit = QtWidgets.QLineEdit("12.546")
        point1_set_btn = QtWidgets.QPushButton("Set")
        point1_set_btn.clicked.connect(self.set_reference_point_1)
        point1_row.addWidget(point1_x_label)
        point1_row.addWidget(self.point1_x_edit)
        point1_row.addWidget(point1_y_label)
        point1_row.addWidget(self.point1_y_edit)
        point1_row.addWidget(point1_set_btn)
        main_layout.addLayout(point1_row)

        # Point 2
        point2_label = QtWidgets.QPushButton("Set")
        point2_label.clicked.connect(self.set_reference_point_2)
        main_layout.addWidget(point2_label)
        point2_row = QtWidgets.QHBoxLayout()
        point2_x_label = QtWidgets.QLabel("X:")
        self.point2_x_edit = QtWidgets.QLineEdit("13.546")
        point2_y_label = QtWidgets.QLabel("Y:")
        self.point2_y_edit = QtWidgets.QLineEdit("12.546")
        point2_set_btn = QtWidgets.QPushButton("Set")
        point2_set_btn.clicked.connect(self.set_reference_point_2)
        point2_row.addWidget(point2_x_label)
        point2_row.addWidget(self.point2_x_edit)
        point2_row.addWidget(point2_y_label)
        point2_row.addWidget(self.point2_y_edit)
        point2_row.addWidget(point2_set_btn)
        main_layout.addLayout(point2_row)

        main_layout.addStretch(1)
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        main_layout.addWidget(btn_box) 

    def set_reference_point_1(self):
        self.reference_point_cosmosort_1 = QPointF(self.point1_x_edit.text(), self.point1_y_edit.text())
    def set_reference_point_2(self):
        self.reference_point_cosmosort_2 = QPointF(self.point2_x_edit.text(), self.point2_y_edit.text())
        
    def set_reference_point_image_1(self):
        self.reference_point_image_1 = QPoint(self.point1_x_edit.text(), self.point1_y_edit.text())
    def set_reference_point_image_2(self):
        self.reference_point_image_2 = QPoint(self.point2_x_edit.text(), self.point2_y_edit.text())
