import sys
from utils import get_resource_path
from ui import AstromapperMainWindow, ImageWidget, LogWidget
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QResource
import logging
import os
import traceback

def setup_application():
    """애플리케이션의 기본 설정을 초기화합니다."""
    app = QtWidgets.QApplication(sys.argv)
    
    # 스타일시트 로드 (기본 스타일)
    style_path = get_resource_path(os.path.join("src", "ui", "styles.qss"))
    with open(style_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
        
    return app

def create_main_window():
    """메인 윈도우와 필요한 컴포넌트들을 생성합니다."""

    image_widget = ImageWidget()
    log_widget = LogWidget()
    
    # 메인 윈도우 생성
    # window = AstromapperMainWindow()
    window = AstromapperMainWindow(image_widget, log_widget)

    
    # # 시그널 연결
    connect_signals(image_widget, log_widget)
    
    return window

def connect_signals(image_widget: ImageWidget, log_widget: LogWidget):
#     """컴포넌트 간 시그널을 연결합니다."""
#     # 이미지 위젯 -> 로그 위젯 시그널
    image_widget.openImgSignal.connect(log_widget.openImgSignal)
#     image_widget.update_log_signal.connect(log_widget.update_log_entries)
#     image_widget.set_image_signal.connect(log_widget.set_image_name)
#     image_widget.connect_signal.connect(log_widget.replace_log_buttons_layout)
    
#     # 로그 위젯 -> 이미지 위젯 시그널
    log_widget.subImageChecked.connect(image_widget.on_checkbox_state_changed)
    log_widget.subImageSliderChanged.connect(image_widget.on_slider_value_changed)
    log_widget.updateImgSignal.connect(image_widget.update_img)
    log_widget.appendROISignal.connect(image_widget.append_roi_layer)
    log_widget.removeROISignal.connect(image_widget.remove_roi_layer)
    log_widget.clearROISignal.connect(image_widget.clear_roi_layer)
    log_widget.moveImageSignal.connect(image_widget.move_image)
#     log_widget.image_upload_requested.connect(image_widget.open_image)
#     log_widget.sub_image_check.connect(image_widget.on_checkbox_state_changed)
#     log_widget.slider_changed.connect(image_widge t.on_slider_value_changed)
#     log_widget.update_image_signal.connect(image_widget.update_image)
#     log_widget.load_rois_signal.connect(image_widget.load_rois)
#     log_widget.extract_signal.connect(image_widget.extract_cosmosort_protocol)

# TODO

# 디자인 파일 정리하기
# lOG에 HOVER기능 추가

# TOOL - 5. 영역선정 시에 이미지에 글씨 추가하기 - 글씨 크기를 조절할 수 있어야 함.

# 4. 레퍼런스 기능 추가하기 - reference dialog 기능 추가

# save dialog 기능 추가
# 6. ROIs들 이미지 출력하는 기능 추가

# 박스 선택하면 드래그로 이동 되도록 및 사이즈 조절 되게

# 레퍼런스 등록되면 실제 길이와 변환 가능하도록.
# 6. svs 이미지 대응 -> svs로드해서 이미지로 받으면 추후 프로세스 동일!

# 7. 라지 이미지 대응

# 버전 체크 기능 추가
# 세이브 기능 구현
# 로그는 프로젝트파일에 저장하도록
# 11. 셀소터 및 이미지 분석 기능 추가.
# Control Z 기능 추가 (10번까지)

def main():
    """애플리케이션의 메인 진입점입니다."""
    # # 설정 로드
    # logging.basicConfig(
    #     filename='log.txt',
    #     level=logging.INFO,
    #     format='[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
    # )

    app = setup_application()
    
    # 메인 윈도우 생성
    window = create_main_window()
    
    # # 윈도우 아이콘 설정
    icon_path = get_resource_path(os.path.join("res", "images", "Astromapper.ico"))
    window.setWindowIcon(QtGui.QIcon(icon_path))
    
    # # 윈도우 표시
    window.show()
    
    # # 애플리케이션 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    main()