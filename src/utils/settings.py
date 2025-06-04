import yaml
import os
from typing import Any, Dict
from .helper import get_resource_path
import sys

class Settings:
    """애플리케이션 설정을 관리하는 클래스입니다."""
    
    _instance = None
    _settings: Dict[str, Any] = {}
    _default_settings: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance
    
    def _load_settings(self):
        """설정 파일을 로드합니다."""
        default_settings_path = get_resource_path(os.path.join("src", "config", "default_settings.yaml"))
        settings_path = get_resource_path(os.path.join("src", "config", "settings.yaml"))
        
        # 기본 설정 파일 로드
        try:
            if os.path.exists(default_settings_path):
                with open(default_settings_path, 'r', encoding='utf-8') as f:
                    self._default_settings = yaml.safe_load(f)
            else:
                raise FileNotFoundError("default_settings.yaml 파일이 없습니다.")
        except Exception as e:
            raise
        
        # 사용자 설정 파일 로드
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    self._settings = yaml.safe_load(f) or {}
            else:
                self._settings = {}
                # 설정 파일이 없으면 생성
                os.makedirs(os.path.dirname(settings_path), exist_ok=True)
                self.save_settings()
        except Exception as e:
            print(f"사용자 설정 파일 로드 중 오류 발생: {e}")
            self._settings = {}
    
    def save_settings(self):
        """설정을 파일에 저장합니다."""
        settings_path = get_resource_path(os.path.join("src", "config", "settings.yaml"))
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._settings, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            print(f"settings.py 설정 파일 저장 중 오류 발생: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정값을 가져옵니다."""
        keys = key.split('.')
        
        # 사용자 설정에서 먼저 찾기
        value = self._settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is not None:
                    continue
            break
        else:
            return value
        
        # 기본 설정에서 찾기
        value = self._default_settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """설정값을 설정합니다."""
        keys = key.split('.')
        target = self._settings
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self.save_settings()
    
    def get_recent_projects(self) -> list:
        """최근 프로젝트 목록을 가져옵니다."""
        return self.get('project.recent_projects', [])
    
    def add_recent_project(self, path: str):
        """최근 프로젝트를 추가합니다."""
        recent = self.get_recent_projects()
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        recent = recent[:5]  # 최대 5개만 유지
        self.set('project.recent_projects', recent)

    def get_window_size(self):
        if sys.platform == "darwin":
            base = self.get('darwin', {})
        else:
            base = self.get('window', {})
        width = base.get('width', 1500)
        height = base.get('height', 1100)
        min_width = base.get('min_width', 1500)
        min_height = base.get('min_height', 1100)

        return width, height, min_width, min_height

    def get_project_view_widget_width(self):
        if sys.platform == "darwin":
            base = self.get('darwin', {})
        else:
            base = self.get('window', {})
        image_widget_width = base.get('image_widget_width', 899)
        log_widget_width = base.get('log_widget_width', 599)
        return image_widget_width, log_widget_width