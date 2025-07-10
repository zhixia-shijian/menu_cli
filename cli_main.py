#!/usr/bin/env python3
"""
视频下载器终端版主程序
支持YouTube、Twitter/X、Bilibili等多平台视频下载
命令行界面版本，无需图形界面
"""
import sys
import os
import argparse
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.downloader import VideoDownloader
from utils.logger import logger
from core.config_manager import config_manager
from utils.validators import URLValidator


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
        print(error_msg)
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


def print_progress(progress):
    """打印下载进度"""
    if progress.status == 'downloading':
        percent = progress.progress if progress.progress is not None else 0
        speed = progress.speed if progress.speed is not None else "未知"
        eta = progress.eta if progress.eta is not None else "未知"
        
        # 清除当前行并打印进度
        sys.stdout.write("\r" + " " * 80)
        sys.stdout.write(f"\r下载中: {percent:.1f}% | 速度: {speed} | 剩余时间: {eta}")
        sys.stdout.flush()
    elif progress.status == 'completed':
        sys.stdout.write("\r" + " " * 80)
        sys.stdout.write(f"\r✅ 下载完成: {progress.filename}\n")
        sys.stdout.flush()
    elif progress.status == 'error':
        sys.stdout.write("\r" + " " * 80)
        sys.stdout.write(f"\r❌ 下载失败: {progress.error}\n")
        sys.stdout.flush()


def download_video(url, args=None, get_info_only=False):
    """下载视频"""
    if args is None:
        args = type('Args', (), {'output': None, 'quality': None, 'audio_only': False,
                                'video_only': False, 'format': None, 'quiet': False,
                                'verbose': False})()

    # 验证URL
    normalized_url, error = URLValidator.validate_and_normalize(url)
    if error:
        logger.error(f"URL验证失败: {error}")
        if not args.quiet:
            print(f"❌ 错误: {error}")
        return False

    # 检测平台
    platform = URLValidator.detect_platform(normalized_url)
    if not args.quiet:
        print(f"🔍 检测到平台: {platform}")

    # 创建下载器
    downloader = VideoDownloader()

    if get_info_only:
        # 仅获取视频信息
        try:
            info = downloader.get_video_info(normalized_url)
            if info:
                print("\n📋 视频信息:")
                print(f"标题: {info.get('title', '未知')}")
                print(f"上传者: {info.get('uploader', '未知')}")
                print(f"时长: {info.get('duration_string', '未知')}")
                print(f"观看次数: {info.get('view_count', '未知')}")
                print(f"上传日期: {info.get('upload_date', '未知')}")
                
                # 显示可用格式
                if 'formats' in info:
                    print("\n可用格式:")
                    for i, fmt in enumerate(info['formats'][:5]):  # 只显示前5个格式
                        print(f"  {i+1}. {fmt.get('format_id', '未知')} - "
                              f"{fmt.get('ext', '未知')} - "
                              f"{fmt.get('resolution', '未知')} - "
                              f"{fmt.get('vcodec', '未知')}")
                    if len(info['formats']) > 5:
                        print(f"  ... 还有 {len(info['formats'])-5} 种格式")
                
                return True
            else:
                print("❌ 无法获取视频信息")
                return False
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            print(f"❌ 获取视频信息失败: {e}")
            return False
    
    # 下载视频
    try:
        # 设置输出路径
        if args.output:
            download_path = args.output
        else:
            download_path = config_manager.get_download_path()
        
        # 创建下载任务
        download_id = downloader.create_download(normalized_url, download_path)
        if not download_id:
            print("❌ 创建下载任务失败")
            return False
        
        print(f"✅ 创建下载任务: {download_id}")
        print(f"📂 下载路径: {download_path}")
        
        # 开始下载
        downloader.start_download(download_id)
        
        # 监控下载进度
        while True:
            progress = downloader.get_progress(download_id)
            print_progress(progress)
            
            if progress.status in ['completed', 'error']:
                break
            
            time.sleep(0.5)
        
        return progress.status == 'completed'
    
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断下载")
        downloader.cancel_download(download_id)
        return False
    except Exception as e:
        logger.error(f"下载失败: {e}")
        print(f"\n❌ 下载失败: {e}")
        return False


def download_from_file(file_path, args=None):
    """从文件批量下载"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        if not urls:
            print("❌ 文件中没有找到有效的URL")
            return False

        print(f"📋 找到 {len(urls)} 个URL，开始批量下载...")

        success_count = 0
        for i, url in enumerate(urls, 1):
            if not args.quiet:
                print(f"\n[{i}/{len(urls)}] 下载: {url}")
            if download_video(url, args):
                success_count += 1
            else:
                if not args.quiet:
                    print(f"❌ 第 {i} 个视频下载失败")

        print(f"\n📊 批量下载完成: {success_count}/{len(urls)} 成功")
        return success_count == len(urls)

    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return False
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='🎬 视频下载器终端版 - 支持1700+网站的视频下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s -1 https://www.bilibili.com/video/BV1GJ411x7h7
  %(prog)s -2 downloads/music -3 720p https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s -4 urls.txt -5
  %(prog)s -9

支持的平台: YouTube, Bilibili, Twitter/X, Instagram, TikTok 等1700+网站
        """
    )

    # 位置参数
    parser.add_argument('url', nargs='?', help='要下载的视频URL')

    # 基本选项 (数字1-4)
    parser.add_argument('-1', '--info', action='store_true',
                       help='仅获取视频信息，不下载')
    parser.add_argument('-2', '--output', metavar='DIR',
                       help='指定下载目录 (默认: downloads)')
    parser.add_argument('-3', '--quality', metavar='QUALITY',
                       choices=['best', '1080p', '720p', '480p', 'worst'],
                       help='视频质量: best, 1080p, 720p, 480p, worst (默认: best)')
    parser.add_argument('-4', '--file', metavar='FILE',
                       help='从文件批量下载URL列表')

    # 格式选项 (数字5-8)
    parser.add_argument('-5', '--audio-only', action='store_true',
                       help='仅下载音频')
    parser.add_argument('-6', '--video-only', action='store_true',
                       help='仅下载视频(无音频)')
    parser.add_argument('-7', '--format', metavar='FORMAT',
                       help='指定下载格式 (如: mp4, webm, m4a)')
    parser.add_argument('-8', '--playlist', action='store_true',
                       help='下载整个播放列表')

    # 信息选项 (数字9)
    parser.add_argument('-9', '--list-platforms', action='store_true',
                       help='列出支持的平台')

    # 高级选项 (保留长选项)
    parser.add_argument('--no-subtitles', action='store_true',
                       help='不下载字幕')
    parser.add_argument('--no-thumbnail', action='store_true',
                       help='不下载缩略图')
    parser.add_argument('--no-metadata', action='store_true',
                       help='不下载元数据')
    parser.add_argument('--proxy', metavar='URL',
                       help='使用代理服务器 (如: http://proxy:port)')
    parser.add_argument('--rate-limit', metavar='RATE',
                       help='限制下载速度 (如: 1M, 500K)')
    parser.add_argument('--retries', type=int, metavar='N', default=3,
                       help='重试次数 (默认: 3)')
    parser.add_argument('--list-formats', metavar='URL',
                       help='列出指定URL的所有可用格式')
    parser.add_argument('--version', action='store_true',
                       help='显示版本信息')
    parser.add_argument('--verbose', action='store_true',
                       help='显示详细输出')
    parser.add_argument('--quiet', action='store_true',
                       help='静默模式，只显示错误')

    return parser.parse_args()


def main():
    """主函数"""
    try:
        logger.info("=" * 50)
        logger.info("视频下载器终端版启动")
        logger.info("=" * 50)
        
        args = parse_arguments()
        
        # 显示版本信息
        if args.version:
            print("🎬 视频下载器终端版 v2.0.0")
            print("=" * 50)
            print("支持YouTube、Twitter/X、Bilibili等1700+网站视频下载")
            print("\n数字选项快速参考:")
            print("  -1 信息  -2 目录  -3 质量  -4 批量  -5 仅音频")
            print("  -6 仅视频  -7 格式  -8 播放列表  -9 平台列表")
            return 0
        
        # 列出支持的平台
        if args.list_platforms:
            platforms = URLValidator.get_supported_platforms()
            print("🌐 支持的平台:")
            platform_names = {
                'youtube': 'YouTube (youtube.com, youtu.be)',
                'twitter': 'Twitter/X (twitter.com, x.com)',
                'instagram': 'Instagram (instagram.com)',
                'tiktok': 'TikTok (tiktok.com)',
                'bilibili': 'Bilibili (bilibili.com, b23.tv)'
            }
            for platform in platforms:
                name = platform_names.get(platform, platform)
                print(f"  ✅ {name}")
            print(f"\n📊 总计支持 1700+ 网站")
            return 0

        # 列出指定URL的格式
        if args.list_formats:
            try:
                downloader = VideoDownloader()
                info = downloader.get_video_info(args.list_formats)
                if info and 'formats' in info:
                    print(f"📋 可用格式 - {info.get('title', '未知标题')}")
                    print("-" * 60)
                    for i, fmt in enumerate(info['formats']):
                        ext = fmt.get('ext', '未知')
                        resolution = fmt.get('resolution', '未知')
                        vcodec = fmt.get('vcodec', '未知')
                        acodec = fmt.get('acodec', '未知')
                        filesize = fmt.get('filesize', 0)
                        size_str = f"{filesize/1024/1024:.1f}MB" if filesize else "未知"
                        print(f"  {i+1:2d}. {fmt.get('format_id', '未知'):>8s} | "
                              f"{ext:>4s} | {resolution:>10s} | "
                              f"V:{vcodec[:8]:>8s} | A:{acodec[:8]:>8s} | {size_str:>8s}")
                else:
                    print("❌ 无法获取格式信息")
                    return 1
            except Exception as e:
                print(f"❌ 获取格式失败: {e}")
                return 1
            return 0
        
        if not check_dependencies():
            return 1
        
        create_directories()
        
        # 批量下载
        if args.file:
            success = download_from_file(args.file, args)
            return 0 if success else 1

        # 如果没有提供URL，显示快速帮助
        if not args.url:
            print("🎬 视频下载器终端版 v2.0.0")
            print("=" * 50)
            print("使用方法: python cli_main.py [选项] <视频URL>")
            print("\n🔥 数字选项 (快速输入):")
            print("  -1  仅获取视频信息")
            print("  -2  指定下载目录")
            print("  -3  视频质量 (best/1080p/720p/480p)")
            print("  -4  批量下载文件")
            print("  -5  仅下载音频")
            print("  -6  仅下载视频")
            print("  -7  指定格式")
            print("  -8  下载播放列表")
            print("  -9  列出支持平台")
            print("\n💡 快速示例:")
            print("  python cli_main.py https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            print("  python cli_main.py -1 https://www.bilibili.com/video/BV1GJ411x7h7")
            print("  python cli_main.py -5 -2 music/ https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            print("  python cli_main.py -4 urls.txt")
            print("  python cli_main.py -3 720p https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            print("\n📖 获取完整帮助: python cli_main.py --help")
            print("🌐 支持平台: YouTube, Bilibili, Twitter/X, Instagram, TikTok 等1700+网站")
            return 0

        # 下载视频或获取信息
        success = download_video(args.url, args, args.info)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
        print("\n⚠️ 用户中断程序")
        return 0
    except Exception as e:
        logger.critical(f"程序异常退出: {e}")
        print(f"\n❌ 程序错误: {e}")
        print("请查看日志文件获取详细信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
