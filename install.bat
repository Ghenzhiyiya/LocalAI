@echo off
chcp 65001 >nul
echo ========================================
echo    📦 LocalAI 环境安装脚本
echo ========================================
echo.
echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo.
    echo 请先安装Python 3.8或更高版本:
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装最新版本的Python
    echo 3. 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ 找到Python版本: %PYTHON_VERSION%
echo.

echo 正在检查pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到pip
    echo 请重新安装Python并确保包含pip
    pause
    exit /b 1
)

echo ✅ pip检查通过
echo.

echo 🔄 升级pip到最新版本...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️  pip升级失败，继续安装...
)

echo.
echo 📥 安装项目依赖...
echo 这可能需要几分钟时间，请耐心等待...
echo.

REM 安装基础依赖
echo 正在安装 gradio...
pip install gradio==4.7.1
if errorlevel 1 (
    echo ❌ gradio安装失败
    pause
    exit /b 1
)

echo 正在安装 huggingface-hub...
pip install huggingface-hub==0.19.4
if errorlevel 1 (
    echo ❌ huggingface-hub安装失败
    pause
    exit /b 1
)

echo 正在安装 llama-cpp-python...
echo 注意: 这个包比较大，可能需要较长时间...
pip install llama-cpp-python==0.2.11
if errorlevel 1 (
    echo ❌ llama-cpp-python安装失败
    echo 尝试使用预编译版本...
    pip install llama-cpp-python --prefer-binary
    if errorlevel 1 (
        echo ❌ 所有安装方式都失败了
        echo 请检查网络连接或尝试手动安装
        pause
        exit /b 1
    )
)

echo 正在安装其他依赖...
pip install requests tqdm numpy transformers
if errorlevel 1 (
    echo ⚠️  部分依赖安装失败，但核心功能应该可用
)

echo.
echo ========================================
echo    ✅ 安装完成！
echo ========================================
echo.
echo 🎉 LocalAI环境安装成功！
echo.
echo 📝 使用说明:
echo 1. 双击 start.bat 启动程序
echo 2. 或者在命令行运行: python app.py
echo 3. 程序会自动打开浏览器
echo 4. 首次使用需要下载AI模型
echo.
echo 📚 更多信息请查看 README.md 文件
echo.
echo 按任意键退出安装程序...
pause >nul