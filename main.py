# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

import paramiko
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


DEFAULT_CONFIG = {
    "ssh": {
        "host": "129.211.190.137",
        "port": 22,
        "username": "deploy",
        "password": "QAZqaz@11",
    },
    "projects": {
        "etc9901": {
            "path": "/www/wwwroot/etc9901",
            "branch": "dev_144",
        },
        "pro-etc9901": {
            "path": "/www/wwwroot/pro-etc9901",
            "branch": "dev_v2",
        },
        "card.jieyouetc.com": {
            "path": "/www/wwwroot/card.jieyouetc.com",
            "branch": "dev",
        },
    },
}


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


CONFIG_PATH = get_base_dir() / "config.json"


def ensure_config_file():
    if CONFIG_PATH.exists():
        return

    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(DEFAULT_CONFIG, file, ensure_ascii=False, indent=2)


def load_config():
    ensure_config_file()

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"未找到配置文件: {CONFIG_PATH}")

    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = json.load(file)

    ssh_config = config.get("ssh", {})
    projects = config.get("projects", {})

    required_ssh_keys = ["host", "port", "username", "password"]
    missing_keys = [key for key in required_ssh_keys if not ssh_config.get(key)]
    if missing_keys:
        raise ValueError(f"SSH 配置缺少字段: {', '.join(missing_keys)}")

    if not projects:
        raise ValueError("项目配置不能为空")

    normalized_projects = {}
    for project_name, project_config in projects.items():
        if not isinstance(project_config, dict):
            raise ValueError(f"项目配置格式错误: {project_name}")

        target_dir = project_config.get("path")
        branch = project_config.get("branch")

        if not target_dir or not branch:
            raise ValueError(f"项目 {project_name} 缺少 path 或 branch 配置")

        normalized_projects[project_name] = {
            "path": target_dir,
            "branch": branch,
        }

    return ssh_config, normalized_projects


class PullWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(bool)

    def __init__(self, ssh_config, projects, selected_projects):
        super().__init__()
        self.ssh_config = ssh_config
        self.projects = projects
        self.selected_projects = selected_projects

    def run(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.log_signal.emit(
                f"开始连接服务器 {self.ssh_config['host']}:{self.ssh_config['port']}"
            )
            ssh.connect(
                hostname=self.ssh_config["host"],
                port=self.ssh_config["port"],
                username=self.ssh_config["username"],
                password=self.ssh_config["password"],
                timeout=10,
            )
            self.log_signal.emit("SSH 连接成功")

            for project_name in self.selected_projects:
                project_config = self.projects[project_name]
                target_dir = project_config["path"]
                branch = project_config["branch"]
                self.log_signal.emit(f"\n开始拉取项目: {project_name}")
                self.log_signal.emit(f"目标目录: {target_dir}")
                self.log_signal.emit(f"目标分支: {branch}")

                cmd = (
                    f"cd {target_dir} && "
                    f"git fetch origin && "
                    f"git checkout {branch} && "
                    f"git pull origin {branch}"
                )
                _, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

                for line in iter(stdout.readline, ""):
                    if not line:
                        break
                    self.log_signal.emit(line.rstrip())

                for line in iter(stderr.readline, ""):
                    if not line:
                        break
                    self.log_signal.emit(line.rstrip())

            self.log_signal.emit("\n所有选中项目拉取完成")
            self.finished_signal.emit(True)
        except Exception as exc:
            self.log_signal.emit(f"\n执行失败: {exc}")
            self.finished_signal.emit(False)
        finally:
            ssh.close()


class PullTool(QWidget):
    def __init__(self, ssh_config, projects):
        super().__init__()
        self.ssh_config = ssh_config
        self.projects = projects
        self.worker = None
        self.checkboxes = {}
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("代码拉取工具")
        self.resize(720, 520)

        main_layout = QVBoxLayout()

        title_label = QLabel("请选择需要拉取代码的项目：")
        main_layout.addWidget(title_label)

        for project_name, project_config in self.projects.items():
            checkbox = QCheckBox(
                f"{project_name}  ({project_config['path']})  [分支: {project_config['branch']}]"
            )
            self.checkboxes[project_name] = checkbox
            main_layout.addWidget(checkbox)

        button_layout = QHBoxLayout()
        self.select_all_button = QPushButton("全选")
        self.select_all_button.clicked.connect(self.select_all)
        button_layout.addWidget(self.select_all_button)

        self.unselect_all_button = QPushButton("取消全选")
        self.unselect_all_button.clicked.connect(self.unselect_all)
        button_layout.addWidget(self.unselect_all_button)

        self.confirm_button = QPushButton("确认拉取")
        self.confirm_button.clicked.connect(self.start_pull)
        button_layout.addWidget(self.confirm_button)

        self.clear_button = QPushButton("清空日志")
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)

        main_layout.addLayout(button_layout)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        main_layout.addWidget(self.log_view)

        self.setLayout(main_layout)

    def append_log(self, message):
        self.log_view.append(message)

    def clear_log(self):
        self.log_view.clear()

    def select_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)

    def unselect_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)

    def start_pull(self):
        selected_projects = [
            name for name, checkbox in self.checkboxes.items() if checkbox.isChecked()
        ]

        if not selected_projects:
            QMessageBox.warning(self, "提示", "请至少选择一个项目。")
            return

        self.confirm_button.setEnabled(False)
        self.append_log("=" * 60)
        self.append_log(f"本次选择项目: {', '.join(selected_projects)}")

        self.worker = PullWorker(
            self.ssh_config,
            self.projects,
            selected_projects,
        )
        self.worker.log_signal.connect(self.append_log)
        self.worker.finished_signal.connect(self.on_pull_finished)
        self.worker.start()

    def on_pull_finished(self, success):
        self.confirm_button.setEnabled(True)
        if success:
            QMessageBox.information(self, "完成", "代码拉取完成。")
        else:
            QMessageBox.critical(self, "失败", "代码拉取失败，请查看日志。")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        ssh_config, projects = load_config()
        window = PullTool(ssh_config, projects)
        window.show()
        sys.exit(app.exec())
    except Exception as exc:
        QMessageBox.critical(None, "启动失败", str(exc))
        sys.exit(1)
