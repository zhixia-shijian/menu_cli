#!/usr/bin/env python3
"""
视频下载器交互式终端版
提供菜单式操作界面，用户直接输入数字选择功能
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.downloader import VideoDownloader
from utils.logger import logger
from core.config_manager import config_manager
from utils.validators import URLValidator


class InteractiveCLI:
    """交互式命令行界面"""
    
    def __init__(self):
        self.downloader = VideoDownloader()
        self.current_url = None
        self.current_quality = "best"
        self.current_output = config_manager.get_download_path()
        
    def clear_screen(self):
        """清屏"""
        # 简单的清屏方式，兼容性更好
        print("\n" * 50)
        
    def print_header(self):
        """打印标题"""
        print("🎬" + "=" * 58 + "🎬")
        print("           视频下载器交互式终端版 v2.0.0")
        print("🎬" + "=" * 58 + "🎬")
        print()
        
    def print_status(self):
        """打印当前状态"""
        print("📊 当前设置:")
        print(f"   URL: {self.current_url if self.current_url else '未设置'}")
        print(f"   质量: {self.current_quality}")
        print(f"   目录: {self.current_output}")
        print()
        
    def print_menu(self):
        """打印主菜单"""
        print("🔥 请选择操作 (输入数字):")
        print("   1. 设置视频URL")
        print("   2. 设置下载目录")
        print("   3. 设置视频质量")
        print("   4. 获取视频信息")
        print("   5. 下载视频")
        print("   6. 仅下载音频")
        print("   7. 批量下载")
        print("   8. 查看支持平台")
        print("   9. 设置选项")
        print("   0. 退出程序")
        print()
        
    def get_user_input(self, prompt="请输入选择: "):
        """获取用户输入"""
        try:
            return input(prompt).strip()
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            sys.exit(0)
            
    def set_url(self):
        """设置URL"""
        print("🔗 设置视频URL")
        print("-" * 30)
        url = self.get_user_input("请输入视频URL: ")
        
        if not url:
            print("❌ URL不能为空")
            return
            
        # 验证URL
        normalized_url, error = URLValidator.validate_and_normalize(url)
        if error:
            print(f"❌ {error}")
            return
            
        platform = URLValidator.detect_platform(normalized_url)
        self.current_url = normalized_url
        print(f"✅ URL已设置")
        print(f"🔍 检测到平台: {platform}")
        
    def set_output_dir(self):
        """设置输出目录"""
        print("📁 设置下载目录")
        print("-" * 30)
        print(f"当前目录: {self.current_output}")
        new_dir = self.get_user_input("请输入新目录 (回车保持当前): ")
        
        if new_dir:
            self.current_output = new_dir
            print(f"✅ 下载目录已设置为: {new_dir}")
        else:
            print("📁 保持当前目录")
            
    def set_quality(self):
        """设置视频质量"""
        print("🎯 设置视频质量")
        print("-" * 30)
        print("可选质量:")
        qualities = ["best", "1080p", "720p", "480p", "worst"]
        for i, quality in enumerate(qualities, 1):
            marker = "👉" if quality == self.current_quality else "  "
            print(f"   {i}. {quality} {marker}")
        print()
        
        choice = self.get_user_input("请选择质量 (1-5): ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(qualities):
                self.current_quality = qualities[index]
                print(f"✅ 视频质量已设置为: {self.current_quality}")
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入数字")
            
    def get_video_info(self):
        """获取视频信息"""
        if not self.current_url:
            print("❌ 请先设置视频URL (选项1)")
            return
            
        print("📋 获取视频信息中...")
        try:
            info = self.downloader.get_video_info(self.current_url)
            if info:
                print("\n📺 视频信息:")
                print(f"   标题: {info.get('title', '未知')}")
                print(f"   上传者: {info.get('uploader', '未知')}")
                print(f"   时长: {info.get('duration_string', '未知')}")
                print(f"   观看次数: {info.get('view_count', '未知')}")
                print(f"   上传日期: {info.get('upload_date', '未知')}")
                
                if 'formats' in info:
                    print(f"\n📊 可用格式数量: {len(info['formats'])}")
                    print("   (前5个格式预览)")
                    for i, fmt in enumerate(info['formats'][:5]):
                        print(f"   {i+1}. {fmt.get('format_id', '未知')} - "
                              f"{fmt.get('ext', '未知')} - "
                              f"{fmt.get('resolution', '未知')}")
            else:
                print("❌ 无法获取视频信息")
        except Exception as e:
            print(f"❌ 获取信息失败: {e}")
            
    def download_video(self, audio_only=False):
        """下载视频"""
        if not self.current_url:
            print("❌ 请先设置视频URL (选项1)")
            return
            
        media_type = "音频" if audio_only else "视频"
        print(f"⬇️ 开始下载{media_type}...")
        print(f"   URL: {self.current_url}")
        print(f"   质量: {self.current_quality}")
        print(f"   目录: {self.current_output}")
        print()
        
        try:
            # 创建下载任务
            download_id = self.downloader.create_download(self.current_url, self.current_output)
            if not download_id:
                print("❌ 创建下载任务失败")
                return
                
            # 开始下载
            self.downloader.start_download(download_id)
            
            # 监控进度
            print("📊 下载进度:")
            while True:
                progress = self.downloader.get_progress(download_id)
                
                if progress.status == 'downloading':
                    percent = progress.progress if progress.progress is not None else 0
                    speed = progress.speed if progress.speed is not None else "未知"
                    eta = progress.eta if progress.eta is not None else "未知"
                    
                    # 进度条
                    bar_length = 30
                    filled_length = int(bar_length * percent / 100)
                    bar = "█" * filled_length + "░" * (bar_length - filled_length)
                    
                    print(f"\r   [{bar}] {percent:.1f}% | {speed} | 剩余: {eta}", end="", flush=True)
                    
                elif progress.status == 'completed':
                    print(f"\n✅ {media_type}下载完成!")
                    print(f"   文件: {progress.filename}")
                    break
                    
                elif progress.status == 'error':
                    print(f"\n❌ 下载失败: {progress.error}")
                    break
                    
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n⚠️ 用户中断下载")
            self.downloader.cancel_download(download_id)
        except Exception as e:
            print(f"\n❌ 下载失败: {e}")
            
    def batch_download(self):
        """批量下载"""
        print("📦 批量下载")
        print("-" * 30)
        file_path = self.get_user_input("请输入URL列表文件路径: ")
        
        if not file_path:
            print("❌ 文件路径不能为空")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
            if not urls:
                print("❌ 文件中没有找到有效的URL")
                return
                
            print(f"📋 找到 {len(urls)} 个URL")
            confirm = self.get_user_input("确认开始批量下载? (y/N): ")
            
            if confirm.lower() != 'y':
                print("❌ 已取消")
                return
                
            success_count = 0
            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{len(urls)}] 下载: {url}")
                
                # 临时设置URL并下载
                old_url = self.current_url
                self.current_url = url
                
                try:
                    self.download_video()
                    success_count += 1
                except:
                    print(f"❌ 第 {i} 个视频下载失败")
                    
                self.current_url = old_url
                
            print(f"\n📊 批量下载完成: {success_count}/{len(urls)} 成功")
            
        except FileNotFoundError:
            print(f"❌ 文件不存在: {file_path}")
        except Exception as e:
            print(f"❌ 批量下载失败: {e}")
            
    def show_platforms(self):
        """显示支持平台"""
        print("🌐 支持的平台:")
        print("-" * 30)
        platforms = URLValidator.get_supported_platforms()
        platform_names = {
            'youtube': 'YouTube (youtube.com, youtu.be)',
            'twitter': 'Twitter/X (twitter.com, x.com)',
            'instagram': 'Instagram (instagram.com)',
            'tiktok': 'TikTok (tiktok.com)',
            'bilibili': 'Bilibili (bilibili.com, b23.tv)'
        }
        
        for platform in platforms:
            name = platform_names.get(platform, platform)
            print(f"   ✅ {name}")
        print(f"\n📊 总计支持 1700+ 网站")
        
    def show_settings(self):
        """显示设置选项"""
        print("⚙️ 设置选项")
        print("-" * 30)
        print("1. 重置为默认设置")
        print("2. 查看当前配置")
        print("3. 返回主菜单")
        print()
        
        choice = self.get_user_input("请选择: ")
        if choice == "1":
            self.current_quality = "best"
            self.current_output = config_manager.get_download_path()
            self.current_url = None
            print("✅ 已重置为默认设置")
        elif choice == "2":
            print("\n📋 当前配置:")
            print(f"   默认质量: {self.current_quality}")
            print(f"   默认目录: {self.current_output}")
            print(f"   当前URL: {self.current_url if self.current_url else '未设置'}")
        elif choice == "3":
            return
        else:
            print("❌ 无效选择")
            
    def run(self):
        """运行主循环"""
        self.clear_screen()
        self.print_header()
        
        print("🎉 欢迎使用视频下载器交互式终端版!")
        print("💡 提示: 随时按 Ctrl+C 退出程序")
        print()
        
        while True:
            self.print_status()
            self.print_menu()
            
            choice = self.get_user_input()
            print()
            
            if choice == "1":
                self.set_url()
            elif choice == "2":
                self.set_output_dir()
            elif choice == "3":
                self.set_quality()
            elif choice == "4":
                self.get_video_info()
            elif choice == "5":
                self.download_video(audio_only=False)
            elif choice == "6":
                self.download_video(audio_only=True)
            elif choice == "7":
                self.batch_download()
            elif choice == "8":
                self.show_platforms()
            elif choice == "9":
                self.show_settings()
            elif choice == "0":
                print("👋 感谢使用，再见！")
                break
            else:
                print("❌ 无效选择，请输入 0-9")
                
            print()
            self.get_user_input("按回车继续...")
            self.clear_screen()
            self.print_header()


def main():
    """主函数"""
    try:
        logger.info("=" * 50)
        logger.info("视频下载器交互式终端版启动")
        logger.info("=" * 50)
        
        # 检查依赖
        try:
            import yt_dlp
            import requests
        except ImportError as e:
            print(f"❌ 缺少依赖项: {e}")
            print("请运行: pip install -r requirements.txt")
            return 1
            
        # 创建必要目录
        directories = [config_manager.get_download_path(), 'logs', 'config']
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
        # 启动交互界面
        cli = InteractiveCLI()
        cli.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        return 0
    except Exception as e:
        logger.critical(f"程序异常退出: {e}")
        print(f"\n❌ 程序错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
