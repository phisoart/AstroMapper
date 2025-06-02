import os
import logging
from PySide6 import QtWidgets
from utils.settings import Settings
from utils.config import ProjectConfig
import yaml
from utils.helper import get_resource_path


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
    def __init__(self, main_window):
        self.main_window = main_window
        self.settings = Settings()

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
        msg_box = QtWidgets.QMessageBox(self.main_window)
        msg_box.setWindowTitle("Error")
        msg_box.setText(error_msg)
        msg_box.exec()

    def initialize_project(self, project_dir: str):
        setup_logging(project_dir)
        self.main_window.project_dir = project_dir
        self.main_window.initialize_project_config(ProjectConfig(project_dir))
        self.settings.add_recent_project(project_dir)
        display_path = project_dir
        if len(project_dir) > 30:
            display_path = "..." + project_dir[-30:]
        self.main_window.status_bar.showLeftMessage(f"Project: {display_path}")
        _has_img, _img_info = self.main_window.project_config.get_image_info()
        if _has_img:
            self.main_window.image_widget.load_image(_img_info["path"])
        self.main_window.log_widget.update_log_frame()
        self.main_window.show_project_view_widget()

    def open_project(self, is_new: bool = False, _project_dir: str = None):
        # TODO: make save_current_project
        # 이미 프로젝트가 열려있는 경우도 확인하자.

        # if not self.save_current_project():
            # return 
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
            sub_folders = self.main_window.project_config.get_config("sub_folder")
            for folder in sub_folders.values():
                folder_path = os.path.join(project_dir, folder)
                os.makedirs(folder_path, exist_ok=True)
            logging.info(f"create project: {project_dir}")
        else:
            settings_dict = self.main_window.project_config.get_window_size()
            window_width = settings_dict.get("window_width", 1500)
            window_height = settings_dict.get("window_height", 1100)
            image_widget_width = settings_dict.get("image_widget_width", 899)
            log_widget_width = settings_dict.get("log_widget_width", 599)
            self.main_window.resize(window_width, window_height)
            self.main_window.project_view_widget.setSizes([image_widget_width, log_widget_width])
            logging.info(f"open project: {project_dir}")

    def open_recent_project(self, project_dir):
        if os.path.exists(project_dir):
            self.open_project(is_new=False, _project_dir=project_dir) 