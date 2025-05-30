import sys
from PySide6 import QtWidgets, QtCore, QtGui
import os

def show_dialog(dialog_type, parent=None):
    if dialog_type == 'file':
        QtWidgets.QFileDialog.getOpenFileName(parent, "파일 열기")
    elif dialog_type == 'color':
        QtWidgets.QColorDialog.getColor(parent=parent)
    elif dialog_type == 'font':
        QtWidgets.QFontDialog.getFont(parent=parent)
    elif dialog_type == 'message':
        QtWidgets.QMessageBox.information(parent, "메시지", "QMessageBox 테스트입니다.")
    elif dialog_type == 'input':
        QtWidgets.QInputDialog.getText(parent, "입력", "문자열을 입력하세요:")
    # QPrintDialog 등은 프린터가 없으면 동작하지 않을 수 있음


def main():
    app = QtWidgets.QApplication(sys.argv)
    # 스타일시트 적용
    style_path = os.path.join(os.path.dirname(__file__), "ui", "test_styles.qss")
    with open(style_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    win = QtWidgets.QMainWindow(flags=QtCore.Qt.FramelessWindowHint)
    win.setWindowTitle("Qt All Widget/Dialogs Style Test")
    central = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(central)

    # QLabel
    layout.addWidget(QtWidgets.QLabel("QLabel (라벨)"))
    # QPushButton
    btn_layout = QtWidgets.QHBoxLayout()
    btn_layout.addWidget(QtWidgets.QPushButton("QPushButton (버튼)"))
    btn_layout.addWidget(QtWidgets.QPushButton("Hover/Pressed"))
    layout.addLayout(btn_layout)
    # QLineEdit
    layout.addWidget(QtWidgets.QLineEdit("QLineEdit (입력창)"))
    # QCheckBox, QRadioButton
    check_layout = QtWidgets.QHBoxLayout()
    check_layout.addWidget(QtWidgets.QCheckBox("QCheckBox"))
    check_layout.addWidget(QtWidgets.QRadioButton("QRadioButton"))
    layout.addLayout(check_layout)
    # QComboBox
    combo = QtWidgets.QComboBox()
    combo.addItems(["QComboBox - 1", "2", "3"])
    layout.addWidget(combo)
    # QSlider
    slider = QtWidgets.QSlider()
    layout.addWidget(slider)
    # QScrollBar
    scrollbar = QtWidgets.QScrollBar()
    layout.addWidget(scrollbar)
    # QProgressBar
    progress = QtWidgets.QProgressBar()
    progress.setValue(50)
    layout.addWidget(progress)
    # QTabWidget
    tabs = QtWidgets.QTabWidget()
    tab1 = QtWidgets.QWidget(); tab1.setLayout(QtWidgets.QVBoxLayout()); tab1.layout().addWidget(QtWidgets.QLabel("Tab 1"))
    tab2 = QtWidgets.QWidget(); tab2.setLayout(QtWidgets.QVBoxLayout()); tab2.layout().addWidget(QtWidgets.QLabel("Tab 2"))
    tabs.addTab(tab1, "Tab 1"); tabs.addTab(tab2, "Tab 2")
    layout.addWidget(tabs)
    # QTableWidget
    table = QtWidgets.QTableWidget(2, 2)
    table.setHorizontalHeaderLabels(["A", "B"])
    table.setItem(0, 0, QtWidgets.QTableWidgetItem("Cell 1"))
    table.setItem(1, 1, QtWidgets.QTableWidgetItem("Cell 2"))
    layout.addWidget(table)
    # QListWidget
    listw = QtWidgets.QListWidget()
    listw.addItems(["Item 1", "Item 2", "Item 3"])
    layout.addWidget(listw)
    # QFrame
    frame = QtWidgets.QFrame()
    frame.setFrameShape(QtWidgets.QFrame.Box)
    frame.setFixedHeight(30)
    layout.addWidget(frame)
    # QSplitter
    splitter = QtWidgets.QSplitter()
    splitter.addWidget(QtWidgets.QLabel("Left"))
    splitter.addWidget(QtWidgets.QLabel("Right"))
    layout.addWidget(splitter)
    # QMenuBar, QMenu
    menubar = QtWidgets.QMenuBar()
    menu = QtWidgets.QMenu("File")
    menu.addAction("Open")
    menu.addAction("Save")
    menubar.addMenu(menu)
    win.setMenuBar(menubar)
    # QToolBar
    toolbar = QtWidgets.QToolBar()
    toolbar.addAction("Tool 1")
    toolbar.addAction("Tool 2")
    win.addToolBar(toolbar)
    # QStatusBar
    status = QtWidgets.QStatusBar()
    status.showMessage("QStatusBar (상태바)")
    win.setStatusBar(status)
    # QGroupBox
    group = QtWidgets.QGroupBox("QGroupBox")
    group.setLayout(QtWidgets.QVBoxLayout())
    group.layout().addWidget(QtWidgets.QLabel("Group Content"))
    layout.addWidget(group)

    # 표준 다이얼로그 테스트 버튼
    dialog_layout = QtWidgets.QHBoxLayout()
    file_btn = QtWidgets.QPushButton("QFileDialog")
    file_btn.clicked.connect(lambda: show_dialog('file', win))
    color_btn = QtWidgets.QPushButton("QColorDialog")
    color_btn.clicked.connect(lambda: show_dialog('color', win))
    font_btn = QtWidgets.QPushButton("QFontDialog")
    font_btn.clicked.connect(lambda: show_dialog('font', win))
    msg_btn = QtWidgets.QPushButton("QMessageBox")
    msg_btn.clicked.connect(lambda: show_dialog('message', win))
    input_btn = QtWidgets.QPushButton("QInputDialog")
    input_btn.clicked.connect(lambda: show_dialog('input', win))
    dialog_layout.addWidget(file_btn)
    dialog_layout.addWidget(color_btn)
    dialog_layout.addWidget(font_btn)
    dialog_layout.addWidget(msg_btn)
    dialog_layout.addWidget(input_btn)
    layout.addLayout(dialog_layout)

    win.setCentralWidget(central)
    win.resize(1000, 1000)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
