#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置对话框模块
提供用户配置界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from core.config_manager import config_manager
from utils.logger import logger


class SettingsDialog:
    """设置对话框类"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.settings = {}
        
        # 创建对话框
        self.create_dialog()
        
    def create_dialog(self):
        """创建设置对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("设置")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        
        # 设置对话框图标和属性
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.center_dialog()
        
        # 创建主框架
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选项卡
        self.create_notebook(main_frame)
        
        # 创建按钮区域
        self.create_buttons(main_frame)
        
        # 加载当前设置
        self.load_settings()
        
    def center_dialog(self):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
    def create_notebook(self, parent):
        """创建选项卡"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 基本设置选项卡
        self.create_basic_tab()
        
        # 下载设置选项卡
        self.create_download_tab()
        
        # 格式设置选项卡
        self.create_format_tab()
        
        # 高级设置选项卡
        self.create_advanced_tab()
        
    def create_basic_tab(self):
        """创建基本设置选项卡"""
        basic_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(basic_frame, text="基本设置")
        
        # 下载目录设置
        ttk.Label(basic_frame, text="下载目录:", font=('Microsoft YaHei UI', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(basic_frame)
        dir_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        dir_frame.columnconfigure(0, weight=1)
        
        self.download_path_var = tk.StringVar()
        ttk.Entry(dir_frame, textvariable=self.download_path_var, state='readonly').grid(
            row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="浏览", command=self.browse_download_dir).grid(
            row=0, column=1)
        
        # 最大并发下载数
        ttk.Label(basic_frame, text="最大并发下载数:", font=('Microsoft YaHei UI', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.max_concurrent_var = tk.StringVar()
        concurrent_frame = ttk.Frame(basic_frame)
        concurrent_frame.grid(row=3, column=0, sticky=tk.W, pady=(0, 15))
        
        ttk.Spinbox(concurrent_frame, from_=1, to=10, width=10, 
                   textvariable=self.max_concurrent_var).pack(side=tk.LEFT)
        ttk.Label(concurrent_frame, text="个").pack(side=tk.LEFT, padx=(5, 0))
        
        # 界面设置
        ttk.Label(basic_frame, text="界面设置:", font=('Microsoft YaHei UI', 9, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        self.auto_start_var = tk.BooleanVar()
        ttk.Checkbutton(basic_frame, text="自动开始下载", 
                       variable=self.auto_start_var).grid(row=5, column=0, sticky=tk.W)
        
        self.show_progress_var = tk.BooleanVar()
        ttk.Checkbutton(basic_frame, text="显示下载进度", 
                       variable=self.show_progress_var).grid(row=6, column=0, sticky=tk.W)
        
        basic_frame.columnconfigure(0, weight=1)
        
    def create_download_tab(self):
        """创建下载设置选项卡"""
        download_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(download_frame, text="下载设置")
        
        # 重试设置
        ttk.Label(download_frame, text="重试设置:", font=('Microsoft YaHei UI', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        retry_frame = ttk.Frame(download_frame)
        retry_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 15))
        
        ttk.Label(retry_frame, text="重试次数:").pack(side=tk.LEFT)
        self.retry_attempts_var = tk.StringVar()
        ttk.Spinbox(retry_frame, from_=0, to=10, width=10, 
                   textvariable=self.retry_attempts_var).pack(side=tk.LEFT, padx=(5, 0))
        
        # 超时设置
        timeout_frame = ttk.Frame(download_frame)
        timeout_frame.grid(row=2, column=0, sticky=tk.W, pady=(0, 15))
        
        ttk.Label(timeout_frame, text="超时时间:").pack(side=tk.LEFT)
        self.timeout_var = tk.StringVar()
        ttk.Spinbox(timeout_frame, from_=10, to=300, width=10, 
                   textvariable=self.timeout_var).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(timeout_frame, text="秒").pack(side=tk.LEFT, padx=(5, 0))
        
        # 附加下载选项
        ttk.Label(download_frame, text="附加下载:", font=('Microsoft YaHei UI', 9, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=(15, 5))
        
        self.enable_subtitles_var = tk.BooleanVar()
        ttk.Checkbutton(download_frame, text="下载字幕", 
                       variable=self.enable_subtitles_var).grid(row=4, column=0, sticky=tk.W)
        
        self.enable_thumbnail_var = tk.BooleanVar()
        ttk.Checkbutton(download_frame, text="下载缩略图", 
                       variable=self.enable_thumbnail_var).grid(row=5, column=0, sticky=tk.W)
        
        self.enable_metadata_var = tk.BooleanVar()
        ttk.Checkbutton(download_frame, text="下载元数据", 
                       variable=self.enable_metadata_var).grid(row=6, column=0, sticky=tk.W)
        
        download_frame.columnconfigure(0, weight=1)
        
    def create_format_tab(self):
        """创建格式设置选项卡"""
        format_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(format_frame, text="格式设置")
        
        # 视频质量设置
        ttk.Label(format_frame, text="视频质量:", font=('Microsoft YaHei UI', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.video_quality_var = tk.StringVar()
        quality_frame = ttk.Frame(format_frame)
        quality_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        quality_options = [
            ("最佳质量", "best"),
            ("1080p", "best[height<=1080]"),
            ("720p", "best[height<=720]"),
            ("480p", "best[height<=480]")
        ]
        
        for i, (text, value) in enumerate(quality_options):
            ttk.Radiobutton(quality_frame, text=text, value=value, 
                           variable=self.video_quality_var).grid(row=i//2, column=i%2, 
                                                                sticky=tk.W, padx=(0, 20))
        
        # 格式转换设置
        ttk.Label(format_frame, text="格式转换:", font=('Microsoft YaHei UI', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(15, 5))
        
        self.auto_convert_var = tk.BooleanVar()
        ttk.Checkbutton(format_frame, text="自动将AV1格式转换为H.264", 
                       variable=self.auto_convert_var).grid(row=3, column=0, sticky=tk.W)
        
        # 转换质量设置
        convert_frame = ttk.Frame(format_frame)
        convert_frame.grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        
        ttk.Label(convert_frame, text="转换质量:").pack(side=tk.LEFT)
        self.convert_quality_var = tk.StringVar()
        quality_combo = ttk.Combobox(convert_frame, textvariable=self.convert_quality_var,
                                   values=["高质量 (CRF 18)", "中等质量 (CRF 23)", "低质量 (CRF 28)"],
                                   state="readonly", width=20)
        quality_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        format_frame.columnconfigure(0, weight=1)
        
    def create_advanced_tab(self):
        """创建高级设置选项卡"""
        advanced_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(advanced_frame, text="高级设置")
        
        # 代理设置
        ttk.Label(advanced_frame, text="网络代理:", font=('Microsoft YaHei UI', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        proxy_frame = ttk.Frame(advanced_frame)
        proxy_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        proxy_frame.columnconfigure(1, weight=1)
        
        ttk.Label(proxy_frame, text="代理地址:").grid(row=0, column=0, sticky=tk.W)
        self.proxy_var = tk.StringVar()
        ttk.Entry(proxy_frame, textvariable=self.proxy_var, width=40).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        ttk.Label(proxy_frame, text="格式: http://proxy:port 或 socks5://proxy:port", 
                 foreground="gray").grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        
        # 用户代理设置
        ttk.Label(advanced_frame, text="用户代理:", font=('Microsoft YaHei UI', 9, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=(15, 5))
        
        self.user_agent_var = tk.StringVar()
        ttk.Entry(advanced_frame, textvariable=self.user_agent_var, width=60).grid(
            row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 速度限制
        ttk.Label(advanced_frame, text="下载速度限制:", font=('Microsoft YaHei UI', 9, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        rate_frame = ttk.Frame(advanced_frame)
        rate_frame.grid(row=5, column=0, sticky=tk.W)
        
        self.rate_limit_var = tk.StringVar()
        ttk.Entry(rate_frame, textvariable=self.rate_limit_var, width=15).pack(side=tk.LEFT)
        ttk.Label(rate_frame, text="KB/s (0表示无限制)").pack(side=tk.LEFT, padx=(5, 0))
        
        advanced_frame.columnconfigure(0, weight=1)
        
    def create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="确定", command=self.save_settings).pack(
            side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(
            side=tk.RIGHT)
        ttk.Button(button_frame, text="应用", command=self.apply_settings).pack(
            side=tk.RIGHT, padx=(0, 5))
        ttk.Button(button_frame, text="重置", command=self.reset_settings).pack(
            side=tk.LEFT)
        
    def browse_download_dir(self):
        """浏览下载目录"""
        directory = filedialog.askdirectory(
            title="选择下载目录",
            initialdir=self.download_path_var.get()
        )
        if directory:
            self.download_path_var.set(directory)
            
    def load_settings(self):
        """加载当前设置"""
        try:
            # 基本设置
            self.download_path_var.set(config_manager.get('DEFAULT', 'download_path'))
            self.max_concurrent_var.set(config_manager.get('DEFAULT', 'max_concurrent_downloads'))
            self.auto_start_var.set(config_manager.getboolean('GUI', 'auto_start_download'))
            self.show_progress_var.set(config_manager.getboolean('GUI', 'show_download_progress'))
            
            # 下载设置
            self.retry_attempts_var.set(config_manager.get('DEFAULT', 'retry_attempts'))
            self.timeout_var.set(config_manager.get('DEFAULT', 'timeout'))
            self.enable_subtitles_var.set(config_manager.getboolean('DEFAULT', 'enable_subtitles'))
            self.enable_thumbnail_var.set(config_manager.getboolean('DEFAULT', 'enable_thumbnail'))
            self.enable_metadata_var.set(config_manager.getboolean('DEFAULT', 'enable_metadata'))
            
            # 格式设置
            self.video_quality_var.set(config_manager.get('DEFAULT', 'video_quality'))
            self.auto_convert_var.set(config_manager.getboolean('DEFAULT', 'auto_convert_av1_to_h264'))
            
            # 转换质量映射
            quality_map = {
                "18": "高质量 (CRF 18)",
                "23": "中等质量 (CRF 23)", 
                "28": "低质量 (CRF 28)"
            }
            convert_crf = getattr(config_manager, 'convert_quality_crf', '23')
            self.convert_quality_var.set(quality_map.get(convert_crf, "中等质量 (CRF 23)"))
            
            # 高级设置
            self.proxy_var.set(config_manager.get('ADVANCED', 'proxy'))
            self.user_agent_var.set(config_manager.get('ADVANCED', 'user_agent'))
            self.rate_limit_var.set(config_manager.get('ADVANCED', 'rate_limit'))
            
        except Exception as e:
            logger.error(f"加载设置失败: {e}")
            messagebox.showerror("错误", f"加载设置失败: {e}")
            
    def save_settings(self):
        """保存设置并关闭对话框"""
        if self.apply_settings():
            self.dialog.destroy()
            
    def apply_settings(self):
        """应用设置"""
        try:
            # 验证设置
            if not self.validate_settings():
                return False
                
            # 保存基本设置
            config_manager.set('DEFAULT', 'download_path', self.download_path_var.get())
            config_manager.set('DEFAULT', 'max_concurrent_downloads', self.max_concurrent_var.get())
            config_manager.set('GUI', 'auto_start_download', str(self.auto_start_var.get()))
            config_manager.set('GUI', 'show_download_progress', str(self.show_progress_var.get()))
            
            # 保存下载设置
            config_manager.set('DEFAULT', 'retry_attempts', self.retry_attempts_var.get())
            config_manager.set('DEFAULT', 'timeout', self.timeout_var.get())
            config_manager.set('DEFAULT', 'enable_subtitles', str(self.enable_subtitles_var.get()))
            config_manager.set('DEFAULT', 'enable_thumbnail', str(self.enable_thumbnail_var.get()))
            config_manager.set('DEFAULT', 'enable_metadata', str(self.enable_metadata_var.get()))
            
            # 保存格式设置
            config_manager.set('DEFAULT', 'video_quality', self.video_quality_var.get())
            config_manager.set('DEFAULT', 'auto_convert_av1_to_h264', str(self.auto_convert_var.get()))
            
            # 保存转换质量
            quality_crf_map = {
                "高质量 (CRF 18)": "18",
                "中等质量 (CRF 23)": "23",
                "低质量 (CRF 28)": "28"
            }
            crf_value = quality_crf_map.get(self.convert_quality_var.get(), "23")
            config_manager.set('DEFAULT', 'convert_quality_crf', crf_value)
            
            # 保存高级设置
            config_manager.set('ADVANCED', 'proxy', self.proxy_var.get())
            config_manager.set('ADVANCED', 'user_agent', self.user_agent_var.get())
            config_manager.set('ADVANCED', 'rate_limit', self.rate_limit_var.get())
            
            # 写入配置文件
            config_manager.save_config()
            
            messagebox.showinfo("成功", "设置已保存！\n部分设置需要重启程序后生效。")
            logger.info("用户设置已更新")
            return True
            
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            messagebox.showerror("错误", f"保存设置失败: {e}")
            return False
            
    def validate_settings(self):
        """验证设置"""
        try:
            # 验证下载目录
            download_path = self.download_path_var.get()
            if not download_path:
                messagebox.showerror("错误", "请选择下载目录")
                return False
                
            # 验证并发数
            max_concurrent = int(self.max_concurrent_var.get())
            if max_concurrent < 1 or max_concurrent > 10:
                messagebox.showerror("错误", "最大并发下载数必须在1-10之间")
                return False
                
            # 验证重试次数
            retry_attempts = int(self.retry_attempts_var.get())
            if retry_attempts < 0 or retry_attempts > 10:
                messagebox.showerror("错误", "重试次数必须在0-10之间")
                return False
                
            # 验证超时时间
            timeout = int(self.timeout_var.get())
            if timeout < 10 or timeout > 300:
                messagebox.showerror("错误", "超时时间必须在10-300秒之间")
                return False
                
            # 验证速度限制
            rate_limit = self.rate_limit_var.get()
            if rate_limit and rate_limit != "0":
                try:
                    rate_value = int(rate_limit)
                    if rate_value < 0:
                        messagebox.showerror("错误", "速度限制不能为负数")
                        return False
                except ValueError:
                    messagebox.showerror("错误", "速度限制必须是数字")
                    return False
                    
            return True
            
        except ValueError as e:
            messagebox.showerror("错误", f"设置值无效: {e}")
            return False
            
    def reset_settings(self):
        """重置设置为默认值"""
        if messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？"):
            try:
                # 重置为默认值
                self.download_path_var.set("downloads")
                self.max_concurrent_var.set("3")
                self.auto_start_var.set(False)
                self.show_progress_var.set(True)
                
                self.retry_attempts_var.set("3")
                self.timeout_var.set("30")
                self.enable_subtitles_var.set(False)
                self.enable_thumbnail_var.set(True)
                self.enable_metadata_var.set(True)
                
                self.video_quality_var.set("best")
                self.auto_convert_var.set(True)
                self.convert_quality_var.set("中等质量 (CRF 23)")
                
                self.proxy_var.set("")
                self.user_agent_var.set("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                self.rate_limit_var.set("0")
                
                messagebox.showinfo("成功", "设置已重置为默认值")
                
            except Exception as e:
                logger.error(f"重置设置失败: {e}")
                messagebox.showerror("错误", f"重置设置失败: {e}")
                
    def cancel(self):
        """取消并关闭对话框"""
        self.dialog.destroy()
        
    def show(self):
        """显示对话框"""
        self.dialog.wait_window()
