# 초기설정관리파일인데, 아직.import os
import yaml
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os
from PIL import Image
import json
import sys
from utils import get_resource_path

class ProjectConfig:
    """프로젝트 설정을 관리하는 클래스입니다."""
    
    def __init__(self, project_dir: str):
        """
        프로젝트 설정을 초기화합니다.
        
        Args:
            project_dir: 프로젝트 루트 디렉토리 경로
        """
        self.project_dir = project_dir
        self.config_path = os.path.join(project_dir, "project_config.yaml")
        self.config: Dict = {}

        # 설정 파일이 없으면 새로 생성
        if not os.path.exists(self.config_path):
            self._create_default_config()
        else:
            self.load_config()
    
    def _create_default_config(self):
        """기본 설정 파일을 생성합니다."""
        default_config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "default_config.yaml"))
        try:
            with open(default_config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
            # 프로젝트별로 name, path, created_date, last_modified만 갱신 (시:분까지)
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.config["project"]["name"] = os.path.basename(self.project_dir)
            self.config["project"]["path"] = self.project_dir
            self.config["project"]["created_date"] = now
            self.config["project"]["last_modified"] = now
        except Exception as e:
            print(f"default_config.yaml 로드 실패 : {e}")
        self.save_config()
    
    def load_config(self):
        """설정 파일을 로드합니다."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"설정 파일 로드 중 오류 발생: {e}")
    
    def save_config(self):
        """설정을 파일에 저장합니다."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            print(f"config.py설정 파일 저장 중 오류 발생: {e}")
    
    def update_last_modified(self):
        """마지막 수정 시간을 업데이트합니다."""
        self.config["project"]["last_modified"] = datetime.now().strftime("%Y-%m-%d")
        self.save_config()
    
    def save_image_info(self, image_path: str):
        """
        이미지 정보를 설정 파일에 저장합니다.
        
        Args:
            image_path: 이미지 파일의 경로
        """
        # TODO: svs도 적용되게
        try:
            # 파일 크기 가져오기
            file_size = os.path.getsize(image_path)
            
            # 이미지 크기 정보만 가져오기
            with Image.open(image_path) as img:
                width, height = img.size
                format = img.format
            
            # 설정 업데이트
            self.config["image"] = {
                "name": os.path.basename(image_path),
                "size": file_size,
                "width": width,
                "height": height,
                "format": format,
                "path": image_path
            }
            
            # 설정 저장
            self.save_config()
            self.update_last_modified()
            
        except Exception as e:
            print(f"이미지 정보 저장 중 오류 발생: {e}")
    
    def get_image_info(self) -> Tuple[bool, Optional[Dict]]:
        """
        이미지 설정을 반환합니다.
        
        Returns:
            Tuple[bool, Optional[Dict]]: (이미지 존재 여부, 이미지 설정)
            - 이미지가 존재하면 (True, 이미지 설정)
            - 이미지가 없으면 (False, None)
        """
        image_info = self.config.get("image", {})
        if image_info.get("name", "") == "":
            return False, None
        return True, image_info

    def get_window_size(self) -> Dict:
        """프로젝트 설정을 반환합니다."""
        # OS별 설정 이름 생성
        os_specific_name = f"window_size_{'mac' if sys.platform == 'darwin' else 'windows'}"
        
        # OS별 설정이 있으면 해당 설정 반환, 없으면 기본 설정 반환
        return self.config.get(os_specific_name, {})
    
    def get_config(self, _config_name: str) -> Dict:
        """프로젝트 설정을 반환합니다."""
        return self.config.get(_config_name, {})

    def get_point_info_visible(self) -> list:
        """
        point_info의 visible 설정을 반환합니다.
        project_config.yaml의 log_widget 설정을 사용합니다.
        빈 문자열("")에 해당하는 컬럼은 무조건 True로 설정됩니다.
        
        Returns:
            list: 각 컬럼의 visible 상태 리스트
        """
        try:
            point_info_path = get_resource_path(os.path.join("res", "data", "point_info.json"))
            with open(point_info_path, "r", encoding="utf-8") as f:
                point_info = json.load(f)["point_info"]
        except Exception:
            point_info = ["checkbox","#", "X", "Y", "Width", "Height", "Well", "Color", "Note", "Delete"]
        
        # project_config의 log_widget 설정에서 visible 상태 가져오기
        log_widget_config = self.config.get("log_widget", {})
        
        # 각 컬럼의 visible 상태 설정
        visible_list = []
        for col in point_info:
            if col == "":  # 빈 문자열인 경우 무조건 True
                visible_list.append(True)
            else:
                visible_list.append(log_widget_config.get(col, True))  # 설정이 없으면 True 
        return visible_list

    def set_window_size(self, width: int, height: int):
        """
        현재 윈도우 사이즈를 config에 저장합니다.
        Args:
            width (int): 윈도우 너비
            height (int): 윈도우 높이
        """
        os_specific_name = f"window_size_{'mac' if sys.platform == 'darwin' else 'windows'}"

        self.config.setdefault(os_specific_name, {})
        self.config[os_specific_name]["window_width"] = width
        self.config[os_specific_name]["window_height"] = height
        self.save_config()

    def set_splitter_widths(self, image_width: int, log_width: int):
        """
        splitter의 각 위젯(이미지, 로그)의 width를 config에 저장합니다.
        """
        os_specific_name = f"window_size_{'mac' if sys.platform == 'darwin' else 'windows'}"

        self.config.setdefault(os_specific_name, {})
        self.config[os_specific_name]["image_widget_width"] = image_width
        self.config[os_specific_name]["log_widget_width"] = log_width
        self.save_config()

    def set_log_widget_widths(self, widths: list):
        self.config.setdefault("log_widget", {})
        self.config["log_widget"]["widths"] = widths
        self.save_config()

    def get_log_widget_widths(self) -> list:
        print(f"widths: {self.config.get('log_widget', {}).get('widths', [])}")
        return self.config.get("log_widget", {}).get("widths", [])
    
    def set_tool_color(self, color: str):
        self.config.setdefault("tool", {})
        self.config["tool"]["color"] = color
        self.save_config()
    
    def get_color(self):
        """현재 선택된 색상을 반환합니다."""
        return self.config.get("tool", {}).get("color", "#FF0000")  # tool.color 값을 가져옴

    def get_color_name(self):
        """현재 선택된 색상의 이름을 반환합니다."""
        return self.config.get("tool", {}).get("color_name", "Red")  # tool.color_name 값을 가져옴

    def set_color_name(self, color_name: str):
        """색상의 이름을 설정합니다."""
        self.config.setdefault("tool", {})
        self.config["tool"]["color_name"] = color_name
        self.save_config()

    def set_color(self, color: str):
        """색상을 설정합니다."""
        self.config.setdefault("tool", {})
        self.config["tool"]["color"] = color
        self.save_config()
