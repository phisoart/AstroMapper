from PySide6 import QtCore, QtGui

from dataclasses import dataclass, field
import json, os


@dataclass
class ROI:
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    rect: QtCore.QRect = QtCore.QRect(0, 0, 0, 0)
    color: QtGui.QColor = field(default_factory=lambda: QtGui.QColor(0, 0, 255))
    note: str = ""
    checked: bool = True
    well: str = ""


class ROIs:
    def __init__(self):
        self.__len = 0  # Private 속성
        self.__ROIs = []  # Private 속성

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
        print(_ROI)

        if _ROI.description == "":
            _ROI.description = str(self.__len + 1)
        if _ROI.well == "":
            _ROI.well = self.well_positions[self.__len]
        self.__ROIs.append(_ROI)
        self.__len += 1

    def removeROI(self, index):
        if index < 0 or index >= self.__len:
            print(f"Index {index} is out of range.")
            return None
        removed_ROI = self.__ROIs.pop(index)
        self.__len -= 1
        return removed_ROI

    def clearROIs(self):
        self.__ROIs.clear()  # 리스트의 모든 항목을 제거
        self.__ROIs = []
        self.__len = 0  # 리스트의 길이를 0으로 재설정
