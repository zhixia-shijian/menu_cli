#!/usr/bin/env python3
"""
菜单式视频下载器
用户直接输入数字选择功能
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 全局变量存储用户设置
settings = {
    'url': None,
    'quality': 'best',
    'output': 'downloads',
    'audio_only': False
}

def show_header():
    """显示标题"""
    print("🎬" + "=" * 50 + "🎬")
    print("        视频下载器菜单版 v2.0.0")
    print("🎬" + "=" * 50 + "🎬")

def show_status():
    """显示当前状态"""
    print("\n📊 当前设置:")
    print(f"   URL: {settings['url'] if settings['url'] else '❌ 未设置'}")
    print(f"   质量: {settings['quality']}")
    print(f"   目录: {settings['output']}")
    print(f"   模式: {'🎵 仅音频' if settings['audio_only'] else '🎬 视频'}")

def show_menu():
    """显示主菜单"""
    print("\n🔥 请输入数字选择功能:")
    print("   1 - 设置视频URL")
    print("   2 - 设置下载目录") 
    print("   3 - 选择视频质量")
    print("   4 - 获取视频信息")
    print("   5 - 下载视频")
    print("   6 - 下载音频")
    print("   7 - 批量下载")
    print("   8 - 支持平台")
    print("   9 - 重置设置")
    print("   0 - 退出")

def handle_set_url():
    """处理设置URL"""
    print("\n🔗 设置视频URL")
    print("支持: YouTube, Bilibili, Twitter/X, Instagram, TikTok等")
    url = input("请输入视频URL: ").strip()
    
    if url:
        # 简单验证URL
        if any(site in url.lower() for site in ['youtube.com', 'youtu.be', 'bilibili.com', 'twitter.com', 'x.com', 'instagram.com', 'tiktok.com']):
            settings['url'] = url
            print(f"✅ URL已设置")
            
            # 检测平台
            if 'youtube.com' in url or 'youtu.be' in url:
                platform = "YouTube"
            elif 'bilibili.com' in url:
                platform = "Bilibili"
            elif 'twitter.com' in url or 'x.com' in url:
                platform = "Twitter/X"
            elif 'instagram.com' in url:
                platform = "Instagram"
            elif 'tiktok.com' in url:
                platform = "TikTok"
            else:
                platform = "其他平台"
                
            print(f"🔍 检测到平台: {platform}")
        else:
            print("⚠️ URL已设置，但可能不是支持的平台")
            settings['url'] = url
    else:
        print("❌ URL不能为空")

def handle_set_output():
    """处理设置输出目录"""
    print(f"\n📁 当前下载目录: {settings['output']}")
    new_dir = input("请输入新目录 (回车保持当前): ").strip()
    
    if new_dir:
        settings['output'] = new_dir
        print(f"✅ 下载目录已设置为: {new_dir}")
    else:
        print("📁 保持当前目录")

def handle_set_quality():
    """处理设置质量"""
    print("\n🎯 选择视频质量:")
    qualities = ["best", "1080p", "720p", "480p", "worst"]
    
    for i, quality in enumerate(qualities, 1):
        marker = " 👈 当前" if quality == settings['quality'] else ""
        print(f"   {i} - {quality}{marker}")
    
    try:
        choice = input("\n请选择质量 (1-5): ").strip()
        index = int(choice) - 1
        
        if 0 <= index < len(qualities):
            settings['quality'] = qualities[index]
            print(f"✅ 视频质量已设置为: {settings['quality']}")
        else:
            print("❌ 无效选择")
    except ValueError:
        print("❌ 请输入数字 1-5")

def handle_get_info():
    """处理获取信息"""
    if not settings['url']:
        print("\n❌ 请先设置视频URL (输入 1)")
        return
    
    print(f"\n📋 获取视频信息...")
    print(f"URL: {settings['url']}")
    
    try:
        from core.downloader import VideoDownloader
        downloader = VideoDownloader()
        info = downloader.get_video_info(settings['url'])
        
        if info:
            print("\n📺 视频信息:")
            print(f"   标题: {info.get('title', '未知')}")
            print(f"   上传者: {info.get('uploader', '未知')}")
            print(f"   时长: {info.get('duration_string', '未知')}")
            print(f"   观看次数: {info.get('view_count', '未知')}")
            
            if 'formats' in info:
                print(f"   可用格式: {len(info['formats'])} 种")
        else:
            print("❌ 无法获取视频信息")
    except Exception as e:
        print(f"❌ 获取信息失败: {e}")

def handle_download(audio_only=False):
    """处理下载"""
    if not settings['url']:
        print("\n❌ 请先设置视频URL (输入 1)")
        return
    
    media_type = "音频" if audio_only else "视频"
    print(f"\n⬇️ 开始下载{media_type}...")
    print(f"URL: {settings['url']}")
    print(f"质量: {settings['quality']}")
    print(f"目录: {settings['output']}")
    
    try:
        from core.downloader import VideoDownloader
        import time
        
        downloader = VideoDownloader()
        download_id = downloader.create_download(settings['url'], settings['output'])
        
        if download_id:
            downloader.start_download(download_id)
            print("📊 下载进度:")
            
            while True:
                progress = downloader.get_progress(download_id)
                
                if progress.status == 'downloading':
                    percent = progress.progress or 0
                    speed = progress.speed or "未知"
                    print(f"\r   进度: {percent:.1f}% | 速度: {speed}", end="", flush=True)
                    
                elif progress.status == 'completed':
                    print(f"\n✅ {media_type}下载完成!")
                    break
                    
                elif progress.status == 'error':
                    print(f"\n❌ 下载失败: {progress.error}")
                    break
                    
                time.sleep(1)
        else:
            print("❌ 创建下载任务失败")
            
    except Exception as e:
        print(f"❌ 下载失败: {e}")

def handle_batch_download():
    """处理批量下载"""
    print("\n📦 批量下载")
    file_path = input("请输入URL列表文件路径: ").strip()
    
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
        confirm = input("确认开始批量下载? (y/N): ").strip().lower()
        
        if confirm == 'y':
            print("🚀 开始批量下载...")
            # 这里可以调用实际的批量下载逻辑
            print("💡 批量下载功能开发中...")
        else:
            print("❌ 已取消")
            
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

def handle_show_platforms():
    """显示支持平台"""
    print("\n🌐 支持的平台:")
    platforms = [
        "✅ YouTube (youtube.com, youtu.be)",
        "✅ Twitter/X (twitter.com, x.com)", 
        "✅ Instagram (instagram.com)",
        "✅ TikTok (tiktok.com)",
        "✅ Bilibili (bilibili.com, b23.tv)",
        "✅ Facebook (facebook.com)",
        "✅ Reddit (reddit.com)",
        "✅ Vimeo (vimeo.com)"
    ]
    
    for platform in platforms:
        print(f"   {platform}")
    
    print(f"\n📊 总计支持 1700+ 网站")

def handle_reset():
    """重置设置"""
    print("\n🔄 重置设置")
    confirm = input("确认重置所有设置? (y/N): ").strip().lower()
    
    if confirm == 'y':
        settings['url'] = None
        settings['quality'] = 'best'
        settings['output'] = 'downloads'
        settings['audio_only'] = False
        print("✅ 设置已重置为默认值")
    else:
        print("❌ 已取消")

def main():
    """主函数"""
    print("🎉 欢迎使用视频下载器菜单版!")
    print("💡 提示: 随时按 Ctrl+C 退出")
    
    while True:
        try:
            show_header()
            show_status()
            show_menu()
            
            choice = input("\n请输入选择 (0-9): ").strip()
            
            if choice == "1":
                handle_set_url()
            elif choice == "2":
                handle_set_output()
            elif choice == "3":
                handle_set_quality()
            elif choice == "4":
                handle_get_info()
            elif choice == "5":
                handle_download(audio_only=False)
            elif choice == "6":
                handle_download(audio_only=True)
            elif choice == "7":
                handle_batch_download()
            elif choice == "8":
                handle_show_platforms()
            elif choice == "9":
                handle_reset()
            elif choice == "0":
                print("\n👋 感谢使用，再见！")
                break
            else:
                print("\n❌ 无效选择，请输入 0-9")
            
            input("\n按回车继续...")
            print("\n" * 2)  # 简单分隔
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 程序错误: {e}")
            input("按回车继续...")

if __name__ == "__main__":
    main()
