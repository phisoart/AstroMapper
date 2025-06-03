import os
import yaml
import shutil
import sys
from utils.helper import get_resource_path
import logging
from datetime import datetime
class TempConfigManager:
    """
    프로젝트 폴더 내 임시 설정(.config.yaml) 파일을 관리하는 매니저 클래스
    - 최초 실행 시 default_config.yaml을 복사해 .config.yaml 생성
    - window_size만 메모리에서 관리하다가 저장 시 .config.yaml에 반영
    """
    def __init__(self, main_window):
        self.main_window = main_window
        self.project_dir = ""
        self.temp_config_path = ""
        self.config_path = ""
        self.temp_config = {}

    def set_project_dir(self, project_dir: str):
        self.project_dir = project_dir
        self.temp_config_path = os.path.join(project_dir, ".config.yaml")
        self.config_path = os.path.join(project_dir, "project_config.yaml")

    def _ensure_temp_config(self):
        if not os.path.exists(self.temp_config_path):
            shutil.copy(self.config_path, self.temp_config_path)

    def _load_temp_config(self):
        with open(self.temp_config_path, 'r', encoding='utf-8') as f:
            self.temp_config = yaml.safe_load(f)

    def _set_window_size(self, width: int, height: int):
        self._ensure_temp_config()
        self._load_temp_config()
        os_key = f"window_size_{'mac' if sys.platform == 'darwin' else 'windows'}"
        if os_key not in self.temp_config:
            self.temp_config[os_key] = {}
        self.temp_config[os_key]["window_width"] = width
        self.temp_config[os_key]["window_height"] = height
        logging.info(f"window_size: {width}x{height}")
        self._save()

    def _set_splitter_sizes(self, sizes: list):
        if len(sizes) < 2:
            return
            
        self._ensure_temp_config()
        self._load_temp_config()
        os_key = f"window_size_{'mac' if sys.platform == 'darwin' else 'windows'}"
        if os_key not in self.temp_config:
            self.temp_config[os_key] = {}
            
        self.temp_config[os_key]["image_widget_width"] = sizes[0]
        self.temp_config[os_key]["log_widget_width"] = sizes[1]
        logging.info(f"splitter sizes: {sizes}")
        self._save()

    def _save(self):
        with open(self.temp_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.temp_config, f, allow_unicode=True, sort_keys=False)

    def save_config(self):
        size = self.main_window.size()
        self._set_window_size(size.width(), size.height())
        # splitter 각 위젯 width 저장
        if hasattr(self, 'project_view_widget'):
            splitter_sizes = self.main_window.project_view_widget.sizes()
            if len(splitter_sizes) >= 2:
                self._set_splitter_sizes(splitter_sizes)
        self._update_last_modified()
        shutil.copy(self.temp_config_path, self.config_path)
        os.remove(self.temp_config_path)
        logging.info(f"size: {size}")
        logging.info(f"splitter_sizes: {splitter_sizes}")
        logging.info(f"update_last_modified: {self.temp_config['project']['last_modified']}")
        self.temp_config = {}

    def _update_last_modified(self):
        self.temp_config["project"]["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._save()

    def is_exist_temp_config(self):
        return os.path.exists(self.temp_config_path)