"""
配置管理模块
管理应用程序的配置信息
"""
import os
import configparser
from utils.logger import logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file="config/settings.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_default_config()
        self._load_config()
    
    def _load_default_config(self):
        """加载默认配置"""
        self.config['DEFAULT'] = {
            'download_path': 'downloads',
            'video_quality': 'best',
            'audio_quality': 'best',
            'max_concurrent_downloads': '3',
            'enable_subtitles': 'False',
            'subtitle_language': 'zh-CN',
            'enable_thumbnail': 'True',
            'enable_metadata': 'True',
            'retry_attempts': '3',
            'timeout': '30'
        }
        
        self.config['GUI'] = {
            'window_width': '800',
            'window_height': '600',
            'theme': 'default',
            'auto_start_download': 'False',
            'show_download_progress': 'True',
            'minimize_to_tray': 'False'
        }
        
        self.config['ADVANCED'] = {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'proxy': '',
            'cookies_file': '',
            'rate_limit': '0',
            'extract_flat': 'False'
        }
    
    def _load_config(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file, encoding='utf-8')
                logger.info(f"配置文件加载成功: {self.config_file}")
            else:
                self._save_config()
                logger.info("创建默认配置文件")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            logger.info("配置文件保存成功")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")

    def save_config(self):
        """公开的保存配置方法"""
        self._save_config()

    def get(self, section, key, fallback=None):
        """获取配置值"""
        try:
            return self.config.get(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    def getint(self, section, key, fallback=0):
        """获取整数配置值"""
        try:
            return self.config.getint(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    def getboolean(self, section, key, fallback=False):
        """获取布尔配置值"""
        try:
            return self.config.getboolean(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    def set(self, section, key, value):
        """设置配置值"""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, key, str(value))
            self._save_config()
        except Exception as e:
            logger.error(f"设置配置失败: {e}")
    
    def get_download_path(self):
        """获取下载路径"""
        path = self.get('DEFAULT', 'download_path', 'downloads')

        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(path):
            path = os.path.abspath(path)

        # 确保目录存在
        if not os.path.exists(path):
            os.makedirs(path)
            logger.info(f"创建下载目录: {path}")

        logger.info(f"使用下载目录: {path}")
        return path
    
    def get_video_quality(self):
        """获取视频质量设置"""
        return self.get('DEFAULT', 'video_quality', 'best')
    
    def get_max_concurrent_downloads(self):
        """获取最大并发下载数"""
        return self.getint('DEFAULT', 'max_concurrent_downloads', 3)
    
    def get_retry_attempts(self):
        """获取重试次数"""
        return self.getint('DEFAULT', 'retry_attempts', 3)


# 创建全局配置管理器实例
config_manager = ConfigManager()
