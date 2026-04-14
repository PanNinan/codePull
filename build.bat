@echo off
setlocal

cd /d %~dp0

py -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name CodePullTool ^
  main.py

if errorlevel 1 (
  echo.
  echo 打包失败。
  exit /b 1
)

echo.
echo 打包完成: dist\CodePullTool.exe
endlocal
