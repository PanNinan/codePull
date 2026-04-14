# GitHub Actions 配置说明

本项目通过 GitHub Actions 实现自动化 CI/CD 流程，包括代码质量检查和 Windows EXE 自动打包发布。

---

## 工作流文件概览

| 文件 | 触发条件 | 作用 |
|------|----------|------|
| `.github/workflows/ci.yml` | push / PR | 代码语法检查、Flake8 风格检查、config.json 结构验证 |
| `.github/workflows/build-release.yml` | 推送 `v*.*.*` tag 或手动触发 | PyInstaller 打包 Windows EXE，创建 GitHub Release |

---

## 必须配置的 GitHub Secrets

> 进入仓库 → Settings → Secrets and variables → Actions → New repository secret

| Secret 名称 | 说明 | 示例值 |
|-------------|------|--------|
| `SSH_HOST` | 服务器 IP 或域名 | `129.211.190.137` |
| `SSH_PORT` | SSH 端口 | `22` |
| `SSH_USERNAME` | SSH 登录用户名 | `deploy` |
| `SSH_PASSWORD` | SSH 登录密码 | `your-password` |

> **说明**：Secrets 不是必须的。如果未配置，打包时会使用仓库中的 `config.example.json` 模板（无真实密码），用户下载后自行填写。

---

## 发布新版本的步骤

```bash
# 1. 确认代码已提交并推送
git add .
git commit -m "feat: 新功能描述"
git push origin main

# 2. 打标签（遵循语义化版本）
git tag v1.0.0
git push origin v1.0.0
```

推送 tag 后，GitHub Actions 将自动：
1. 在 Windows 环境安装 Python 3.11 和依赖
2. 使用 PyInstaller 打包为单文件 EXE
3. 在 GitHub Releases 页面发布，附带 EXE 和 config 模板

---

## 本地开发配置

由于 `config.json` 已加入 `.gitignore`，本地首次使用需手动创建：

```bash
# 复制示例文件
cp config.example.json config.json

# 编辑填入真实服务器信息
```

---

## CI 检查说明

### 语法检查（py_compile）

验证 `main.py` 无语法错误，失败会阻断整个 CI。

### Flake8 风格检查

代码风格不规范会报错（允许行长 120 字符）。

### Pylint 静态分析

评分低于 6.0 时仅警告，不阻断 CI（`continue-on-error: true`）。

### config.json 结构验证

确认配置文件中 SSH 字段和项目字段均完整，防止带有结构缺失的配置文件入库。

---

## 打包产物说明

每次 tag 触发的构建会在 GitHub Actions Artifacts 中保留 30 天，Release 页面永久保存：

```
CodePullTool.exe   # Windows 单文件可执行程序（无需安装 Python）
config.json        # 脱敏配置模板（用户需自行填写服务器信息）
```
