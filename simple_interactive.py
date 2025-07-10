#!/usr/bin/env python3
"""
简单交互式视频下载器
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_menu():
    """打印菜单"""
    print("🎬" + "=" * 50 + "🎬")
    print("        视频下载器交互式终端版 v2.0.0")
    print("🎬" + "=" * 50 + "🎬")
    print()
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

def show_platforms():
    """显示支持平台"""
    print("🌐 支持的平台:")
    print("   ✅ YouTube (youtube.com, youtu.be)")
    print("   ✅ Twitter/X (twitter.com, x.com)")
    print("   ✅ Instagram (instagram.com)")
    print("   ✅ TikTok (tiktok.com)")
    print("   ✅ Bilibili (bilibili.com, b23.tv)")
    print("📊 总计支持 1700+ 网站")

def main():
    """主函数"""
    current_url = None
    current_quality = "best"
    current_output = "downloads"
    
    while True:
        print_menu()
        
        # 显示当前状态
        print("📊 当前设置:")
        print(f"   URL: {current_url if current_url else '未设置'}")
        print(f"   质量: {current_quality}")
        print(f"   目录: {current_output}")
        print()
        
        try:
            choice = input("请输入选择 (0-9): ").strip()
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
            
        print()
        
        if choice == "1":
            print("🔗 设置视频URL")
            url = input("请输入视频URL: ").strip()
            if url:
                current_url = url
                print(f"✅ URL已设置: {url}")
            else:
                print("❌ URL不能为空")
                
        elif choice == "2":
            print("📁 设置下载目录")
            print(f"当前目录: {current_output}")
            new_dir = input("请输入新目录 (回车保持当前): ").strip()
            if new_dir:
                current_output = new_dir
                print(f"✅ 下载目录已设置为: {new_dir}")
            else:
                print("📁 保持当前目录")
                
        elif choice == "3":
            print("🎯 设置视频质量")
            print("可选质量:")
            qualities = ["best", "1080p", "720p", "480p", "worst"]
            for i, quality in enumerate(qualities, 1):
                marker = "👉" if quality == current_quality else "  "
                print(f"   {i}. {quality} {marker}")
            
            try:
                q_choice = input("请选择质量 (1-5): ").strip()
                index = int(q_choice) - 1
                if 0 <= index < len(qualities):
                    current_quality = qualities[index]
                    print(f"✅ 视频质量已设置为: {current_quality}")
                else:
                    print("❌ 无效选择")
            except ValueError:
                print("❌ 请输入数字")
                
        elif choice == "4":
            if not current_url:
                print("❌ 请先设置视频URL (选项1)")
            else:
                print("📋 获取视频信息功能")
                print(f"URL: {current_url}")
                print("💡 此功能需要完整版本支持")
                
        elif choice == "5":
            if not current_url:
                print("❌ 请先设置视频URL (选项1)")
            else:
                print("⬇️ 下载视频功能")
                print(f"URL: {current_url}")
                print(f"质量: {current_quality}")
                print(f"目录: {current_output}")
                print("💡 此功能需要完整版本支持")
                
        elif choice == "6":
            if not current_url:
                print("❌ 请先设置视频URL (选项1)")
            else:
                print("🎵 下载音频功能")
                print(f"URL: {current_url}")
                print(f"目录: {current_output}")
                print("💡 此功能需要完整版本支持")
                
        elif choice == "7":
            print("📦 批量下载功能")
            file_path = input("请输入URL列表文件路径: ").strip()
            if file_path:
                print(f"📁 文件路径: {file_path}")
                print("💡 此功能需要完整版本支持")
            else:
                print("❌ 文件路径不能为空")
                
        elif choice == "8":
            show_platforms()
            
        elif choice == "9":
            print("⚙️ 设置选项")
            print("1. 重置为默认设置")
            print("2. 查看当前配置")
            
            setting_choice = input("请选择 (1-2): ").strip()
            if setting_choice == "1":
                current_quality = "best"
                current_output = "downloads"
                current_url = None
                print("✅ 已重置为默认设置")
            elif setting_choice == "2":
                print("📋 当前配置:")
                print(f"   默认质量: {current_quality}")
                print(f"   默认目录: {current_output}")
                print(f"   当前URL: {current_url if current_url else '未设置'}")
            else:
                print("❌ 无效选择")
                
        elif choice == "0":
            print("👋 感谢使用，再见！")
            break
            
        else:
            print("❌ 无效选择，请输入 0-9")
            
        print()
        input("按回车继续...")
        print("\n" * 3)  # 简单清屏

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 再见！")
    except Exception as e:
        print(f"❌ 程序错误: {e}")
