#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频格式转换工具
将AV1等新格式转换为兼容性更好的H.264格式
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def convert_video_to_h264(input_path, output_path=None, quality='medium'):
    """
    将视频转换为H.264格式
    
    Args:
        input_path: 输入视频文件路径
        output_path: 输出视频文件路径（可选）
        quality: 质量设置 ('high', 'medium', 'low')
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        print(f"错误：输入文件不存在: {input_path}")
        return False
    
    # 如果没有指定输出路径，在原文件名后加_h264
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_h264{input_path.suffix}"
    else:
        output_path = Path(output_path)
    
    # 质量设置
    quality_settings = {
        'high': ['-crf', '18'],      # 高质量
        'medium': ['-crf', '23'],    # 中等质量（推荐）
        'low': ['-crf', '28']        # 低质量，文件更小
    }
    
    crf_setting = quality_settings.get(quality, quality_settings['medium'])
    
    # FFmpeg命令
    cmd = [
        'ffmpeg',
        '-i', str(input_path),
        '-c:v', 'libx264',           # 使用H.264编码器
        '-preset', 'medium',         # 编码速度预设
        *crf_setting,                # 质量设置
        '-c:a', 'aac',               # 音频使用AAC编码
        '-b:a', '128k',              # 音频比特率
        '-movflags', '+faststart',   # 优化网络播放
        '-y',                        # 覆盖输出文件
        str(output_path)
    ]
    
    print(f"开始转换: {input_path.name}")
    print(f"输出文件: {output_path}")
    print(f"质量设置: {quality}")
    print("转换中，请稍候...")
    
    try:
        # 执行转换
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 转换成功！")
            
            # 显示文件大小对比
            original_size = input_path.stat().st_size / (1024 * 1024)
            converted_size = output_path.stat().st_size / (1024 * 1024)
            
            print(f"原文件大小: {original_size:.1f} MB")
            print(f"转换后大小: {converted_size:.1f} MB")
            print(f"大小变化: {((converted_size - original_size) / original_size * 100):+.1f}%")
            
            return True
        else:
            print("❌ 转换失败！")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("❌ 错误：未找到ffmpeg，请确保已安装ffmpeg并添加到PATH")
        return False
    except Exception as e:
        print(f"❌ 转换过程中出错: {e}")
        return False

def batch_convert_directory(directory, quality='medium'):
    """
    批量转换目录中的视频文件
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"错误：目录不存在: {directory}")
        return
    
    # 查找视频文件
    video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv'}
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(directory.rglob(f"*{ext}"))
    
    if not video_files:
        print("未找到视频文件")
        return
    
    print(f"找到 {len(video_files)} 个视频文件")
    
    success_count = 0
    for video_file in video_files:
        print(f"\n处理: {video_file.relative_to(directory)}")
        
        # 检查是否已经是H.264格式
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name', '-of', 'csv=p=0',
                str(video_file)
            ], capture_output=True, text=True)
            
            codec = result.stdout.strip()
            if codec in ['h264', 'avc']:
                print(f"⏭️  跳过（已是H.264格式）")
                continue
                
        except:
            pass  # 如果检查失败，继续转换
        
        if convert_video_to_h264(video_file, quality=quality):
            success_count += 1
    
    print(f"\n✅ 批量转换完成！成功转换 {success_count}/{len(video_files)} 个文件")

def main():
    parser = argparse.ArgumentParser(description='视频格式转换工具')
    parser.add_argument('input', help='输入视频文件或目录路径')
    parser.add_argument('-o', '--output', help='输出文件路径（仅单文件转换时有效）')
    parser.add_argument('-q', '--quality', choices=['high', 'medium', 'low'], 
                       default='medium', help='转换质量 (默认: medium)')
    parser.add_argument('-b', '--batch', action='store_true', 
                       help='批量转换目录中的所有视频文件')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"错误：路径不存在: {input_path}")
        sys.exit(1)
    
    if args.batch or input_path.is_dir():
        batch_convert_directory(input_path, args.quality)
    else:
        convert_video_to_h264(input_path, args.output, args.quality)

if __name__ == '__main__':
    main()
