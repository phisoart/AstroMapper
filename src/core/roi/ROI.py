from PySide6 import QtCore, QtGui

from dataclasses import dataclass, field
import json, os
from utils import helper

@dataclass
class ROI:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    rect: QtCore.QRect = QtCore.QRect(0, 0, 0, 0)
    color: QtGui.QColor = field(default_factory=lambda: QtGui.QColor(255, 0, 0))
    color_name: str = "Red"
    note: str = ""
    checked: bool = True
    well: str = ""
    roi_layer_updated: bool = False


class ROIs(QtCore.QObject):  # QObject 상속
    rois_changed = QtCore.Signal()  # 시그널 추가

    def __init__(self):
        super().__init__()  # QObject 초기화
        self.__len = 0  # Private 속성
        self.__ROIs = []  # Private 속성
        
        # well_positions 로드
        try:
            with open("res/data/well_info.json", "r", encoding="utf-8") as f:
                well_data = json.load(f)
                self.well_positions = well_data.get("96well", [])
        except Exception as e:
            print(f"Well positions 로드 실패: {e}")
            self.well_positions = ["A01", "B01", "C01", "D01", "E01", "F01", "G01", "H01"]  # 기본값

    def __len__(self):
        return self.__len

    def getROIs(self):
        return self.__ROIs

    # TODO: 예외 처리 추가
    def getROI(self, index):
        try:
            return self.__ROIs[index]
        except IndexError:
            print(f"Index {index} is out of range.")
            return None

    def appendROI(self, _ROI):
        _ROI.x = _ROI.rect.x()
        _ROI.y = _ROI.rect.y()
        _ROI.width = _ROI.rect.width()
        _ROI.height = _ROI.rect.height()
        _ROI.roi_layer_updated = False
        # TODO 이전 연결해서 복사해주는 기능 추가
        if _ROI.note == "":
            _ROI.note = str(self.__len + 1)
        if _ROI.well == "":
            _ROI.well = self.well_positions[self.__len]
        self.__ROIs.append(_ROI)
        self.__len += 1
        print(_ROI)
        self.rois_changed.emit()  # 시그널 발생

    def removeROI(self, index):
        if index < 0 or index >= self.__len:
            print(f"Index {index} is out of range.")
            return None
        removed_ROI = self.__ROIs.pop(index)
        self.__len -= 1
        self.rois_changed.emit()  # 시그널 발생
        return removed_ROI

    def clearROIs(self):
        self.__ROIs.clear()  # 리스트의 모든 항목을 제거
        self.__ROIs = []
        self.__len = 0  # 리스트의 길이를 0으로 재설정
        self.rois_changed.emit()  # 시그널 발생
