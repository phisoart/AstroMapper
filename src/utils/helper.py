import os, sys
import webbrowser
from PySide6 import QtCore, QtGui
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.widgets.image_widget import ImageWidget

def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # 현재 실행 파일의 디렉토리를 기준으로 상대 경로 계산
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)


def open_webpage(url: str) -> None:
    """
    기본 웹 브라우저에서 지정된 URL을 엽니다.
    
    Args:
        url: 열고자 하는 웹페이지의 URL
    """
    webbrowser.open(url)

def mousePressEvent(self: 'ImageWidget', event):
    if event.button() == QtCore.Qt.LeftButton:
        # if self.file_name and event.modifiers() == QtCore.Qt.ShiftModifier:
        #     self.current_ROI.rect = QtCore.QRect(
        #         int(event.pos().x()), int(event.pos().y()), 1, 1
        #     )
        #     self.current_ROI.color = QtGui.QColor(0, 0, 255)
        #     self.shift_on = True
        # elif self.file_name and event.modifiers() == QtCore.Qt.ControlModifier:
        #     if self.marker_state != -1:
        #         self.marker_center[self.marker_state] = (
        #             self.convert_qpoint_window2image(
        #                 QtCore.QPoint(event.pos().x(), event.pos().y())
        #             )
        #         )
        #         self.marker_status[self.marker_state] = True
        #         self.update_img(True)
        #         self.marker_state = -1
        #         self.update_marker_btns()
        # else:
        self.dragging = True
        self.last_pos = event.pos()
        event.accept()

def mouseReleaseEvent(self: 'ImageWidget', event):
    if event.button() == QtCore.Qt.LeftButton:
        self.dragging = False
#         if self.file_name and self.shift_on:
#             self.shift_on = False

#             # 현재 윈도우에서의 window 값
#             xmin, xmax = min(self.current_ROI.rect.x(), event.pos().x()), max(
#                 self.current_ROI.rect.x(), event.pos().x()
#             )
#             ymin, ymax = min(self.current_ROI.rect.y(), event.pos().y()), max(
#                 self.current_ROI.rect.y(), event.pos().y()
#             )
#             if self.is_square:
#                 len = min(int(xmax - xmin), int(ymax - ymin))
#                 if (
#                     self.current_ROI.rect.x() > event.pos().x()
#                     and int(xmax - xmin) > len
#                 ):
#                     xmin = self.current_ROI.rect.x() - len
#                 if (
#                     self.current_ROI.rect.y() > event.pos().y()
#                     and int(ymax - ymin) > len
#                 ):
#                     ymin = self.current_ROI.rect.y() - len
#                 current_rect = QtCore.QRect(int(xmin), int(ymin), len, len)
#             else:
#                 current_rect = QtCore.QRect(
#                     int(xmin), int(ymin), int(xmax - xmin), int(ymax - ymin)
#                 )
#             self.current_ROI.rect = self.convert_qrect_window2image(current_rect)
#             self.ROIs.appendROI(copy.deepcopy(self.current_ROI))
#             self.update_img(updateROIs=True)
#             self.updateLogSignal.emit()
#         else:
#             self.shift_on = False
#         event.accept()


def mouseMoveEvent(self: 'ImageWidget', event):
    # if self.file_name and self.shift_on:
    #     xmin, xmax = min(self.current_ROI.rect.x(), event.pos().x()), max(
    #         self.current_ROI.rect.x(), event.pos().x()
    #     )
    #     ymin, ymax = min(self.current_ROI.rect.y(), event.pos().y()), max(
    #         self.current_ROI.rect.y(), event.pos().y()
    #     )
    #     len = min(int(xmax - xmin), int(ymax - ymin))
    #     if self.current_ROI.rect.x() > event.pos().x() and int(xmax - xmin) > len:
    #         xmin = self.current_ROI.rect.x() - len
    #     if self.current_ROI.rect.y() > event.pos().y() and int(ymax - ymin) > len:
    #         ymin = self.current_ROI.rect.y() - len
    #     self.drawing_rect = QtCore.QRect(int(xmin), int(ymin), len, len)
    #     self.update_img()
    #     event.accept()
    if self.dragging:
        # Calculate the movement vector based on the current and last positions
        delta = event.pos() - self.last_pos

        self.last_pos = event.pos()

        # Move the pixmap and update tmp_center
        self.tmp_center.setX(self.tmp_center.x() - delta.x() / self.zoom)
        self.tmp_center.setY(self.tmp_center.y() - delta.y() / self.zoom)
        self.update_img()
        event.accept()
    
    # 마우스 위치를 이미지 좌표로 변환하여 상태바에 표시
    has_image, _ = self.project_config.get_image_settings()
    if has_image:
        x = int((event.pos().x() - self.image_label.width() / 2) / self.zoom + self.tmp_center.x())
        y = int((event.pos().y() - self.image_label.height() / 2) / self.zoom + self.tmp_center.y())
        
        # 이미지 범위 내에 있는지 확인
        if 0 <= x < self.origin_img.width() and 0 <= y < self.origin_img.height():
            self.window().status_bar.showCenterMessage(f"Position: ({x}, {y})")
        else:
            self.window().status_bar.clearCenterMessage()


def wheelEvent(self: 'ImageWidget', event: QtGui.QWheelEvent):
    # if self.image_widget.pixmap and self.left_widget.underMouse():
    delta = event.angleDelta().y() / 240
    if delta > 0:
        zoom_in(self)
    elif delta < 0:
        zoom_out(self)
    event.accept()


def on_size_changed(self: 'ImageWidget', event):
    # This function will be called whenever self.image_label is resized
    print("Image label resized to: ", self.image_label.size())
    has_image, _ = self.project_config.get_image_settings()
    if has_image:
        self.sub_img_size = int(
            max(min(self.image_label.width() / 3, self.image_label.height() / 3), 200)
        )
        # zoom: 현재 window에서 이미지랑 비교했을 때 길쭉한쪽 기준 비율
        _window_ratio = self.image_label.width() / self.image_label.height()
        if _window_ratio > self.init_window_ratio:
            self.zoom = self.zoom * self.image_label.height() / self.last_window_size.height()
        else:
            self.zoom = self.zoom * self.image_label.width() / self.last_window_size.width()
        self.last_window_size = self.image_label.size()

        self.update_img()


def zoom_in(self):
    has_image, _ = self.project_config.get_image_settings()
    if has_image:
        if not self.zoom_max < self.zoom * self.zoom_speed:
            self.zoom *= self.zoom_speed
        else:
            self.zoom = self.zoom_max
        self.update_img()


def zoom_out(self):
    has_image, _ = self.project_config.get_image_settings()
    if has_image:
        if not self.zoom_min > self.zoom / self.zoom_speed:
            self.zoom /= self.zoom_speed
        else:
            self.zoom = self.zoom_min
        self.update_img()

def on_double_click(self: 'ImageWidget', event):
    """
    ImageWidget에서 더블클릭 시, 클릭한 이미지 좌표가 가운데에 오도록 이동합니다.
    Args:
        self: ImageWidget 인스턴스
        event: QEvent
    """
    if event.type() == QtCore.QEvent.MouseButtonDblClick:
        has_image, _ = self.project_config.get_image_settings()
        if has_image and self.origin_img is not None:
            x = int((event.pos().x() - self.image_label.width() / 2) / self.zoom + self.tmp_center.x())
            y = int((event.pos().y() - self.image_label.height() / 2) / self.zoom + self.tmp_center.y())
            self.tmp_center = QtCore.QPointF(x, y)
            self.update_img()