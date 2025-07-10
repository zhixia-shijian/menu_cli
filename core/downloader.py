"""
视频下载器核心模块
使用yt-dlp实现多平台视频下载功能
"""
import os
import threading
import time
import subprocess
from datetime import datetime
from typing import Callable, Dict, Any, Optional
from pathlib import Path

import yt_dlp
from utils.logger import logger
from utils.validators import URLValidator
from core.config_manager import config_manager


class DownloadProgress:
    """下载进度信息"""
    
    def __init__(self):
        self.url = ""
        self.title = ""
        self.status = "waiting"  # waiting, downloading, completed, error, cancelled
        self.progress = 0.0
        self.speed = ""
        self.eta = ""
        self.file_size = ""
        self.downloaded_bytes = 0
        self.total_bytes = 0
        self.error_message = ""
        self.start_time = None
        self.end_time = None


class VideoDownloader:
    """视频下载器"""

    def __init__(self):
        self.downloads = {}  # 存储下载任务
        self.download_lock = threading.Lock()
        self.active_downloads = 0
        self.max_concurrent = config_manager.get_max_concurrent_downloads()
        self.ffmpeg_available = self._check_ffmpeg()

    def _check_ffmpeg(self) -> bool:
        """检查ffmpeg是否可用"""
        # 检查系统ffmpeg二进制文件（yt-dlp需要的是二进制文件，不是Python包）
        try:
            result = subprocess.run(['ffmpeg', '-version'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("检测到系统ffmpeg，支持高质量视频合并")
                return True
            else:
                logger.warning("系统ffmpeg检测失败")
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            logger.info("系统ffmpeg未安装或不在PATH中")

        # 检查是否有python-ffmpeg包（仅用于提示）
        try:
            import ffmpeg
            logger.warning("检测到python-ffmpeg包，但yt-dlp需要系统级ffmpeg二进制文件")
            logger.info("建议安装: pip install ffmpeg-python 或下载ffmpeg二进制文件")
        except ImportError:
            logger.info("建议安装ffmpeg以获得更好的下载质量")

        logger.warning("ffmpeg不可用，将使用兼容模式")
        return False

    def _get_ffmpeg_location(self) -> str:
        """获取ffmpeg的位置"""
        try:
            # 尝试从python-ffmpeg获取路径
            import ffmpeg
            # python-ffmpeg通常会在包内包含ffmpeg二进制文件
            import pkg_resources
            try:
                ffmpeg_path = pkg_resources.resource_filename('ffmpeg', 'bin/ffmpeg.exe')
                if os.path.exists(ffmpeg_path):
                    logger.info(f"使用python-ffmpeg路径: {ffmpeg_path}")
                    return ffmpeg_path
            except:
                pass
        except ImportError:
            pass

        # 如果python-ffmpeg方法失败，返回None让yt-dlp自动查找
        return None

    def _find_downloaded_file_in_folder(self, output_path: str, title: str):
        """在分类文件夹结构中查找下载的文件"""
        try:
            # 使用完整标题作为主文件夹名
            expected_main_folder = os.path.join(output_path, title)

            # 检查预期的主文件夹是否存在
            if os.path.exists(expected_main_folder):
                # 查找video子文件夹中的视频文件
                video_folder = os.path.join(expected_main_folder, 'video')
                if os.path.exists(video_folder):
                    video_files = [f for f in os.listdir(video_folder)
                                 if f.endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm'))]
                    if video_files:
                        video_file = video_files[0]
                        full_path = os.path.join(video_folder, video_file)
                        logger.info(f"找到视频文件: {full_path}")

                        # 记录其他文件的位置
                        self._log_additional_files(expected_main_folder)
                        return full_path

            # 如果预期文件夹不存在，查找相似的文件夹
            if os.path.exists(output_path):
                folders = [f for f in os.listdir(output_path) if os.path.isdir(os.path.join(output_path, f))]
                title_keywords = title.replace(' ', '').lower()[:20]

                for folder in folders:
                    if title_keywords in folder.replace(' ', '').lower():
                        main_folder_path = os.path.join(output_path, folder)
                        video_folder = os.path.join(main_folder_path, 'video')

                        if os.path.exists(video_folder):
                            video_files = [f for f in os.listdir(video_folder)
                                         if f.endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm'))]
                            if video_files:
                                video_file = video_files[0]
                                full_path = os.path.join(video_folder, video_file)
                                logger.info(f"找到可能的视频文件: {full_path}")
                                return full_path

        except Exception as e:
            logger.error(f"查找下载文件时出错: {e}")

        return None

    def _log_additional_files(self, main_folder: str):
        """记录下载的附加文件"""
        try:
            subfolders = ['thumbnails', 'metadata', 'subtitles']
            for subfolder in subfolders:
                subfolder_path = os.path.join(main_folder, subfolder)
                if os.path.exists(subfolder_path):
                    files = os.listdir(subfolder_path)
                    if files:
                        logger.info(f"{subfolder}文件夹包含: {', '.join(files)}")
        except Exception as e:
            logger.error(f"记录附加文件时出错: {e}")

    def _clean_filename(self, filename: str) -> str:
        """清理文件名，移除不安全字符"""
        import re
        # 移除或替换不安全的字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', ' ', filename).strip()
        return filename
        
    def _get_ydl_opts(self, output_path: str, progress_callback: Callable = None, url: str = None) -> Dict[str, Any]:
        """获取yt-dlp配置选项"""
        # 改进的格式选择策略，针对不同平台优化
        video_quality = config_manager.get_video_quality()

        # 智能格式选择：优先H.264，如果没有则下载其他格式并自动转换
        if url and 'bilibili.com' in url:
            if self.ffmpeg_available:
                # B站 + ffmpeg：优先H.264，备选其他格式
                format_selector = 'bestvideo[vcodec^=avc][height<=1080]+bestaudio[acodec=aac]/bestvideo[vcodec^=avc][height<=720]+bestaudio[acodec=aac]/bestvideo[vcodec^=avc]+bestaudio/bestvideo[height<=1080]+bestaudio/best'
                logger.info("B站链接：优先H.264编码，如无则下载其他格式并自动转换")
            else:
                # B站无ffmpeg：优先H.264单一格式，备选其他
                format_selector = 'best[vcodec^=avc][height<=720]/best[vcodec^=avc]/best[height<=720]/best'
                logger.info("B站链接：ffmpeg不可用，优先H.264，备选其他格式")
        elif url and ('twitter.com' in url or 'x.com' in url):
            if self.ffmpeg_available:
                # Twitter/X + ffmpeg：优先最高质量，自动转换为H.264
                format_selector = 'best[height<=1080]/best[height<=720]/best'
                logger.info("Twitter/X链接：下载最高质量视频，自动转换为H.264")
            else:
                # Twitter/X无ffmpeg：选择兼容格式
                format_selector = 'best[vcodec^=avc]/best[height<=720]/best'
                logger.info("Twitter/X链接：ffmpeg不可用，优先兼容格式")
        else:
            if self.ffmpeg_available:
                # 其他平台 + ffmpeg：优先H.264，备选其他
                format_selector = 'bestvideo[vcodec^=avc]+bestaudio[acodec=aac]/bestvideo[vcodec^=avc]+bestaudio/bestvideo+bestaudio/best'
                logger.info("优先H.264编码，如无则下载其他格式并自动转换")
            else:
                # 其他平台无ffmpeg：优先H.264，备选其他
                format_selector = 'best[vcodec^=avc]/best'
                logger.info("ffmpeg不可用，优先H.264，备选其他格式")

        # 创建分类文件夹结构的模板
        # 主文件夹：downloads/视频标题/
        # 视频文件：downloads/视频标题/video/视频标题.ext
        base_folder = os.path.join(output_path, '%(title)s')

        opts = {
            'outtmpl': {
                'default': os.path.join(base_folder, 'video', '%(title)s.%(ext)s'),
                'thumbnail': os.path.join(base_folder, 'thumbnails', '%(title)s.%(ext)s'),
                'description': os.path.join(base_folder, 'metadata', '%(title)s.%(ext)s'),
                'annotation': os.path.join(base_folder, 'metadata', '%(title)s.%(ext)s'),
                'subtitle': os.path.join(base_folder, 'subtitles', '%(title)s.%(ext)s'),
                'infojson': os.path.join(base_folder, 'metadata', '%(title)s.info.json'),
            },
            'format': format_selector,
            # 文件名清理选项 - 保留完整标题但确保Windows兼容
            'restrictfilenames': False,  # 不限制文件名字符，保留完整标题
            'windowsfilenames': True,   # Windows兼容文件名
            'trim_filenames': 255,      # 文件名最大长度（Windows限制）
            'writesubtitles': config_manager.getboolean('DEFAULT', 'enable_subtitles'),
            'writeautomaticsub': config_manager.getboolean('DEFAULT', 'enable_subtitles'),
            'subtitleslangs': [config_manager.get('DEFAULT', 'subtitle_language', 'zh-CN')],
            'writethumbnail': config_manager.getboolean('DEFAULT', 'enable_thumbnail'),
            'writeinfojson': config_manager.getboolean('DEFAULT', 'enable_metadata'),
            'ignoreerrors': False,
            'no_warnings': False,
            'extractaudio': False,
            'audioformat': 'mp3',
            'audioquality': config_manager.get('DEFAULT', 'audio_quality', 'best'),
            # 根据ffmpeg可用性配置
            'prefer_ffmpeg': self.ffmpeg_available,
            # 添加更多调试信息
            'verbose': True,
        }

        # 如果ffmpeg可用，添加高级功能
        if self.ffmpeg_available:
            ffmpeg_opts = {
                'merge_output_format': 'mp4',  # 合并后的输出格式
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }

            # 尝试指定ffmpeg路径（对python-ffmpeg有帮助）
            ffmpeg_location = self._get_ffmpeg_location()
            if ffmpeg_location:
                ffmpeg_opts['ffmpeg_location'] = ffmpeg_location

            opts.update(ffmpeg_opts)
        else:
            # ffmpeg不可用时的兼容设置
            opts.update({
                'abort_on_error': False,  # 不因为ffmpeg缺失而中止
            })
        
        # 添加用户代理
        user_agent = config_manager.get('ADVANCED', 'user_agent')
        if user_agent:
            opts['http_headers'] = {'User-Agent': user_agent}
        
        # 添加代理设置
        proxy = config_manager.get('ADVANCED', 'proxy')
        if proxy:
            opts['proxy'] = proxy
        
        # 添加进度回调
        if progress_callback:
            opts['progress_hooks'] = [progress_callback]
        
        return opts
    
    def _progress_hook(self, download_id: str, d: Dict[str, Any]):
        """下载进度回调函数"""
        if download_id not in self.downloads:
            return
        
        progress = self.downloads[download_id]
        
        if d['status'] == 'downloading':
            progress.status = 'downloading'
            
            # 更新进度信息
            if 'total_bytes' in d and d['total_bytes']:
                progress.total_bytes = d['total_bytes']
                progress.downloaded_bytes = d.get('downloaded_bytes', 0)
                progress.progress = (progress.downloaded_bytes / progress.total_bytes) * 100
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                progress.total_bytes = d['total_bytes_estimate']
                progress.downloaded_bytes = d.get('downloaded_bytes', 0)
                progress.progress = (progress.downloaded_bytes / progress.total_bytes) * 100
            
            # 更新速度和预计时间
            progress.speed = d.get('_speed_str', '')
            progress.eta = d.get('_eta_str', '')
            
            # 格式化文件大小
            if progress.total_bytes > 0:
                progress.file_size = self._format_bytes(progress.total_bytes)
        
        elif d['status'] == 'finished':
            progress.status = 'completed'
            progress.progress = 100.0
            progress.end_time = datetime.now()
            logger.info(f"下载完成: {progress.title}")
        
        elif d['status'] == 'error':
            progress.status = 'error'
            progress.error_message = str(d.get('error', '未知错误'))
            progress.end_time = datetime.now()
            logger.error(f"下载失败: {progress.title} - {progress.error_message}")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """格式化字节数为可读格式"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """获取视频信息"""
        try:
            # 验证URL
            normalized_url, error = URLValidator.validate_and_normalize(url)
            if error:
                logger.error(f"URL验证失败: {error}")
                return None

            # 配置yt-dlp选项
            opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'ignoreerrors': True,  # 忽略某些错误，继续获取可用信息
            }

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(normalized_url, download=False)

                if not info:
                    logger.warning("无法获取视频信息")
                    return None

                # 安全地获取各种信息，处理可能的None值
                return {
                    'title': info.get('title', '未知标题'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', '未知上传者'),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': info.get('formats', []),
                    'url': normalized_url
                }

        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return None
    
    def start_download(self, url: str, output_path: str = None, 
                      progress_callback: Callable = None) -> str:
        """开始下载视频"""
        # 生成下载ID
        download_id = f"download_{int(time.time() * 1000)}"
        
        # 验证URL
        normalized_url, error = URLValidator.validate_and_normalize(url)
        if error:
            logger.error(f"URL验证失败: {error}")
            return None
        
        # 设置输出路径
        if not output_path:
            output_path = config_manager.get_download_path()
        
        # 创建下载进度对象
        progress = DownloadProgress()
        progress.url = normalized_url
        progress.start_time = datetime.now()
        
        with self.download_lock:
            self.downloads[download_id] = progress
        
        # 检查并发下载限制
        if self.active_downloads >= self.max_concurrent:
            progress.status = 'waiting'
            logger.info(f"下载任务排队中: {download_id}")
        
        # 启动下载线程
        download_thread = threading.Thread(
            target=self._download_worker,
            args=(download_id, normalized_url, output_path, progress_callback)
        )
        download_thread.daemon = True
        download_thread.start()
        
        return download_id

    def _download_worker(self, download_id: str, url: str, output_path: str,
                        progress_callback: Callable = None):
        """下载工作线程"""
        try:
            # 等待下载槽位
            while self.active_downloads >= self.max_concurrent:
                time.sleep(1)

            with self.download_lock:
                self.active_downloads += 1
                progress = self.downloads[download_id]
                progress.status = 'downloading'

            # 创建进度回调包装器
            def wrapped_progress_hook(d):
                self._progress_hook(download_id, d)
                if progress_callback:
                    progress_callback(download_id, progress)

            # 配置yt-dlp选项
            opts = self._get_ydl_opts(output_path, wrapped_progress_hook, url)

            # 开始下载
            with yt_dlp.YoutubeDL(opts) as ydl:
                logger.info(f"开始下载视频: {url}")
                logger.info(f"下载目录: {output_path}")
                logger.info(f"使用格式选择器: {opts['format']}")

                # 先尝试获取可用格式信息（调试用）
                try:
                    info_only = ydl.extract_info(url, download=False)
                    if info_only and 'formats' in info_only:
                        available_formats = [f"id:{f.get('format_id', 'unknown')} res:{f.get('height', 'unknown')}p ext:{f.get('ext', 'unknown')}"
                                           for f in info_only['formats'][:5]]  # 只显示前5个
                        logger.info(f"可用格式示例: {', '.join(available_formats)}")
                except Exception as format_error:
                    logger.warning(f"无法获取格式信息: {format_error}")

                # 直接下载，让yt-dlp在下载过程中获取信息
                try:
                    # 使用下载模式，这样可以同时获取信息和下载文件
                    info = ydl.extract_info(url, download=True)

                    if info:
                        progress.title = info.get('title', '未知标题')
                        logger.info(f"下载完成: {progress.title}")

                        # 检查文件是否真的存在
                        expected_filename = ydl.prepare_filename(info)
                        if os.path.exists(expected_filename):
                            logger.info(f"文件保存成功: {expected_filename}")
                            # 验证文件夹结构
                            video_folder = os.path.dirname(expected_filename)
                            logger.info(f"视频保存在文件夹: {video_folder}")
                        else:
                            # 尝试查找可能的文件
                            self._find_downloaded_file_in_folder(output_path, info.get('title', '未知标题'))
                    else:
                        progress.title = '未知标题'
                        logger.warning("下载完成但无法获取视频信息")

                    # 下载成功，检查是否需要转换格式
                    if progress.status != 'error':
                        # 检查并转换AV1格式到H.264
                        converted_file = self._convert_av1_to_h264_if_needed(expected_filename, info)
                        if converted_file:
                            logger.info(f"视频已自动转换为H.264格式: {converted_file}")

                        progress.status = 'completed'
                        progress.progress = 100.0
                        progress.end_time = datetime.now()

                except Exception as download_error:
                    logger.error(f"下载过程中出错: {download_error}")
                    raise download_error

        except Exception as e:
            with self.download_lock:
                progress = self.downloads[download_id]
                progress.status = 'error'
                progress.error_message = str(e)
                progress.end_time = datetime.now()
            logger.error(f"下载失败: {e}")

        finally:
            with self.download_lock:
                self.active_downloads -= 1

    def cancel_download(self, download_id: str) -> bool:
        """取消下载"""
        try:
            if download_id in self.downloads:
                progress = self.downloads[download_id]
                if progress.status in ['waiting', 'downloading']:
                    progress.status = 'cancelled'
                    progress.end_time = datetime.now()
                    logger.info(f"下载已取消: {download_id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"取消下载失败: {e}")
            return False

    def get_download_progress(self, download_id: str) -> Optional[DownloadProgress]:
        """获取下载进度"""
        return self.downloads.get(download_id)

    def get_all_downloads(self) -> Dict[str, DownloadProgress]:
        """获取所有下载任务"""
        return self.downloads.copy()

    def clear_completed_downloads(self):
        """清除已完成的下载任务"""
        with self.download_lock:
            completed_ids = [
                download_id for download_id, progress in self.downloads.items()
                if progress.status in ['completed', 'error', 'cancelled']
            ]
            for download_id in completed_ids:
                del self.downloads[download_id]
            logger.info(f"清除了 {len(completed_ids)} 个已完成的下载任务")

    def get_download_statistics(self) -> Dict[str, int]:
        """获取下载统计信息"""
        stats = {
            'total': len(self.downloads),
            'waiting': 0,
            'downloading': 0,
            'completed': 0,
            'error': 0,
            'cancelled': 0
        }

        for progress in self.downloads.values():
            if progress.status in stats:
                stats[progress.status] += 1

        return stats

    def _convert_av1_to_h264_if_needed(self, video_file_path: str, video_info: dict) -> str:
        """
        检查视频是否为AV1格式，如果是则自动转换为H.264格式

        Args:
            video_file_path: 视频文件路径
            video_info: 视频信息字典

        Returns:
            转换后的文件路径，如果不需要转换则返回None
        """
        try:
            # 检查是否启用自动转换
            if not config_manager.getboolean('DEFAULT', 'auto_convert_av1_to_h264'):
                logger.info("自动AV1转H.264功能已禁用")
                return None
            if not os.path.exists(video_file_path):
                logger.warning(f"视频文件不存在，无法检查格式: {video_file_path}")
                return None

            # 检查视频编码格式
            import subprocess

            # 使用ffprobe检查视频编码
            cmd = [
                'ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_name', '-of', 'csv=p=0',
                video_file_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

            if result.returncode != 0:
                logger.warning(f"无法检查视频编码格式: {video_file_path}")
                return None

            codec = result.stdout.strip().lower()
            logger.info(f"检测到视频编码格式: {codec}")

            # 如果不是AV1格式，不需要转换
            if codec != 'av1':
                logger.info(f"视频已是兼容格式({codec})，无需转换")
                return None

            logger.info(f"检测到AV1格式，开始自动转换为H.264...")

            # 生成输出文件路径
            video_path = Path(video_file_path)
            output_path = video_path.parent / f"{video_path.stem}_h264{video_path.suffix}"

            # FFmpeg转换命令
            convert_cmd = [
                'ffmpeg',
                '-i', video_file_path,
                '-c:v', 'libx264',           # 使用H.264编码器
                '-preset', 'medium',         # 编码速度预设
                '-crf', '23',                # 质量设置（中等质量）
                '-c:a', 'aac',               # 音频使用AAC编码
                '-b:a', '128k',              # 音频比特率
                '-movflags', '+faststart',   # 优化网络播放
                '-y',                        # 覆盖输出文件
                str(output_path)
            ]

            logger.info(f"开始转换: {video_path.name} -> {output_path.name}")

            # 执行转换
            convert_result = subprocess.run(
                convert_cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            if convert_result.returncode == 0:
                logger.info(f"✅ AV1转H.264转换成功: {output_path}")

                # 显示文件大小对比
                original_size = os.path.getsize(video_file_path) / (1024 * 1024)
                converted_size = os.path.getsize(output_path) / (1024 * 1024)

                logger.info(f"原文件大小: {original_size:.1f} MB")
                logger.info(f"转换后大小: {converted_size:.1f} MB")

                # 删除原始AV1文件，保留H.264版本
                try:
                    os.remove(video_file_path)
                    logger.info(f"已删除原始AV1文件: {video_path.name}")

                    # 重命名转换后的文件，去掉_h264后缀
                    final_path = video_path
                    os.rename(output_path, final_path)
                    logger.info(f"已重命名为原文件名: {final_path.name}")

                    return str(final_path)

                except Exception as e:
                    logger.warning(f"文件操作失败: {e}")
                    return str(output_path)

            else:
                logger.error(f"❌ AV1转H.264转换失败")
                logger.error(f"错误信息: {convert_result.stderr}")
                return None

        except FileNotFoundError:
            logger.warning("ffmpeg或ffprobe未安装，无法进行格式转换")
            return None
        except Exception as e:
            logger.error(f"格式转换过程中出错: {e}")
            return None
