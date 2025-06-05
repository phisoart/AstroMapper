import sys
from utils import get_resource_path
from ui import AstromapperMainWindow, ImageWidget, LogWidget
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QResource
import os
from core.roi.ROI import ROIs
import platform

def setup_application():
    """애플리케이션의 기본 설정을 초기화합니다."""
    app = QtWidgets.QApplication(sys.argv)

    style_path = get_resource_path(os.path.join("src", "ui", "styles.qss"))
    with open(style_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
        
    return app

def create_main_window():
    """메인 윈도우와 필요한 컴포넌트들을 생성합니다."""
    
    window = AstromapperMainWindow()

    connect_signals(window.image_widget, window.log_widget, window.ROIs)
    
    return window

def connect_signals(image_widget: ImageWidget, log_widget: LogWidget, ROIs: ROIs):
#     """컴포넌트 간 시그널을 연결합니다."""
#     # 이미지 위젯 -> 로그 위젯 시그널
    image_widget.openImgSignal.connect(log_widget.openImgSignal)
    image_widget.tool_bar.sameWellToggled.connect(ROIs.set_is_same_well)
    image_widget.tool_bar.roiToggled.connect(image_widget.set_tool_bar_roi_on)
#     image_widget.set_image_signal.connect(log_widget.set_image_name)
#     image_widget.connect_signal.connect(log_widget.replace_log_buttons_layout)
    
#     # 로그 위젯 -> 이미지 위젯 시그널
    log_widget.subImageChecked.connect(image_widget.on_checkbox_state_changed)
    log_widget.subImageSliderChanged.connect(image_widget.on_slider_value_changed)
    log_widget.updateImgSignal.connect(image_widget.update_image)
    log_widget.appendROISignal.connect(image_widget.append_roi_layer)
    log_widget.removeROISignal.connect(image_widget.remove_roi_layer)
    log_widget.clearROISignal.connect(image_widget.clear_roi_layer)
    log_widget.moveImageSignal.connect(image_widget.move_image)
    log_widget.updateROISignal.connect(image_widget.update_roi_layer)
    ROIs.rois_changed.connect(log_widget.on_rois_changed)

#     log_widget.image_upload_requested.connect(image_widget.open_image)
#     log_widget.sub_image_check.connect(image_widget.on_checkbox_state_changed)
#     log_widget.slider_changed.connect(image_widge t.on_slider_value_changed)
#     log_widget.update_image_signal.connect(image_widget.update_image)
#     log_widget.load_rois_signal.connect(image_widget.load_rois)
#     log_widget.extract_signal.connect(image_widget.extract_cosmosort_protocol)

# TODO


# 4. 레퍼런스 기능 추가하기 - reference dialog 기능 추가
# save버튼시 생기는 dialog 기능 추가
# 6. ROIs들 이미지 출력하는 기능 추가

# 박스 선택하면 드래그로 이동 되도록 및 사이즈 조절 되게

# Undo 기능 추가 (10번까지)
# (setting)ROI관련 - 체크, 색, note, sorting순서, 삭제, 이동, 추가, 초기화, 웰정보
# (setting)legend 사이즈 및 체크 여부

# settings_btn 구현
# save as 기능 추가
# 이미 파일 열린상태에서 여는거는 일단 추후에

# TOOL - 5. 영역선정 시에 이미지에 글씨 추가하기 - 글씨 크기를 조절할 수 있어야 함.

# 이미지 대응 ->
# 6. svs 이미지 대응 -> svs로드해서 이미지로 받으면 추후 프로세스 동일!
# 7. 라지 이미지 대응

# 레퍼런스 등록되면 실제 길이와 변환 가능하도록.

# 11. 셀소터 및 이미지 분석 기능 추가.


def main():
    """애플리케이션의 메인 진입점입니다."""

    app = setup_application()
    window = create_main_window()
    
    # TODO: 아이콘 업데이트
    if platform.system() == "Darwin":  # macOS
        icon_path = get_resource_path(os.path.join("res", "images", "Astromapper.icns"))
    else:
        icon_path = get_resource_path(os.path.join("res", "images", "Astromapper.ico"))

    window.setWindowIcon(QtGui.QIcon(icon_path))
    
    # # 윈도우 표시
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()