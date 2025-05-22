import sys
import os
from utils import get_resource_path
from ui import AstromapperMainWindow, ImageWidget, LogWidget
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QResource

def setup_application():
    """애플리케이션의 기본 설정을 초기화합니다."""
    app = QtWidgets.QApplication(sys.argv)
    
    # 스타일시트 로드 (기본 스타일)
    style_path = get_resource_path(os.path.join("src", "ui", "styles.qss"))
    with open(style_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
    
    QResource.registerResource("ui/resources.qrc")
    
    return app

def create_main_window():
    """메인 윈도우와 필요한 컴포넌트들을 생성합니다."""
    # # 핵심 컴포넌트 초기화
    # image_processor = ImageProcessor()
    # roi_manager = ROIManager()
    
    # # UI 컴포넌트 생성
    # image_widget = ImageWidget(image_processor, roi_manager)
    # log_widget = LogWidget(roi_manager)
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
#     log_widget.image_upload_requested.connect(image_widget.open_image)
#     log_widget.sub_image_check.connect(image_widget.on_checkbox_state_changed)
#     log_widget.slider_changed.connect(image_widge t.on_slider_value_changed)
#     log_widget.update_image_signal.connect(image_widget.update_image)
#     log_widget.load_rois_signal.connect(image_widget.load_rois)
#     log_widget.extract_signal.connect(image_widget.extract_cosmosort_protocol)

# TODO
# Points들 디자인
# 1. shift통해서 로그에 저장하기
# 2. ROIs들 이미지 형태로 만들어서 효율적으로 관리하기
# 3. ROI 클릭하면 해당 부분으로 이동하기
# 4. 레퍼런스 기능 추가하기
# 5. 영역선정 시에 이미지에 글씨 추가하기 - 글씨 크기를 조절할 수 있어야 함.
# 6. svs 이미지 대응
# 7. 라지 이미지 대응
# 8. cam 기능 추가
# 9. 이미지정보 받아오기 - 예외처리 추가

def main():
    """애플리케이션의 메인 진입점입니다."""
    # # 설정 로드
    # config = Config()
    
    # 애플리케이션 설정
    app = setup_application()
    
    # 메인 윈도우 생성
    window = create_main_window()
    
    # 윈도우 아이콘 설정
    icon_path = get_resource_path(os.path.join("res", "images", "Astromapper.ico"))
    window.setWindowIcon(QtGui.QIcon(icon_path))
    
    # 윈도우 표시
    window.show()
    
    # 애플리케이션 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    main()