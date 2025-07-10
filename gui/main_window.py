"""
主窗口GUI模块
提供用户友好的视频下载界面
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from datetime import datetime

from core.downloader import VideoDownloader
from core.config_manager import config_manager
from utils.logger import logger
from utils.validators import URLValidator


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.downloader = VideoDownloader()
        self.download_items = {}  # 存储下载项目的GUI元素
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()
        
        # 启动进度更新线程
        self.update_thread = threading.Thread(target=self.update_progress_loop, daemon=True)
        self.update_thread.start()
    
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("视频下载器 - 支持YouTube、Twitter/X等平台")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap("icon.ico")  # 可选：添加图标
            pass
        except:
            pass
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)  # 下载列表区域
        main_frame.rowconfigure(4, weight=2)  # 视频信息区域 - 增加权重
        
        # URL输入区域
        self.create_url_input_section(main_frame)
        
        # 控制按钮区域
        self.create_control_section(main_frame)
        
        # 下载列表区域
        self.create_download_list_section(main_frame)

        # 视频信息区域
        self.create_video_info_section(main_frame)

        # 状态栏
        self.create_status_bar(main_frame)
    
    def create_url_input_section(self, parent):
        """创建URL输入区域"""
        # URL输入标签
        url_label = ttk.Label(parent, text="视频链接:")
        url_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # URL输入框
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(parent, textvariable=self.url_var, font=('Arial', 10))
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        
        # 粘贴按钮
        paste_btn = ttk.Button(parent, text="粘贴", command=self.paste_url, width=8)
        paste_btn.grid(row=0, column=2, padx=(5, 0), pady=(0, 5))
        
        # 支持的平台提示
        platforms_text = f"支持平台: {', '.join(URLValidator.get_supported_platforms())}"
        platforms_label = ttk.Label(parent, text=platforms_text, font=('Arial', 8), foreground='gray')
        platforms_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 10))
    
    def create_control_section(self, parent):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 下载按钮
        self.download_btn = ttk.Button(
            control_frame, text="开始下载", command=self.start_download,
            style='Accent.TButton'
        )
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 获取信息按钮
        info_btn = ttk.Button(control_frame, text="获取视频信息", command=self.get_video_info)
        info_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 选择下载目录按钮
        folder_btn = ttk.Button(control_frame, text="选择下载目录", command=self.select_download_folder)
        folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清除已完成按钮
        clear_btn = ttk.Button(control_frame, text="清除已完成", command=self.clear_completed)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 设置按钮
        settings_btn = ttk.Button(control_frame, text="设置", command=self.open_settings)
        settings_btn.pack(side=tk.RIGHT)
        
        # 当前下载目录显示
        self.folder_var = tk.StringVar(value=f"下载目录: {config_manager.get_download_path()}")
        folder_label = ttk.Label(control_frame, textvariable=self.folder_var, font=('Arial', 8))
        folder_label.pack(side=tk.RIGHT, padx=(0, 10))
    
    def create_download_list_section(self, parent):
        """创建下载列表区域"""
        # 下载列表标签 - 使用更大的字体和图标
        list_label = ttk.Label(parent, text="📥 下载列表", font=('Microsoft YaHei UI', 10, 'bold'))
        list_label.grid(row=3, column=0, sticky=(tk.W, tk.N), pady=(0, 5))

        # 创建下载列表容器框架
        list_frame = ttk.LabelFrame(parent, text="", padding="5")
        list_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # 创建Treeview用于显示下载列表
        columns = ('标题', '状态', '进度', '速度', '大小', '时间')
        self.download_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)

        # 设置列标题和宽度 - 优化列宽分配，确保内容完整显示
        column_configs = {
            '标题': {'width': 400, 'minwidth': 250, 'anchor': 'w'},
            '状态': {'width': 100, 'minwidth': 80, 'anchor': 'center'},
            '进度': {'width': 150, 'minwidth': 120, 'anchor': 'center'},
            '速度': {'width': 120, 'minwidth': 90, 'anchor': 'center'},
            '大小': {'width': 120, 'minwidth': 90, 'anchor': 'center'},
            '时间': {'width': 150, 'minwidth': 130, 'anchor': 'center'}
        }

        for col in columns:
            config = column_configs[col]
            self.download_tree.heading(col, text=col, anchor='center')
            self.download_tree.column(col,
                                    width=config['width'],
                                    minwidth=config['minwidth'],
                                    anchor=config['anchor'])

        # 添加垂直滚动条
        v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.download_tree.yview)
        self.download_tree.configure(yscrollcommand=v_scrollbar.set)

        # 添加水平滚动条
        h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.download_tree.xview)
        self.download_tree.configure(xscrollcommand=h_scrollbar.set)

        # 放置组件
        self.download_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 配置框架的行列权重
        list_frame.rowconfigure(1, weight=0)  # 水平滚动条行不扩展

        # 配置样式
        self.configure_tree_style()

        # 右键菜单
        self.create_context_menu()

    def configure_tree_style(self):
        """配置Treeview样式"""
        style = ttk.Style()

        # 配置Treeview样式
        style.configure("Treeview",
                       background="#FFFFFF",
                       foreground="#333333",
                       rowheight=18,  # 进一步降低行高，更紧凑
                       fieldbackground="#FFFFFF",
                       font=('Microsoft YaHei UI', 9))

        # 配置Treeview标题样式
        style.configure("Treeview.Heading",
                       background="#F0F0F0",
                       foreground="#333333",
                       font=('Microsoft YaHei UI', 9, 'bold'),
                       relief="flat",
                       borderwidth=1)

        # 配置选中行样式
        style.map("Treeview",
                 background=[('selected', '#0078D4')],
                 foreground=[('selected', 'white')])

        # 配置标题悬停效果
        style.map("Treeview.Heading",
                 background=[('active', '#E1E1E1')])

        # 绑定行交替颜色
        self.download_tree.tag_configure('oddrow', background='#F8F9FA')
        self.download_tree.tag_configure('evenrow', background='#FFFFFF')

        # 状态颜色配置
        self.download_tree.tag_configure('downloading', foreground='#0078D4', font=('Microsoft YaHei UI', 9, 'bold'))
        self.download_tree.tag_configure('completed', foreground='#107C10', font=('Microsoft YaHei UI', 9, 'bold'))
        self.download_tree.tag_configure('error', foreground='#D13438', font=('Microsoft YaHei UI', 9, 'bold'))
        self.download_tree.tag_configure('paused', foreground='#FF8C00', font=('Microsoft YaHei UI', 9, 'bold'))

    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="取消下载", command=self.cancel_selected_download)
        self.context_menu.add_command(label="重新下载", command=self.retry_selected_download)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="打开文件夹", command=self.open_download_folder)
        self.context_menu.add_command(label="复制链接", command=self.copy_selected_url)
        
        # 绑定右键事件
        self.download_tree.bind("<Button-3>", self.show_context_menu)

    def create_video_info_section(self, parent):
        """创建视频信息显示区域"""
        # 视频信息标签 - 使用图标和更大字体
        info_label = ttk.Label(parent, text="📺 视频信息", font=('Microsoft YaHei UI', 10, 'bold'))
        info_label.grid(row=4, column=0, sticky=(tk.W, tk.N), pady=(10, 5))

        # 创建主信息框架
        main_info_frame = ttk.LabelFrame(parent, text="", padding="10")
        main_info_frame.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 5))
        main_info_frame.columnconfigure(0, weight=1)
        main_info_frame.rowconfigure(1, weight=1)

        # 创建顶部信息卡片区域
        self.create_info_cards(main_info_frame)

        # 创建详细信息区域
        self.create_detailed_info_area(main_info_frame)

        # 初始化显示
        self.reset_video_info_display()

    def create_info_cards(self, parent):
        """创建信息卡片区域"""
        cards_frame = ttk.Frame(parent)
        cards_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        cards_frame.columnconfigure((0, 1, 2, 3), weight=1)

        # 标题卡片
        self.title_frame = ttk.LabelFrame(cards_frame, text="📝 标题", padding="5")
        self.title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.title_label = ttk.Label(self.title_frame, text="暂无信息",
                                   font=('Microsoft YaHei UI', 9))
        self.title_label.pack(fill=tk.BOTH, expand=True)

        # 时长卡片
        self.duration_frame = ttk.LabelFrame(cards_frame, text="⏱️ 时长", padding="5")
        self.duration_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.duration_label = ttk.Label(self.duration_frame, text="--:--",
                                      font=('Microsoft YaHei UI', 9, 'bold'))
        self.duration_label.pack(fill=tk.BOTH, expand=True)

        # 观看次数卡片
        self.views_frame = ttk.LabelFrame(cards_frame, text="👁️ 观看", padding="5")
        self.views_frame.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(0, 5))
        self.views_label = ttk.Label(self.views_frame, text="-- 次",
                                   font=('Microsoft YaHei UI', 9, 'bold'))
        self.views_label.pack(fill=tk.BOTH, expand=True)

        # 上传日期卡片
        self.date_frame = ttk.LabelFrame(cards_frame, text="📅 日期", padding="5")
        self.date_frame.grid(row=0, column=3, sticky=(tk.W, tk.E))
        self.date_label = ttk.Label(self.date_frame, text="----/--/--",
                                  font=('Microsoft YaHei UI', 9))
        self.date_label.pack(fill=tk.BOTH, expand=True)

    def create_detailed_info_area(self, parent):
        """创建详细信息区域"""
        # 详细信息框架
        detail_frame = ttk.LabelFrame(parent, text="📋 详细信息", padding="5")
        detail_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)

        # 创建带样式的文本框
        self.info_text = scrolledtext.ScrolledText(
            detail_frame,
            wrap=tk.WORD,
            font=('Microsoft YaHei UI', 9),
            height=10,  # 增加高度，显示更多内容
            state=tk.DISABLED,
            bg='#FAFAFA',
            fg='#333333',
            selectbackground='#0078D4',
            selectforeground='white'
        )
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置文本样式
        self.configure_text_styles()

    def configure_text_styles(self):
        """配置文本样式"""
        self.info_text.tag_configure('header', font=('Microsoft YaHei UI', 10, 'bold'), foreground='#0078D4')
        self.info_text.tag_configure('label', font=('Microsoft YaHei UI', 9, 'bold'), foreground='#666666')
        self.info_text.tag_configure('value', font=('Microsoft YaHei UI', 9), foreground='#333333')
        self.info_text.tag_configure('url', font=('Microsoft YaHei UI', 9), foreground='#0078D4', underline=True)
        self.info_text.tag_configure('success', font=('Microsoft YaHei UI', 9), foreground='#107C10')
        self.info_text.tag_configure('warning', font=('Microsoft YaHei UI', 9), foreground='#FF8C00')

    def reset_video_info_display(self):
        """重置视频信息显示"""
        self.title_label.config(text="暂无信息")
        self.duration_label.config(text="--:--")
        self.views_label.config(text="-- 次")
        self.date_label.config(text="----/--/--")

        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "💡 ", 'header')
        self.info_text.insert(tk.END, "使用说明\n", 'header')
        self.info_text.insert(tk.END, "1. 粘贴视频链接 → 2. 获取视频信息 → 3. 开始下载\n", 'value')
        self.info_text.insert(tk.END, "支持平台：", 'label')
        self.info_text.insert(tk.END, "YouTube, Bilibili, Twitter/X, Instagram, TikTok 等\n\n", 'value')
        self.info_text.insert(tk.END, "📁 下载文件夹结构：\n", 'label')
        self.info_text.insert(tk.END, "downloads/视频标题/video/视频文件.mp4\n", 'value')
        self.info_text.insert(tk.END, "downloads/视频标题/thumbnails/缩略图.jpg\n", 'value')
        self.info_text.insert(tk.END, "downloads/视频标题/metadata/信息.json", 'value')
        self.info_text.config(state=tk.DISABLED)

    def update_video_info_display(self, info_data):
        """更新视频信息显示"""
        if isinstance(info_data, str):
            # 如果是字符串，显示在详细信息区域
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, info_data)
            self.info_text.config(state=tk.DISABLED)
            return

        # 如果是字典，解析并美化显示
        try:
            # 更新信息卡片
            self.update_info_cards(info_data)

            # 更新详细信息
            self.update_detailed_info(info_data)

        except Exception as e:
            logger.error(f"更新视频信息显示失败: {e}")
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"❌ 信息显示错误: {str(e)}", 'warning')
            self.info_text.config(state=tk.DISABLED)

    def update_info_cards(self, info_data):
        """更新信息卡片"""
        try:
            # 更新标题
            title = info_data.get('title', '未知标题')
            if title:
                display_title = title[:50] + ('...' if len(title) > 50 else '')
            else:
                display_title = '未知标题'
            self.title_label.config(text=display_title)

            # 更新时长
            duration = info_data.get('duration', 0)
            if duration and duration > 0:
                try:
                    # 确保duration是数字
                    duration = float(duration)
                    minutes, seconds = divmod(int(duration), 60)
                    hours, minutes = divmod(minutes, 60)
                    if hours:
                        duration_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        duration_text = f"{minutes:02d}:{seconds:02d}"
                except (ValueError, TypeError):
                    duration_text = "--:--"
            else:
                duration_text = "--:--"
            self.duration_label.config(text=duration_text)

            # 更新观看次数
            view_count = info_data.get('view_count', 0)
            if view_count and view_count > 0:
                try:
                    view_count = int(float(view_count))  # 先转float再转int，处理字符串数字
                    if view_count >= 10000:
                        views_text = f"{view_count/10000:.1f}万 次"
                    else:
                        views_text = f"{view_count:,} 次"
                except (ValueError, TypeError):
                    views_text = "-- 次"
            else:
                views_text = "-- 次"
            self.views_label.config(text=views_text)

            # 更新上传日期
            upload_date = info_data.get('upload_date', '')
            if upload_date and len(str(upload_date)) >= 8:
                try:
                    upload_str = str(upload_date)
                    year = upload_str[:4]
                    month = upload_str[4:6]
                    day = upload_str[6:8]
                    date_text = f"{year}/{month}/{day}"
                except:
                    date_text = "----/--/--"
            else:
                date_text = "----/--/--"
            self.date_label.config(text=date_text)

        except Exception as e:
            logger.error(f"更新信息卡片失败: {e}")
            # 设置默认值
            self.title_label.config(text="信息获取失败")
            self.duration_label.config(text="--:--")
            self.views_label.config(text="-- 次")
            self.date_label.config(text="----/--/--")

    def update_detailed_info(self, info_data):
        """更新详细信息"""
        try:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)

            # 标题部分
            self.info_text.insert(tk.END, "🎬 ", 'header')
            self.info_text.insert(tk.END, "视频详细信息\n", 'header')

            # 基本信息
            title = info_data.get('title', '未知标题') or '未知标题'
            self.info_text.insert(tk.END, "📝 标题：", 'label')
            self.info_text.insert(tk.END, f"{title}\n", 'value')

            # 上传者信息
            uploader = info_data.get('uploader', '未知') or '未知'
            channel = info_data.get('channel', uploader) or uploader
            self.info_text.insert(tk.END, "👤 上传者：", 'label')
            self.info_text.insert(tk.END, f"{channel}  ", 'value')

            # 时长信息 - 同行显示
            duration = info_data.get('duration', 0)
            if duration and duration > 0:
                try:
                    duration = float(duration)
                    minutes, seconds = divmod(int(duration), 60)
                    hours, minutes = divmod(minutes, 60)
                    if hours:
                        duration_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        duration_text = f"{minutes:02d}:{seconds:02d}"
                    self.info_text.insert(tk.END, "⏱️ 时长：", 'label')
                    self.info_text.insert(tk.END, f"{duration_text}  ", 'value')
                except (ValueError, TypeError):
                    pass

            # 观看次数 - 同行显示
            view_count = info_data.get('view_count', 0)
            if view_count and view_count > 0:
                try:
                    view_count = int(float(view_count))
                    if view_count >= 10000:
                        views_text = f"{view_count/10000:.1f}万次"
                    else:
                        views_text = f"{view_count:,}次"
                    self.info_text.insert(tk.END, "👁️ 观看：", 'label')
                    self.info_text.insert(tk.END, f"{views_text}\n", 'value')
                except (ValueError, TypeError):
                    self.info_text.insert(tk.END, "\n", 'value')
            else:
                self.info_text.insert(tk.END, "\n", 'value')

            # 技术信息 - 一行显示多个
            tech_info = []

            # 分辨率
            try:
                width = info_data.get('width', 0)
                height = info_data.get('height', 0)
                if width and height:
                    width = int(float(width))
                    height = int(float(height))
                    tech_info.append(f"📐 {width}x{height}")
            except (ValueError, TypeError):
                pass

            # 文件大小
            try:
                filesize = info_data.get('filesize', 0) or info_data.get('filesize_approx', 0)
                if filesize:
                    filesize = float(filesize)
                    size_mb = filesize / (1024 * 1024)
                    if size_mb >= 1024:
                        size_text = f"{size_mb/1024:.1f}GB"
                    else:
                        size_text = f"{size_mb:.1f}MB"
                    tech_info.append(f"💾 {size_text}")
            except (ValueError, TypeError):
                pass

            # 格式信息
            ext = info_data.get('ext', '未知') or '未知'
            tech_info.append(f"📁 {ext.upper()}")

            # 显示技术信息
            if tech_info:
                self.info_text.insert(tk.END, "  ".join(tech_info) + "\n", 'value')

            # 描述（截取前150字符，更紧凑）
            description = info_data.get('description', '')
            if description:
                desc_preview = description[:150] + ('...' if len(description) > 150 else '')
                self.info_text.insert(tk.END, "📄 描述：", 'label')
                self.info_text.insert(tk.END, f"{desc_preview}\n", 'value')

            # 链接
            webpage_url = info_data.get('webpage_url', '') or info_data.get('url', '')
            if webpage_url:
                self.info_text.insert(tk.END, "🔗 链接：", 'label')
                self.info_text.insert(tk.END, f"{webpage_url}", 'url')

            self.info_text.config(state=tk.DISABLED)

        except Exception as e:
            logger.error(f"更新详细信息失败: {e}")
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "❌ ", 'warning')
            self.info_text.insert(tk.END, "信息显示错误\n\n", 'warning')
            self.info_text.insert(tk.END, f"错误详情: {str(e)}", 'value')
            self.info_text.config(state=tk.DISABLED)
    
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        status_frame.columnconfigure(1, weight=1)
        
        # 状态文本
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 统计信息
        self.stats_var = tk.StringVar(value="")
        stats_label = ttk.Label(status_frame, textvariable=self.stats_var)
        stats_label.grid(row=0, column=2, sticky=tk.E)

    def setup_bindings(self):
        """设置事件绑定"""
        # 回车键开始下载
        self.url_entry.bind('<Return>', lambda e: self.start_download())

        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def paste_url(self):
        """粘贴URL"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.url_var.set(clipboard_text.strip())
            self.status_var.set("已粘贴链接")
        except tk.TclError:
            messagebox.showwarning("警告", "剪贴板为空或无法访问")

    def start_download(self):
        """开始下载"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入视频链接")
            return

        # 验证URL
        normalized_url, error = URLValidator.validate_and_normalize(url)
        if error:
            messagebox.showerror("错误", f"链接验证失败: {error}")
            return

        # 开始下载
        try:
            download_id = self.downloader.start_download(
                normalized_url,
                config_manager.get_download_path(),
                self.on_download_progress
            )

            if download_id:
                # 添加到下载列表
                self.add_download_item(download_id, normalized_url)
                self.url_var.set("")  # 清空输入框
                self.status_var.set(f"开始下载: {normalized_url}")
                logger.info(f"开始下载: {download_id}")
            else:
                messagebox.showerror("错误", "无法开始下载，请检查链接")

        except Exception as e:
            messagebox.showerror("错误", f"下载失败: {str(e)}")
            logger.error(f"下载失败: {e}")

    def get_video_info(self):
        """获取视频信息"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("警告", "请输入视频链接")
            return

        # 在新线程中获取信息，避免界面冻结
        def get_info_worker():
            try:
                self.status_var.set("正在获取视频信息...")
                self.update_video_info_display("正在获取视频信息，请稍候...")

                info = self.downloader.get_video_info(url)

                if info:
                    # 在主界面显示信息
                    self.display_video_info_in_main(info)
                    self.status_var.set("视频信息获取成功")
                else:
                    self.update_video_info_display("无法获取视频信息，请检查链接是否正确")
                    self.status_var.set("获取视频信息失败")

            except Exception as e:
                error_msg = f"获取信息失败: {str(e)}"
                self.update_video_info_display(error_msg)
                self.status_var.set("获取视频信息失败")

        threading.Thread(target=get_info_worker, daemon=True).start()

    def display_video_info_in_main(self, info):
        """在主界面显示视频信息"""
        # 直接传递信息字典给美化的显示方法
        self.root.after(0, lambda: self.update_video_info_display(info))

    def format_duration(self, seconds):
        """格式化时长"""
        if not seconds or seconds is None:
            return "未知"

        try:
            # 确保seconds是数字类型
            seconds = float(seconds)
            if seconds <= 0:
                return "未知"

            # 转换为整数秒
            total_seconds = int(seconds)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            remaining_seconds = total_seconds % 60

            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"
            else:
                return f"{minutes:02d}:{remaining_seconds:02d}"
        except (ValueError, TypeError):
            return "未知"

    def select_download_folder(self):
        """选择下载目录"""
        folder = filedialog.askdirectory(
            title="选择下载目录",
            initialdir=config_manager.get_download_path()
        )

        if folder:
            config_manager.set('DEFAULT', 'download_path', folder)
            self.folder_var.set(f"下载目录: {folder}")
            self.status_var.set(f"下载目录已更改为: {folder}")

    def clear_completed(self):
        """清除已完成的下载"""
        # 获取已完成的项目
        completed_items = []
        for item in self.download_tree.get_children():
            values = self.download_tree.item(item)['values']
            if len(values) > 1 and values[1] in ['已完成', '错误', '已取消']:
                completed_items.append(item)

        # 删除GUI中的项目
        for item in completed_items:
            self.download_tree.delete(item)

        # 清除下载器中的记录
        self.downloader.clear_completed_downloads()

        self.status_var.set(f"已清除 {len(completed_items)} 个已完成的下载")

    def open_settings(self):
        """打开设置对话框"""
        try:
            from gui.settings_dialog import SettingsDialog
            settings_dialog = SettingsDialog(self.root)
            settings_dialog.show()
        except Exception as e:
            logger.error(f"打开设置对话框失败: {e}")
            messagebox.showerror("错误", f"打开设置对话框失败: {e}")

    def add_download_item(self, download_id, url):
        """添加下载项目到列表"""
        # 计算行索引用于交替颜色
        row_count = len(self.download_tree.get_children())
        row_tag = 'evenrow' if row_count % 2 == 0 else 'oddrow'

        # 插入新项目
        item = self.download_tree.insert('', 'end', values=(
            '🔄 获取视频信息中...', '⏳ 等待中', '0%', '', '', datetime.now().strftime('%H:%M:%S')
        ), tags=(row_tag,))

        # 存储映射关系
        self.download_items[download_id] = item

    def on_download_progress(self, download_id, progress):
        """下载进度回调"""
        # 这个方法在下载线程中调用，需要线程安全
        pass  # 实际更新在update_progress_loop中进行

    def update_progress_loop(self):
        """进度更新循环（在主线程中运行）"""
        while True:
            try:
                self.update_download_list()
                self.update_statistics()
            except Exception as e:
                logger.error(f"更新进度失败: {e}")

            # 每秒更新一次
            threading.Event().wait(1)

    def update_download_list(self):
        """更新下载列表显示"""
        downloads = self.downloader.get_all_downloads()

        for download_id, progress in downloads.items():
            if download_id in self.download_items:
                item = self.download_items[download_id]

                # 状态映射（带图标）
                status_map = {
                    'waiting': '⏳ 等待中',
                    'downloading': '⬇️ 下载中',
                    'completed': '✅ 已完成',
                    'error': '❌ 错误',
                    'cancelled': '⏹️ 已取消',
                    'paused': '⏸️ 已暂停'
                }

                # 格式化进度显示
                if progress.progress > 0:
                    progress_text = f"{progress.progress:.1f}%"
                    # 添加进度条效果
                    bar_length = 10
                    filled_length = int(bar_length * progress.progress / 100)
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)
                    progress_display = f"{progress_text} {bar}"
                else:
                    progress_display = "0%"

                # 格式化速度显示
                speed_display = progress.speed if progress.speed else ""
                if speed_display and not speed_display.endswith('/s'):
                    speed_display = f"{speed_display}/s" if speed_display != "" else ""

                # 格式化文件大小
                size_display = progress.file_size if progress.file_size else ""

                # 更新项目值
                values = (
                    progress.title or '🔄 获取视频信息中...',
                    status_map.get(progress.status, progress.status),
                    progress_display,
                    speed_display,
                    size_display,
                    progress.start_time.strftime('%H:%M:%S') if progress.start_time else ''
                )

                # 确定状态标签
                status_tag = self.get_status_tag(progress.status)

                # 在主线程中更新GUI
                self.root.after(0, lambda i=item, v=values, t=status_tag: self.update_tree_item(i, v, t))

    def get_status_tag(self, status):
        """获取状态对应的标签"""
        tag_map = {
            'downloading': 'downloading',
            'completed': 'completed',
            'error': 'error',
            'cancelled': 'error',
            'paused': 'paused'
        }
        return tag_map.get(status, '')

    def update_tree_item(self, item, values, status_tag):
        """更新树形控件项目"""
        # 获取当前标签
        current_tags = list(self.download_tree.item(item, 'tags'))

        # 移除旧的状态标签，保留行颜色标签
        new_tags = [tag for tag in current_tags if tag in ['oddrow', 'evenrow']]

        # 添加新的状态标签
        if status_tag:
            new_tags.append(status_tag)

        # 更新项目
        self.download_tree.item(item, values=values, tags=new_tags)

    def update_statistics(self):
        """更新统计信息"""
        stats = self.downloader.get_download_statistics()
        stats_text = f"总计: {stats['total']} | 下载中: {stats['downloading']} | 已完成: {stats['completed']} | 错误: {stats['error']}"
        self.root.after(0, lambda: self.stats_var.set(stats_text))

    def show_context_menu(self, event):
        """显示右键菜单"""
        # 选择点击的项目
        item = self.download_tree.identify_row(event.y)
        if item:
            self.download_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def cancel_selected_download(self):
        """取消选中的下载"""
        selected = self.download_tree.selection()
        if not selected:
            return

        # 找到对应的download_id
        for download_id, item in self.download_items.items():
            if item in selected:
                if self.downloader.cancel_download(download_id):
                    self.status_var.set(f"已取消下载: {download_id}")
                break

    def retry_selected_download(self):
        """重新下载选中项目"""
        messagebox.showinfo("提示", "重新下载功能正在开发中...")

    def open_download_folder(self):
        """打开下载文件夹"""
        download_path = config_manager.get_download_path()
        try:
            os.startfile(download_path)  # Windows
        except AttributeError:
            try:
                os.system(f'open "{download_path}"')  # macOS
            except:
                os.system(f'xdg-open "{download_path}"')  # Linux

    def copy_selected_url(self):
        """复制选中项目的URL"""
        selected = self.download_tree.selection()
        if not selected:
            return

        # 找到对应的URL
        for download_id, item in self.download_items.items():
            if item in selected:
                progress = self.downloader.get_download_progress(download_id)
                if progress:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(progress.url)
                    self.status_var.set("链接已复制到剪贴板")
                break

    def on_closing(self):
        """窗口关闭事件"""
        # 询问是否确认退出
        if messagebox.askokcancel("退出", "确定要退出视频下载器吗？"):
            # 取消所有正在进行的下载
            downloads = self.downloader.get_all_downloads()
            for download_id, progress in downloads.items():
                if progress.status in ['waiting', 'downloading']:
                    self.downloader.cancel_download(download_id)

            self.root.destroy()

    def run(self):
        """运行主窗口"""
        self.root.mainloop()


def main():
    """主函数"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        messagebox.showerror("错误", f"应用程序启动失败: {str(e)}")


if __name__ == "__main__":
    main()
