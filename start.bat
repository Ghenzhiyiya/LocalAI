@echo off
chcp 65001 >nul
echo ========================================
echo    🤖 LocalAI 对话助手启动脚本
echo ========================================
echo.
echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.
echo 正在检查依赖包...
pip show llama-cpp-python >nul 2>&1
if errorlevel 1 (
    echo ⚠️  未找到必要依赖，正在安装...
    echo 这可能需要几分钟时间，请耐心等待...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
    echo ✅ 依赖安装完成
)

echo ✅ 依赖检查通过
echo.
echo 🚀 启动LocalAI对话助手...
echo 程序启动后会自动打开浏览器
echo 如果没有自动打开，请手动访问: http://localhost:7860
echo.
echo 按 Ctrl+C 可以停止程序
echo ========================================
echo.
python app.py
echo.
echo 程序已退出，按任意键关闭窗口...
pause >nul