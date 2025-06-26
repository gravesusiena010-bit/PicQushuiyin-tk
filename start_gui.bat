@echo off
chcp 65001 >nul
echo ========================================
echo 🎨 高级图片去水印工具 GUI版本
echo ========================================
echo.
echo 正在启动GUI界面...
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查依赖包
echo 📦 检查依赖包...
python -c "import cv2, numpy, PIL, tkinterdnd2" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  检测到缺少依赖包，正在自动安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败，请手动执行: pip install -r requirements.txt
        pause
        exit /b 1
    )
    echo ✅ 依赖包安装完成
)

:: 启动GUI程序
echo 🚀 启动GUI界面...
python watermark_remover_gui.py

if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错，请检查错误信息
    pause
)

echo.
echo 👋 程序已退出，感谢使用！
pause