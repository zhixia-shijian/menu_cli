#!/usr/bin/env python3
"""
打包脚本 - 将三个程序打包成exe
"""
import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        print("正在安装PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyInstaller安装失败")
            return False

def create_build_dirs():
    """创建构建目录"""
    dirs = ["dist", "build"]
    for dir_name in dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.makedirs(dir_name, exist_ok=True)
    print("✅ 构建目录已创建")

def build_gui_version():
    """打包GUI版本"""
    print("\n🎬 开始打包GUI版本...")
    
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个exe文件
        "--windowed",                   # 无控制台窗口
        "--name=视频下载器GUI版",        # 程序名称
        "--icon=icon.ico",              # 图标文件(如果有)
        "--add-data=config;config",     # 包含配置目录
        "--add-data=logs;logs",         # 包含日志目录
        "--hidden-import=tkinter",      # 隐式导入
        "--hidden-import=yt_dlp",
        "--hidden-import=requests",
        "main.py"
    ]
    
    try:
        # 如果没有图标文件，移除图标参数
        if not os.path.exists("icon.ico"):
            cmd.remove("--icon=icon.ico")
            
        subprocess.run(cmd, check=True)
        print("✅ GUI版本打包成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ GUI版本打包失败: {e}")
        return False

def build_cli_version():
    """打包命令行版本"""
    print("\n💻 开始打包命令行版本...")
    
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个exe文件
        "--console",                    # 保留控制台窗口
        "--name=视频下载器CLI版",        # 程序名称
        "--add-data=config;config",     # 包含配置目录
        "--add-data=logs;logs",         # 包含日志目录
        "--hidden-import=yt_dlp",
        "--hidden-import=requests",
        "--hidden-import=argparse",
        "cli_main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 命令行版本打包成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令行版本打包失败: {e}")
        return False

def build_menu_version():
    """打包菜单版本"""
    print("\n📋 开始打包菜单版本...")
    
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个exe文件
        "--console",                    # 保留控制台窗口
        "--name=视频下载器菜单版",        # 程序名称
        "--add-data=config;config",     # 包含配置目录
        "--add-data=logs;logs",         # 包含日志目录
        "--hidden-import=yt_dlp",
        "--hidden-import=requests",
        "menu_cli.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ 菜单版本打包成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 菜单版本打包失败: {e}")
        return False

def create_spec_files():
    """创建spec文件用于高级配置"""
    
    # GUI版本spec文件
    gui_spec = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('logs', 'logs'),
    ],
    hiddenimports=[
        'tkinter',
        'yt_dlp',
        'requests',
        'configparser',
        'threading',
        'queue',
        'datetime',
        'json',
        'urllib.parse',
        'subprocess',
        'shutil',
        'glob',
        'pathlib'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='视频下载器GUI版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    # CLI版本spec文件
    cli_spec = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cli_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('logs', 'logs'),
    ],
    hiddenimports=[
        'yt_dlp',
        'requests',
        'argparse',
        'configparser',
        'threading',
        'datetime',
        'json',
        'urllib.parse',
        'subprocess',
        'shutil',
        'glob',
        'pathlib'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='视频下载器CLI版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    # 菜单版本spec文件
    menu_spec = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['menu_cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('logs', 'logs'),
    ],
    hiddenimports=[
        'yt_dlp',
        'requests',
        'configparser',
        'threading',
        'datetime',
        'json',
        'urllib.parse',
        'subprocess',
        'shutil',
        'glob',
        'pathlib'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='视频下载器菜单版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""

    # 写入spec文件
    with open("gui_version.spec", "w", encoding="utf-8") as f:
        f.write(gui_spec)
    
    with open("cli_version.spec", "w", encoding="utf-8") as f:
        f.write(cli_spec)
    
    with open("menu_version.spec", "w", encoding="utf-8") as f:
        f.write(menu_spec)
    
    print("✅ Spec文件已创建")

def build_with_spec():
    """使用spec文件打包"""
    print("\n🔧 使用spec文件进行高级打包...")
    
    spec_files = [
        ("gui_version.spec", "GUI版本"),
        ("cli_version.spec", "CLI版本"), 
        ("menu_version.spec", "菜单版本")
    ]
    
    success_count = 0
    for spec_file, name in spec_files:
        print(f"\n📦 打包{name}...")
        try:
            subprocess.run(["pyinstaller", spec_file], check=True)
            print(f"✅ {name}打包成功")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ {name}打包失败: {e}")
    
    return success_count

def organize_output():
    """整理输出文件"""
    print("\n📁 整理输出文件...")
    
    # 创建最终输出目录
    output_dir = "打包完成"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # 移动exe文件
    dist_files = os.listdir("dist")
    for file in dist_files:
        if file.endswith(".exe"):
            src = os.path.join("dist", file)
            dst = os.path.join(output_dir, file)
            shutil.move(src, dst)
            print(f"✅ 移动文件: {file}")
    
    # 复制必要的文件
    necessary_files = [
        "config/settings.ini",
        "example_urls.txt",
        "README.md",
        "CLI_QUICK_REFERENCE.md"
    ]
    
    for file_path in necessary_files:
        if os.path.exists(file_path):
            dst = os.path.join(output_dir, os.path.basename(file_path))
            shutil.copy2(file_path, dst)
            print(f"✅ 复制文件: {file_path}")
    
    # 创建使用说明
    usage_text = """
🎬 视频下载器 - 使用说明

📦 包含三个版本:
1. 视频下载器GUI版.exe - 图形界面版本，双击运行
2. 视频下载器CLI版.exe - 命令行版本，在终端中使用
3. 视频下载器菜单版.exe - 交互菜单版本，双击运行

🚀 快速开始:
- 新手推荐: 双击"视频下载器GUI版.exe"
- 终端用户: 双击"视频下载器菜单版.exe"  
- 高级用户: 在命令行中使用"视频下载器CLI版.exe"

📋 支持平台:
YouTube, Bilibili, Twitter/X, Instagram, TikTok 等1700+网站

⚙️ 配置文件:
settings.ini - 程序配置文件，可自定义设置

📖 详细说明:
README.md - 完整使用说明
CLI_QUICK_REFERENCE.md - 命令行快速参考

💡 提示:
首次运行可能需要几秒钟启动时间，这是正常现象。
"""
    
    with open(os.path.join(output_dir, "使用说明.txt"), "w", encoding="utf-8") as f:
        f.write(usage_text)
    
    print(f"✅ 文件已整理到 {output_dir} 目录")

def main():
    """主函数"""
    print("🎬" + "=" * 50 + "🎬")
    print("           视频下载器打包工具")
    print("🎬" + "=" * 50 + "🎬")
    print()
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return
    
    # 创建构建目录
    create_build_dirs()
    
    # 创建spec文件
    create_spec_files()
    
    # 使用spec文件打包
    success_count = build_with_spec()
    
    if success_count > 0:
        # 整理输出文件
        organize_output()
        
        print(f"\n🎉 打包完成! 成功打包 {success_count}/3 个版本")
        print("📁 所有文件已保存到 '打包完成' 目录")
        print("\n📋 打包结果:")
        
        output_dir = "打包完成"
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.endswith(".exe"):
                    file_path = os.path.join(output_dir, file)
                    size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    print(f"   ✅ {file} ({size:.1f} MB)")
        
        print("\n💡 使用提示:")
        print("   - GUI版本: 双击运行，适合普通用户")
        print("   - 菜单版本: 双击运行，交互式操作")  
        print("   - CLI版本: 命令行使用，适合高级用户")
        
    else:
        print("\n❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main()
