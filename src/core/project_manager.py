import os
import logging
from PySide6 import QtWidgets
from utils.settings import Settings
from utils.config import ProjectConfig
import yaml
from utils.helper import get_resource_path
from ui.dialogs.error_dialog import ErrorDialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.temp_config_manager import TempConfigManager
    from ui.main_window import AstromapperMainWindow

def setup_logging(project_dir: str):
    formatter = logging.Formatter('[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s] %(message)s')
    file_handler = logging.FileHandler(os.path.join(project_dir, 'log.txt'), encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = []
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class ProjectManager:
    def __init__(self, main_window: 'AstromapperMainWindow'):
        self.main_window = main_window
        self.settings = Settings()
        self.temp_config_manager: 'TempConfigManager' = main_window.temp_config_manager

    def check_project_config(self, project_dir: str):
        config_path = os.path.join(project_dir, "project_config.yaml")
        return os.path.exists(config_path)

    def check_project_version(self, project_dir: str):
        default_config_path = get_resource_path(os.path.join("src", "config", "default_config.yaml"))
        config_path = os.path.join(project_dir, "project_config.yaml")
        with open(default_config_path, 'r', encoding='utf-8') as f:
            default_config = yaml.safe_load(f)
        default_version = default_config.get('project', {}).get('version')
        with open(config_path, 'r', encoding='utf-8') as f:
            loaded_config = yaml.safe_load(f)
        current_version = loaded_config.get('project', {}).get('version')
        if current_version != default_version:
            logging.error(f"Project version mismatch!\nCurrent: {current_version} / Required: {default_version}\nPlease create a new project.")
            self.show_error_msg(f"Project version mismatch!\nCurrent: {current_version} / Required: {default_version}\nPlease create a new project.")
            return False
        return True

    def show_error_msg(self, error_msg: str):
        dialog = ErrorDialog(error_msg, self.main_window)
        dialog.exec()

    def initialize_project(self, project_dir: str):
        setup_logging(project_dir)
        self.main_window.project_dir = project_dir
        self.temp_config_manager.set_project_dir(project_dir)
        self.main_window.initialize_project_config(ProjectConfig(project_dir))
        self.settings.add_recent_project(project_dir)
        display_path = project_dir
        if len(project_dir) > 30:
            display_path = "..." + project_dir[-30:]
        self.main_window.status_bar.showLeftMessage(f"Project: {display_path}")
        _has_img, _img_info = self.main_window.project_config.get_image_info()
        if _has_img:
            self.main_window.image_widget.load_image(_img_info["path"])
        else:
            self.main_window.image_widget.show_open_image_btn()
        self.main_window.log_widget.update_log_frame(is_init=True)
        self.main_window.show_project_view_widget()

    def open_project(self, is_new: bool = False, _project_dir: str = None):
        if hasattr(self.main_window, 'temp_config_manager') and self.main_window.temp_config_manager.is_exist_temp_config():
            if not self.main_window.show_save_dialog():
                return
        if _project_dir and not is_new:
            project_dir = _project_dir
        else:
            project_dir = QtWidgets.QFileDialog.getExistingDirectory(
                self.main_window,
                "Select Project Location",
                "",
                QtWidgets.QFileDialog.ShowDirsOnly
            )
        if not project_dir:
            return
        if is_new:
            if self.check_project_config(project_dir):
                self.show_error_msg("A project already exists in this directory.")
                logging.error(f"A project already exists in this directory.")
                return
        else:
            if not self.check_project_config(project_dir):
                self.show_error_msg("No project exists. Please create a new project.")
                logging.error(f"No project exists. Please create a new project.")
                return
            if not self.check_project_version(project_dir):
                return
        self.initialize_project(project_dir)
        if is_new:
            sub_folders = self.main_window.settings.get("sub_folder")
            for folder in sub_folders.values():
                folder_path = os.path.join(project_dir, folder)
                os.makedirs(folder_path, exist_ok=True)
            logging.info(f"create project: {project_dir}")
            screen = QtWidgets.QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            window_geometry = self.main_window.geometry()
            center_x = (screen_geometry.width() - window_geometry.width()) // 2
            center_y = (screen_geometry.height() - window_geometry.height()) // 2
            self.main_window.move(center_x, center_y)
        else:
            settings_dict = self.main_window.project_config.get_window_size()
            window_width = settings_dict.get("window_width", 1500)
            window_height = settings_dict.get("window_height", 1100)
            image_widget_width = settings_dict.get("image_widget_width", 899)
            log_widget_width = settings_dict.get("log_widget_width", 599)
            
            # 윈도우 크기를 설정하고 화면 중앙에 위치시킴
            self.main_window.resize(window_width, window_height)
            
            # 화면 중앙에 윈도우 위치시키기
            screen = QtWidgets.QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            window_geometry = self.main_window.geometry()
            center_x = (screen_geometry.width() - window_geometry.width()) // 2
            center_y = (screen_geometry.height() - window_geometry.height()) // 2
            self.main_window.move(center_x, center_y)
            
            self.main_window.project_view_widget.setSizes([image_widget_width, log_widget_width])
            logging.info(f"open project: {project_dir}")
        self.save_current_project()

    def open_recent_project(self, project_dir):
        if os.path.exists(project_dir):
            self.open_project(is_new=False, _project_dir=project_dir) 
        else:
            self.show_error_msg("Project not found.")
            self.remove_from_recent_projects(project_dir)

    def remove_from_recent_projects(self, project_dir):
        """최근 프로젝트 목록에서 지정된 프로젝트를 제거합니다."""
        recent_projects = self.main_window.settings.get_recent_projects()
        if project_dir in recent_projects:
            recent_projects.remove(project_dir)
            self.main_window.settings.set("project.recent_projects", recent_projects)
            self.main_window.settings.save_settings()
            logging.info(f"Removed from recent projects: {project_dir}")
            if self.main_window.is_init_view:
                self.main_window.init_widget.refresh_recent_list()

    def save_current_project(self):
        if self.main_window.temp_config_manager:
            self.main_window.temp_config_manager.save_config()