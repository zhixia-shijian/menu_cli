"""
URL验证工具模块
验证各种视频平台的URL格式
"""
import re
from urllib.parse import urlparse


class URLValidator:
    """URL验证器"""
    
    # 支持的平台URL模式
    PLATFORM_PATTERNS = {
        'youtube': [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/channel/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/@[\w-]+',
        ],
        'twitter': [
            r'(?:https?://)?(?:www\.)?twitter\.com/\w+/status/\d+',
            r'(?:https?://)?(?:www\.)?x\.com/\w+/status/\d+',
            r'(?:https?://)?(?:www\.)?twitter\.com/i/web/status/\d+',
            r'(?:https?://)?(?:www\.)?x\.com/i/web/status/\d+',
            r'(?:https?://)?(?:mobile\.)?twitter\.com/\w+/status/\d+',
            r'(?:https?://)?(?:mobile\.)?x\.com/\w+/status/\d+',
        ],
        'instagram': [
            r'(?:https?://)?(?:www\.)?instagram\.com/p/[\w-]+',
            r'(?:https?://)?(?:www\.)?instagram\.com/reel/[\w-]+',
            r'(?:https?://)?(?:www\.)?instagram\.com/tv/[\w-]+',
        ],
        'tiktok': [
            r'(?:https?://)?(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'(?:https?://)?vm\.tiktok\.com/[\w-]+',
        ],
        'bilibili': [
            r'(?:https?://)?(?:www\.)?bilibili\.com/video/[\w-]+',
            r'(?:https?://)?(?:www\.)?b23\.tv/[\w-]+',
        ]
    }
    
    @classmethod
    def is_valid_url(cls, url):
        """检查URL是否有效"""
        if not url or not isinstance(url, str):
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @classmethod
    def detect_platform(cls, url):
        """检测URL所属平台"""
        if not cls.is_valid_url(url):
            return None
        
        url = url.strip()
        
        for platform, patterns in cls.PLATFORM_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    return platform
        
        return 'unknown'
    
    @classmethod
    def is_supported_platform(cls, url):
        """检查是否为支持的平台"""
        platform = cls.detect_platform(url)
        return platform and platform != 'unknown'
    
    @classmethod
    def normalize_url(cls, url):
        """标准化URL格式"""
        if not url:
            return url
        
        url = url.strip()
        
        # 如果没有协议，添加https
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        return url
    
    @classmethod
    def get_supported_platforms(cls):
        """获取支持的平台列表"""
        return list(cls.PLATFORM_PATTERNS.keys())
    
    @classmethod
    def validate_and_normalize(cls, url):
        """验证并标准化URL"""
        if not url:
            return None, "URL不能为空"
        
        normalized_url = cls.normalize_url(url)
        
        if not cls.is_valid_url(normalized_url):
            return None, "无效的URL格式"
        
        platform = cls.detect_platform(normalized_url)
        if platform == 'unknown':
            return None, f"不支持的平台，支持的平台: {', '.join(cls.get_supported_platforms())}"
        
        return normalized_url, None
