from PySide6 import QtWidgets, QtCore, QtGui
from utils.helper import get_resource_path
import os
import shutil
from utils import helper
from utils.settings import Settings
from core.roi.ROI import ROIs, ROI
from ui.widgets.tool_bar import ToolBar
class ImageWidget(QtWidgets.QWidget):
    openImgSignal = QtCore.Signal(bool)  # 사용자 정의 시그널
    updateLogSignal = QtCore.Signal()
    connectSignal = QtCore.Signal(bool)

    def __init__(self, ROIs):
        super().__init__()
        self.setObjectName("imageWidget")

        # 여기 있는 것들 로드 되도록.
        self.ROIs = ROIs
        self.project_dir = None
        self.origin_img = None
        self.sub_img = None
        self.is_svs = False
        self.dragging = False
        self.select_roi_on = False
        self.drawing_rect = QtCore.QRect()
        self.init_window_ratio = None
        self.project_config = None
        self.tool_bar_roi_on = False

        self.is_square = True

        self.tmp_center = QtCore.QPointF(0, 0)
        self.zoom = 1
        self.zoom_min = 1
        self.zoom_max = 1
        self.last_window_size = QtCore.QSize(0, 0)
        self.sub_img_size = None
        self.current_ROI = ROI()
       
        # from settings 
        self.settings = Settings()
        self.zoom_max_ratio = self.settings.get('image_widget.default_zoom_max_ratio')
        self.is_sub_img = self.settings.get('image_widget.default_is_sub_img')
        self.sub_img_scale = self.settings.get('image_widget.default_sub_img_size')
        self.zoom_speed = self.settings.get('image_widget.default_zoom_speed')
        self.sub_img_border_color = QtGui.QColor(self.settings.get('image_widget.sub_img_border_color'))
        self.sub_img_border_width = self.settings.get('image_widget.sub_img_border_width')
        self.sub_img_box_color = QtGui.QColor(self.settings.get('image_widget.sub_img_box_color'))
        self.sub_img_box_width = self.settings.get('image_widget.sub_img_box_width')

        self.cross_visible = False

        # ROI 레이어 추가
        self.roi_layer = None

        # 중앙 레이아웃 설정
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignCenter)
        self.tool_bar = ToolBar(self)
        self.layout.addWidget(self.tool_bar)
        self.tool_bar.crossToggled.connect(self.set_cross_visible)
        self.tool_bar.hide()

        # Open Image 버튼 추가
        self.open_btn = QtWidgets.QPushButton("Open Image")
        self.open_btn.setObjectName("openImageButton")
        self.open_btn.setMinimumWidth(150)
        self.open_btn.setMinimumHeight(50)
        self.open_btn.clicked.connect(self.open_image)
        self.layout.addWidget(self.open_btn, alignment=QtCore.Qt.AlignCenter)
        
        # 이미지 표시를 위한 라벨 추가
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 400)
        self.image_label.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        self.image_label.hide()  # 초기에는 숨김
        self.layout.addWidget(self.image_label, 1)  # stretch factor를 1로 설정
        
        # 마우스 추적 활성화
        self.image_label.setMouseTracking(True)

        # =======================================
        # Events
        self.image_label.mousePressEvent = lambda event: helper.mousePressEvent(
            self, event
        )
        self.image_label.mouseReleaseEvent = lambda event: helper.mouseReleaseEvent(
            self, event
        )
        self.image_label.mouseMoveEvent = lambda event: helper.mouseMoveEvent(self, event)
        self.image_label.wheelEvent = lambda event: helper.wheelEvent(self, event)
        self.image_label.resizeEvent = lambda event: helper.on_size_changed(self, event)
        self.image_label.mouseDoubleClickEvent = lambda event: helper.on_double_click(self, event)

        # =======================================

        self.load_styles()

    def load_styles(self):
        """QSS 스타일시트를 로드합니다."""
        style_path = get_resource_path(os.path.join("src", "ui", "styles", "image_widget.qss"))
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def open_image(self):     
        """이미지 파일을 선택하고 프로젝트 폴더로 복사한 후 로드합니다."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            try:
                # 현재 프로젝트 폴더의 images 폴더 경로 가져오기
                if not self.project_dir:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Warning",
                        "Please create a project first."
                    )
                    return
                
                images_dir = os.path.join(self.project_dir, "images")
                if not os.path.exists(images_dir):
                    os.makedirs(images_dir)
                
                # 이미지 파일 이름 가져오기
                new_file_path = os.path.join(images_dir, os.path.basename(file_path))
                # 이미지 파일 복사
                shutil.copy2(file_path, new_file_path)
                # 이미지 설정 저장
                # TODO: 저장 기능 추가
                if self.project_config:
                    self.project_config.save_image_info(new_file_path)
                
                self.load_image(new_file_path)
            # TODO 디자인 확인
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to open image: {str(e)}"
                )
                print(str(e))

    def load_image(self, _file_path: str):
        if _file_path:
            try:
                # TODO: svs제작
                # 이미지 로드
                self.origin_img = QtGui.QPixmap(_file_path)
                self.roi_layer = QtGui.QPixmap(self.origin_img.size())
                self.roi_layer.fill(QtCore.Qt.transparent)
                self.tmp_center = QtCore.QPointF(
                    self.origin_img.width() / 2, self.origin_img.height() / 2
                )
                self.sub_img_size = int(
                    max(min(self.image_label.width() / 3, self.image_label.height() / 3), 200)
                )
                self.init_window_ratio = self.image_label.width() / self.image_label.height()
                self.last_window_size = self.image_label.size()
                # zoom: 현재 window에서 이미지랑 비교했을 때 길쭉한쪽 기준 비율
                if (
                    self.origin_img.width() / self.origin_img.height()
                    > self.image_label.width() / self.image_label.height()
                ):
                    self.zoom = self.image_label.width() / self.origin_img.width()
                else:
                    self.zoom = self.image_label.height() / self.origin_img.height()
                self.zoom_min = self.zoom / 2
                self.zoom_max = self.zoom * self.zoom_max_ratio
                self.update_roi_layer()  # ROI 레이어 초기화
                self.update_img()
                self.image_label.show()
                self.tool_bar.show()
                # 버튼 숨기기
                self.open_btn.hide()
                
                # 시그널 발생 (복사된 이미지 경로 전달)
                self.openImgSignal.emit(True)
            # TODO 디자인 확인
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to load image: {str(e)}"
                )
                print(str(e))

    def append_roi_layer(self, _ROI):
        if self.origin_img is None:
            return
        painter = QtGui.QPainter(self.roi_layer)
        # pen = QtGui.QPen(_ROI.color, 1)

        pen = QtGui.QPen(QtCore.Qt.NoPen)

        painter.setPen(pen)
        half_transparent_color = QtGui.QColor(_ROI.color)
        half_transparent_color.setAlpha(50)
        brush = QtGui.QBrush(half_transparent_color)
        painter.setBrush(brush)
        painter.drawRect(_ROI.rect)
        painter.end()

    def remove_roi_layer(self, _ROI):
        if self.origin_img is None:
            return
        painter = QtGui.QPainter(self.roi_layer)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
        painter.fillRect(_ROI.rect, QtCore.Qt.transparent)
        painter.end()

    def clear_roi_layer(self):
        if self.origin_img is None:
            return
        painter = QtGui.QPainter(self.roi_layer)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
        painter.fillRect(self.roi_layer.rect(), QtCore.Qt.transparent)
        painter.end()

    def update_roi_layer(self):
        if self.origin_img is None:
            return
        painter = QtGui.QPainter(self.roi_layer)
        for roi in self.ROIs.getROIs():
            pen = QtGui.QPen(roi.color, 1)
            painter.setPen(pen)
            half_transparent_color = QtGui.QColor(roi.color)
            half_transparent_color.setAlpha(50)
            brush = QtGui.QBrush(half_transparent_color)
            painter.setBrush(brush)
            painter.drawRect(roi.rect)
        painter.end()

    def update_img(self):
        has_image, _ = self.project_config.get_image_settings()
        if not has_image or self.origin_img is None:
            return

        window_img_rect, crop_rect = self.get_crop_window_rect()

        cropped_origin_img = self.origin_img.copy(crop_rect)
        pixmap = QtGui.QPixmap(self.image_label.width(), self.image_label.height())
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        scaled_origin_img = cropped_origin_img.scaled(
            window_img_rect.width() - window_img_rect.x(),
            window_img_rect.height() - window_img_rect.y(),
        )
        painter.drawPixmap(window_img_rect.topLeft(), scaled_origin_img)
        if self.roi_layer:
            cropped_roi_layer = self.roi_layer.copy(crop_rect)
            scaled_roi_layer = cropped_roi_layer.scaled(
                window_img_rect.width() - window_img_rect.x(),
                window_img_rect.height() - window_img_rect.y(),
            )
            painter.drawPixmap(window_img_rect.topLeft(), scaled_roi_layer)

        if self.is_sub_img:
            self.update_sub_img(painter, crop_rect, self.sub_img_scale)
        if self.select_roi_on:
            color_hex = self.project_config.get_color()
            pen = QtGui.QPen(QtGui.QColor(color_hex), 1)
            painter.setPen(pen)
            painter.drawRect(self.drawing_rect)

        # 십자선 그리기
        if self.cross_visible:
            pen = QtGui.QPen(QtGui.QColor('red'), 2)
            painter.setPen(pen)
            w = self.image_label.width()
            h = self.image_label.height()
            painter.drawLine(w//2, 0, w//2, h)
            painter.drawLine(0, h//2, w, h//2)
        painter.end()

        self.image_label.setPixmap(pixmap)

    def update_sub_img(self, _painter, _crop_rect, sub_img_scale):
        brush = QtGui.QBrush(QtCore.Qt.NoBrush)

        # Set the brush and draw the rectangle
        _painter.setBrush(brush)

        ### sub image
        if self.origin_img.width() > self.origin_img.height():
            _sub_img_rect = [
                int(
                    sub_img_scale
                    * self.sub_img_size
                    * self.origin_img.width()
                    / self.origin_img.height()
                ),
                int(sub_img_scale * self.sub_img_size),
            ]
        else:
            _sub_img_rect = [
                int(sub_img_scale * self.sub_img_size),
                int(
                    sub_img_scale
                    * self.sub_img_size
                    * self.origin_img.height()
                    / self.origin_img.width()
                ),
            ]
        _painter.drawPixmap(
            self.image_label.width() - _sub_img_rect[0],
            self.image_label.height() - _sub_img_rect[1],
            self.origin_img.scaled(_sub_img_rect[0], _sub_img_rect[1]),
        )
        # Draw the edge
        pen = QtGui.QPen(self.sub_img_border_color, self.sub_img_border_width)
        _painter.setPen(pen)
        pixmap_rect = QtCore.QRect(
            self.image_label.width() - _sub_img_rect[0],
            self.image_label.height() - _sub_img_rect[1],
            _sub_img_rect[0],
            _sub_img_rect[1],
        )
        _painter.drawRect(pixmap_rect)

        # Draw the ROI edge
        pen = QtGui.QPen(self.sub_img_box_color, self.sub_img_box_width)
        _painter.setPen(pen)
        roi_rect = QtCore.QRect(
            self.image_label.width()
            - _sub_img_rect[0]
            + int(max(0, _crop_rect.x() / self.origin_img.width() * _sub_img_rect[0])),
            self.image_label.height()
            - _sub_img_rect[1]
            + int(
                max(0, _crop_rect.y() / self.origin_img.height() * _sub_img_rect[1])
            ),
            int(
                max(
                    0,
                    min(
                        _sub_img_rect[0] - 1,
                        _crop_rect.width()
                        / self.origin_img.width()
                        * _sub_img_rect[0],
                    ),
                )
            ),
            int(
                max(
                    0,
                    min(
                        _sub_img_rect[1] - 1,
                        _crop_rect.height()
                        / self.origin_img.height()
                        * _sub_img_rect[1],
                    ),
                )
            ),
        )
        _painter.drawRect(roi_rect)

    def get_crop_window_rect(self):
        # 왼쪽 상단 point x,y 오른쪽 하단 point x,y
        # window 상에서의 좌표값.
        _img_rect = QtCore.QRect(
            int(self.image_label.width() / 2 - self.tmp_center.x() * self.zoom),
            int(self.image_label.height() / 2 - self.tmp_center.y() * self.zoom),
            int(
                self.image_label.width() / 2
                + (self.origin_img.width() - self.tmp_center.x()) * self.zoom
            ),
            int(
                self.image_label.height() / 2
                + (self.origin_img.height() - self.tmp_center.y()) * self.zoom
            ),
        )

        window_img_rect = QtCore.QRect(
            max(0, _img_rect.x()),
            max(0, _img_rect.y()),
            min(self.image_label.width(), _img_rect.width()),
            min(self.image_label.height(), _img_rect.height()),
        )

        crop_rect = QtCore.QRect(
            int(
                (
                    self.tmp_center.x()
                    - (self.image_label.width() / 2 - window_img_rect.x()) / self.zoom
                )
            ),
            int(
                (
                    self.tmp_center.y()
                    - (self.image_label.height() / 2 - window_img_rect.y()) / self.zoom
                )
            ),
            int((window_img_rect.width() - window_img_rect.x()) / self.zoom),
            int((window_img_rect.height() - window_img_rect.y()) / self.zoom),
        )

        return window_img_rect, crop_rect

    def on_slider_value_changed(self, value):
        self.set_sub_img_scale(value / 100 + 0.5)
        self.update_img()

    def set_sub_img_scale(self, _sub_img_scale):
        self.sub_img_scale = _sub_img_scale
    def set_is_sub_img(self, _boolean):
        self.is_sub_img = _boolean

    def on_checkbox_state_changed(self, state):
        if state:
            self.set_is_sub_img(True)
            self.update_img()
            pass
        else:
            self.set_is_sub_img(False)
            self.update_img()
            pass

    def set_cross_visible(self, visible: bool):
        self.cross_visible = visible
        self.update_img()

    def move_image(self, x, y):
        self.tmp_center = QtCore.QPointF(x, y)
        self.update_img()

    def set_tool_bar_roi_on(self, on: bool):
        self.tool_bar_roi_on = on
