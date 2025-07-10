@echo off
chcp 65001 >nul
echo 🎬========================================🎬
echo           视频下载器打包工具
echo 🎬========================================🎬
echo.

echo 📦 检查PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ❌ PyInstaller未安装，正在安装...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ PyInstaller安装失败
        pause
        exit /b 1
    )
    echo ✅ PyInstaller安装成功
) else (
    echo ✅ PyInstaller已安装
)

echo.
echo 🗂️ 清理旧文件...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist "打包完成" rmdir /s /q "打包完成"

echo.
echo 🎬 开始打包GUI版本...
pyinstaller --onefile --windowed --name="视频下载器GUI版" --add-data="config;config" main.py
if errorlevel 1 (
    echo ❌ GUI版本打包失败
) else (
    echo ✅ GUI版本打包成功
)

echo.
echo 💻 开始打包CLI版本...
pyinstaller --onefile --console --name="视频下载器CLI版" --add-data="config;config" cli_main.py
if errorlevel 1 (
    echo ❌ CLI版本打包失败
) else (
    echo ✅ CLI版本打包成功
)

echo.
echo 📋 开始打包菜单版本...
pyinstaller --onefile --console --name="视频下载器菜单版" --add-data="config;config" menu_cli.py
if errorlevel 1 (
    echo ❌ 菜单版本打包失败
) else (
    echo ✅ 菜单版本打包成功
)

echo.
echo 📁 整理输出文件...
mkdir "打包完成"
if exist "dist\视频下载器GUI版.exe" (
    move "dist\视频下载器GUI版.exe" "打包完成\"
    echo ✅ GUI版本已移动
)
if exist "dist\视频下载器CLI版.exe" (
    move "dist\视频下载器CLI版.exe" "打包完成\"
    echo ✅ CLI版本已移动
)
if exist "dist\视频下载器菜单版.exe" (
    move "dist\视频下载器菜单版.exe" "打包完成\"
    echo ✅ 菜单版本已移动
)

echo.
echo 📋 复制必要文件...
if exist "config\settings.ini" copy "config\settings.ini" "打包完成\"
if exist "example_urls.txt" copy "example_urls.txt" "打包完成\"
if exist "README.md" copy "README.md" "打包完成\"

echo.
echo 📝 创建使用说明...
echo 🎬 视频下载器 - 使用说明 > "打包完成\使用说明.txt"
echo. >> "打包完成\使用说明.txt"
echo 📦 包含三个版本: >> "打包完成\使用说明.txt"
echo 1. 视频下载器GUI版.exe - 图形界面版本，双击运行 >> "打包完成\使用说明.txt"
echo 2. 视频下载器CLI版.exe - 命令行版本，在终端中使用 >> "打包完成\使用说明.txt"
echo 3. 视频下载器菜单版.exe - 交互菜单版本，双击运行 >> "打包完成\使用说明.txt"
echo. >> "打包完成\使用说明.txt"
echo 🚀 快速开始: >> "打包完成\使用说明.txt"
echo - 新手推荐: 双击"视频下载器GUI版.exe" >> "打包完成\使用说明.txt"
echo - 终端用户: 双击"视频下载器菜单版.exe" >> "打包完成\使用说明.txt"
echo - 高级用户: 在命令行中使用"视频下载器CLI版.exe" >> "打包完成\使用说明.txt"
echo. >> "打包完成\使用说明.txt"
echo 📋 支持平台: >> "打包完成\使用说明.txt"
echo YouTube, Bilibili, Twitter/X, Instagram, TikTok 等1700+网站 >> "打包完成\使用说明.txt"

echo.
echo 🎉 打包完成！
echo 📁 所有文件已保存到 "打包完成" 目录
echo.
echo 📋 打包结果:
dir "打包完成\*.exe" /b 2>nul
echo.
echo 💡 使用提示:
echo    - GUI版本: 双击运行，适合普通用户
echo    - 菜单版本: 双击运行，交互式操作
echo    - CLI版本: 命令行使用，适合高级用户
echo.
pause
