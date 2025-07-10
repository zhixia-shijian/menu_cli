"""
日志工具模块
提供统一的日志记录功能
"""
import logging
import os
from datetime import datetime


class Logger:
    """日志管理器"""
    
    def __init__(self, name="VideoDownloader", log_dir="logs"):
        self.name = name
        self.log_dir = log_dir
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志配置"""
        # 创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 创建logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 创建文件handler
            log_file = os.path.join(
                self.log_dir, 
                f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            # 创建控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 创建formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加handler
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message):
        """调试信息"""
        self.logger.debug(message)
    
    def info(self, message):
        """一般信息"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告信息"""
        self.logger.warning(message)
    
    def error(self, message):
        """错误信息"""
        self.logger.error(message)
    
    def critical(self, message):
        """严重错误"""
        self.logger.critical(message)


# 创建全局logger实例
logger = Logger()
