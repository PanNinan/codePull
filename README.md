# CodePull 项目说明

[![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml)
[![Build & Release](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/build-release.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/build-release.yml)

> 📦 **直接下载**：无需安装 Python，直接在 [Releases](https://github.com/YOUR_USERNAME/YOUR_REPO/releases) 页面下载最新 `CodePullTool.exe`。

## 项目简介

CodePull 是一个基于 Python + PySide6 开发的桌面工具，用于通过 SSH 连接远程服务器，并对配置好的代码项目执行 Git 拉取操作。

工具会读取本地 `config.json` 中的服务器和项目配置，在界面中列出可选项目，用户勾选后即可一键执行远程更新，适合日常测试环境或部署环境的代码同步场景。

## 功能简介

- 支持通过 SSH 连接远程 Linux 服务器
- 支持配置多个项目目录和对应分支
- 支持勾选一个或多个项目批量拉取代码
- 支持“全选 / 取消全选”快捷操作
- 支持实时显示执行日志，方便查看拉取过程
- 支持在程序首次启动时自动生成默认 `config.json`
- 支持使用 PyInstaller 打包为 Windows 可执行文件

## 项目结构

```text
codePull/
├── main.py                          # 主程序入口
├── config.json                      # SSH 和项目配置文件（本地使用，不提交到仓库）
├── config.example.json              # 配置模板（无密码，随代码提交）
├── requirements.txt                 # Python 依赖
├── build.bat                        # 本地手动打包脚本
├── CodePullTool.spec                # PyInstaller 配置文件
└── .github/
    ├── workflows/
    │   ├── ci.yml                   # CI：代码检查 & 配置验证
    │   └── build-release.yml        # CD：Windows EXE 打包 & 自动发布
    └── ACTIONS_GUIDE.md             # GitHub Actions 配置说明
```

## 运行环境

- Python 3.8 及以上
- 可正常访问目标服务器的 SSH
- 目标服务器已安装 Git

## 依赖安装

在项目目录下执行：

```bash
pip install -r requirements.txt
```

`requirements.txt` 中包含以下依赖：

- `paramiko`
- `PySide6`
- `pyinstaller`

## 配置说明

程序使用 `config.json` 保存 SSH 信息和项目配置。

配置结构示例如下：

```json
{
  "ssh": {
    "host": "your-server-host",
    "port": 22,
    "username": "your-username",
    "password": "your-password"
  },
  "projects": {
    "project-a": {
      "path": "/www/wwwroot/project-a",
      "branch": "dev"
    },
    "project-b": {
      "path": "/www/wwwroot/project-b",
      "branch": "release"
    }
  }
}
```

### 字段说明

#### `ssh`

- `host`：SSH 服务器地址
- `port`：SSH 端口，默认一般为 `22`
- `username`：登录用户名
- `password`：登录密码

#### `projects`

`projects` 中每个键代表一个项目名称，值为该项目的配置：

- `path`：服务器上的项目目录
- `branch`：需要拉取的 Git 分支

## 使用方法

### 方式一：直接运行源码

在项目目录下执行：

```bash
python main.py
```

程序启动后：

1. 确认 `config.json` 中的服务器和项目配置正确
2. 打开界面后勾选需要拉取的项目
3. 点击“确认拉取”按钮
4. 在下方日志窗口中查看执行过程
5. 拉取完成后会弹出完成提示

### 方式二：打包为 EXE 后运行

执行打包脚本：

```bash
build.bat
```

打包成功后会在 `dist/` 目录生成：

```text
CodePullTool.exe
```

双击即可运行。

## 程序执行流程

当用户点击“确认拉取”后，程序会按选中的项目依次在远程服务器执行以下命令：

```bash
git fetch origin && git checkout <branch> && git pull origin <branch>
```

完整执行目录为对应项目的 `path`，即：

```bash
cd <path> && git fetch origin && git checkout <branch> && git pull origin <branch>
```

## 界面说明

程序界面主要包含以下部分：

- 项目勾选列表：展示所有可拉取的项目
- `全选`：勾选全部项目
- `取消全选`：取消全部勾选
- `确认拉取`：开始执行远程拉取
- `清空日志`：清空日志输出窗口
- 日志区域：显示 SSH 连接、Git 拉取及错误信息

## 注意事项

- 请确保服务器可通过 SSH 正常连接
- 请确保配置的目录中存在 Git 仓库
- 请确保配置的分支在远程仓库中存在
- 如果首次运行时没有 `config.json`，程序会自动生成默认配置文件
- 建议不要在仓库中提交真实的服务器密码，可根据实际情况改为更安全的配置方式

## 常见问题

### 1. 启动时报配置错误

请检查 `config.json` 中是否缺少以下字段：

- `host`
- `port`
- `username`
- `password`
- 项目的 `path`
- 项目的 `branch`

### 2. 拉取失败怎么办

可从日志窗口排查以下问题：

- SSH 登录失败
- 服务器目录不存在
- 当前目录不是 Git 仓库
- 分支不存在或无权限切换
- 远程仓库拉取失败

## 打包说明

项目已提供 `build.bat`，内部使用 PyInstaller 执行如下打包逻辑：

- 单文件模式
- 窗口程序模式
- 输出文件名：`CodePullTool`

如需自定义打包行为，也可以修改 `CodePullTool.spec`。

## 适用场景

- 测试环境代码更新
- 多项目统一拉取
- 运维或开发人员日常远程同步代码
- 需要图形界面操作的简单部署辅助工具