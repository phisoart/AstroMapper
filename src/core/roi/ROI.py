from PySide6 import QtCore, QtGui

from dataclasses import dataclass, field
import json, os
from utils import get_resource_path

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

class ROIs(QtCore.QObject):  # QObject 상속
    rois_changed = QtCore.Signal()  # 시그널 추가

    def __init__(self):
        super().__init__()  # QObject 초기화
        self.__len = 0  # Private 속성
        self.__ROIs = []  # Private 속성
        self.is_same_well = False
        
        # well_positions 로드
        try:
            well_info_path = get_resource_path(os.path.join("res", "data", "well_info.json"))
            with open(well_info_path, "r", encoding="utf-8") as f:
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

    def appendROI(self, _ROI, signal: bool = True):
        _ROI.x = _ROI.rect.x()
        _ROI.y = _ROI.rect.y()
        _ROI.width = _ROI.rect.width()
        _ROI.height = _ROI.rect.height()
        if _ROI.note == "":
            _ROI.note = str(self.__len + 1)
        if _ROI.well == "":
            if self.__len == 0:
                _ROI.well = "A01"
            else:
                prev_well = self.__ROIs[-1].well
                if prev_well in self.well_positions:
                    if self.is_same_well:
                        _ROI.well = prev_well
                    else:
                        idx = self.well_positions.index(prev_well)
                        next_idx = (idx + 1) % len(self.well_positions)
                        _ROI.well = self.well_positions[next_idx]
                else:
                    _ROI.well = "A01"
        self.__ROIs.append(_ROI)
        self.__len += 1
        if signal:
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

    def set_is_same_well(self, is_same_well):
        print(f"set_is_same_well: {is_same_well}")
        self.is_same_well = is_same_well

    def sort(self, key_func, reverse=False):
        """
        key_func: ROI 객체를 받아 정렬 기준 값을 반환하는 함수
        reverse: True면 내림차순, False면 오름차순
        내부 __ROIs 리스트를 직접 정렬하고, 정렬된 리스트를 반환
        """
        self.__ROIs.sort(key=key_func, reverse=reverse)
        self.rois_changed.emit()
        return self.__ROIs
