#!/usr/bin/env python3
"""
视频下载器主程序
支持YouTube、Twitter/X、Bilibili等多平台视频下载
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from utils.logger import logger
from core.config_manager import config_manager


def check_dependencies():
    """检查依赖项"""
    try:
        import yt_dlp
        import requests
        logger.info("依赖项检查通过")
        return True
    except ImportError as e:
        error_msg = f"缺少必要的依赖项: {e}\n\n请运行以下命令安装依赖:\npip install -r requirements.txt"
        logger.error(error_msg)
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("依赖项错误", error_msg)
        root.destroy()
        return False


def create_directories():
    """创建必要的目录"""
    directories = [
        config_manager.get_download_path(),
        'logs',
        'config'
    ]
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"创建目录: {directory}")
        except Exception as e:
            logger.error(f"创建目录失败 {directory}: {e}")


def main():
    """主函数"""
    try:
        logger.info("=" * 50)
        logger.info("视频下载器启动")
        logger.info("=" * 50)
        
        if not check_dependencies():
            return 1
        
        create_directories()
        
        logger.info("启动GUI界面")
        app = MainWindow()
        app.run()
        
        logger.info("应用程序正常退出")
        return 0
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        return 0
    except Exception as e:
        logger.critical(f"程序异常退出: {e}")
        
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("程序错误", f"程序遇到错误:\n{str(e)}\n\n请查看日志文件获取详细信息")
            root.destroy()
        except:
            pass
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
