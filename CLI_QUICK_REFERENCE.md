# 🎬 视频下载器终端版 - 数字选项快速参考

## 📋 数字选项一览表

| 选项 | 功能 | 示例 |
|------|------|------|
| **1** | 仅获取视频信息 | `python cli_main.py -1 <URL>` |
| **2** | 指定下载目录 | `python cli_main.py -2 downloads/music <URL>` |
| **3** | 视频质量设置 | `python cli_main.py -3 720p <URL>` |
| **4** | 批量下载文件 | `python cli_main.py -4 urls.txt` |
| **5** | 仅下载音频 | `python cli_main.py -5 <URL>` |
| **6** | 仅下载视频 | `python cli_main.py -6 <URL>` |
| **7** | 指定格式 | `python cli_main.py -7 mp4 <URL>` |
| **8** | 下载播放列表 | `python cli_main.py -8 <PLAYLIST_URL>` |
| **9** | 列出支持平台 | `python cli_main.py -9` |

## 🔥 常用组合

### 基础下载
```bash
# 直接下载
python cli_main.py https://www.youtube.com/watch?v=dQw4w9WgXcQ

# 获取信息
python cli_main.py -1 https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### 质量控制
```bash
# 720p质量
python cli_main.py -3 720p https://www.youtube.com/watch?v=dQw4w9WgXcQ

# 最佳质量
python cli_main.py -3 best https://www.youtube.com/watch?v=dQw4w9WgXcQ

# 最低质量(节省流量)
python cli_main.py -3 worst https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### 音频下载
```bash
# 仅下载音频
python cli_main.py -5 https://www.youtube.com/watch?v=dQw4w9WgXcQ

# 音频+自定义目录
python cli_main.py -5 -2 music/ https://www.youtube.com/watch?v=dQw4w9WgXcQ

# 音频+指定格式
python cli_main.py -5 -7 mp3 https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### 批量下载
```bash
# 从文件批量下载
python cli_main.py -4 urls.txt

# 批量下载到指定目录
python cli_main.py -4 urls.txt -2 downloads/batch/

# 批量下载仅音频
python cli_main.py -4 urls.txt -5
```

### 高级组合
```bash
# 720p视频到音乐目录
python cli_main.py -3 720p -2 music/ https://www.youtube.com/watch?v=dQw4w9WgXcQ

# 仅音频，MP3格式，自定义目录
python cli_main.py -5 -7 mp3 -2 downloads/audio/ https://www.youtube.com/watch?v=dQw4w9WgXcQ

# 获取信息，指定质量查看
python cli_main.py -1 -3 1080p https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

## 📊 质量选项详解

| 质量选项 | 说明 | 适用场景 |
|----------|------|----------|
| `best` | 最佳质量 | 高质量收藏，网络良好 |
| `1080p` | 1080p分辨率 | 高清观看，平衡质量和大小 |
| `720p` | 720p分辨率 | 标准高清，节省空间 |
| `480p` | 480p分辨率 | 移动设备，节省流量 |
| `worst` | 最低质量 | 仅需音频内容，极度节省空间 |

## 🎵 格式选项

### 视频格式
- `mp4` - 最通用，兼容性最好
- `webm` - 较小文件，现代浏览器支持
- `mkv` - 高质量，支持多音轨字幕

### 音频格式
- `mp3` - 最通用的音频格式
- `m4a` - 高质量，Apple设备优化
- `ogg` - 开源格式，质量好

## 🚀 快速记忆法

### 数字含义
- **1-4**: 基础功能 (信息、目录、质量、批量)
- **5-6**: 媒体类型 (音频、视频)
- **7-8**: 高级功能 (格式、播放列表)
- **9**: 帮助信息 (平台列表)

### 记忆口诀
```
1信息 2目录 3质量 4批量
5音频 6视频 7格式 8列表
9平台查看全支持
```

## 💡 使用技巧

### 1. 先查看信息
```bash
# 下载前先看看视频信息
python cli_main.py -1 <URL>
```

### 2. 测试小文件
```bash
# 用最低质量测试下载
python cli_main.py -3 worst <URL>
```

### 3. 批量准备
```bash
# 创建URL列表文件
echo "https://www.youtube.com/watch?v=dQw4w9WgXcQ" > urls.txt
echo "https://www.bilibili.com/video/BV1GJ411x7h7" >> urls.txt
python cli_main.py -4 urls.txt
```

### 4. 音频收藏
```bash
# 建立音乐下载流程
mkdir music
python cli_main.py -5 -2 music/ -7 mp3 <MUSIC_URL>
```

## ⚠️ 注意事项

1. **数字选项必须带连字符**: `-1` 不是 `1`
2. **组合使用**: 多个选项可以组合，如 `-5 -2 music/`
3. **URL放最后**: 通常将URL放在命令的最后
4. **文件路径**: 使用相对或绝对路径都可以
5. **批量文件**: 每行一个URL，支持 `#` 注释

## 🆘 获取帮助

```bash
# 快速帮助
python cli_main.py

# 完整帮助
python cli_main.py --help

# 版本信息
python cli_main.py --version

# 支持平台
python cli_main.py -9
```

---

**记住：数字选项让命令更简洁！** 🎯
