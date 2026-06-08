# PPT Grabber — 会议截图助手

一个轻量级屏幕监控工具，在线会议期间自动抓取演示文稿的每一页幻灯片。

当演讲者翻页时，程序自动检测画面变化并保存高分辨率截图，全程无需手动操作。

## 功能特点

- **自动检测** — 逐帧比对屏幕画面，检测到内容变化时自动截图
- **全局热键** — 通过键盘控制启动/暂停/退出，无需切换窗口
- **会话隔离** — 每次运行创建独立的时间戳文件夹（`Meeting_YYYYMMDD_HHMM`）
- **Obsidian 友好** — 自动生成 `slides_index.md`，含 YAML 头部和 wiki-link 嵌入
- **异步 I/O** — 截图保存不阻塞监控主循环

## 环境要求

- Python 3.7+
- Windows 系统

安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方式

### 快速启动

双击 `start_grabber.bat`，或在命令行运行：

```bash
python ppt_grabber.py
```

### 快捷键

| 按键 | 功能 |
|------|------|
| `F9` | 开始监控 |
| `F10` | 暂停监控 |
| `Esc` | 退出程序 |

### 输出说明

截图以 JPEG 格式保存在会话文件夹中，同时生成 `slides_index.md`，可直接在 [Obsidian](https://obsidian.md) 中打开。

**默认输出位置：** 脚本同目录下的 `sessions/` 文件夹。

如需直接保存到 Obsidian 仓库，修改 `ppt_grabber.py` 中的 `OBSIDIAN_VAULT` 路径：

```python
OBSIDIAN_VAULT = r"C:\你的Obsidian仓库路径\收件箱"
```

## 工作原理

1. 按固定间隔（默认 2 秒）截取主显示器画面
2. 将帧缩放为 128×128 灰度缩略图，快速比对
3. 计算相邻两帧的绝对像素差异
4. 当平均差异超过阈值（默认 8.0）时，保存原始分辨率 JPEG

## 参数配置

编辑 `ppt_grabber.py` 顶部常量：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `THRESHOLD` | `8.0` | 灵敏度，越小越灵敏 |
| `CHECK_INTERVAL` | `2` | 帧捕获间隔（秒） |
| `OBSIDIAN_VAULT` | `""` | Obsidian 仓库路径（留空则在 `sessions/` 输出） |

## 许可证

MIT
