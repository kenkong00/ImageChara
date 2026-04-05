# 图灵注 ImageChara

A Windows desktop tool for reading ComfyUI image metadata and injecting AI character information into images. Supports PNG, WebP, and JPEG formats.

<img width="1800" height="1173" alt="image" src="https://github.com/user-attachments/assets/823eaed1-d0d3-429c-8cc9-4d5bb88dd1ca" />
<img width="1800" height="1173" alt="image" src="https://github.com/user-attachments/assets/d97f1817-cf49-4089-87dc-cb199ea6965b" />
<img width="1800" height="1173" alt="image" src="https://github.com/user-attachments/assets/98a070a1-cef0-41d1-8034-eb15a256b19e" />

## Quick Start for New Users

### Option 1: Run from Source (Recommended for Developers)

1. **Install Python 3.10+**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
2. **Download the Project**
   ```bash
   git clone https://github.com/kenkong00/prompts-reader.git
   cd prompts-reader
   ```
3. **Create Virtual Environment (Optional but Recommended)**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the Application**
   ```bash
   python main.py
   ```

### Option 2: Use Pre-built Executable (Coming Soon)

Download the latest release from the [Releases](https://github.com/kenkong00/prompts-reader/releases) page.

## Features

### Metadata Reading
- Support for ComfyUI PNG, WebP, and JPEG images
- Drag and drop support for single or multiple images
- Automatic metadata parsing:
  - Prompt (positive & negative)
  - Workflow JSON
  - Generation parameters (seed, steps, CFG, sampler, model)
  - AI Character information (chara metadata)

### Character Information Injection
- Edit and save AI character information directly into images
- Support for character fields: Name, Description, Personality, Scenario, First Message, etc.
- Automatic format conversion: WebP/JPEG images are converted to PNG when saving character data
- Newly generated PNG files are automatically added to the file list

### User Interface
- Modern dark theme UI (Catppuccin Mocha style)
- Three-panel layout: file list, image preview, metadata display
- Thumbnail and list view modes
- Multi-select support in both list and thumbnail views
- Delete selected files with Del key or right-click menu
- Image preview with zoom, pan, and reset
- Copy prompts and workflow to clipboard
- Export metadata to JSON or TXT files

## Supported Node Types

The parser supports the following ComfyUI node types:

- `CLIPTextEncode` - Standard text encoding
- `CLIPTextEncodeSDXL` - SDXL text encoding
- `Text Multiline` - Multiline text input
- `KSampler` / `KSamplerAdvanced` - Sampling parameters
- `UNETLoader` / `CheckpointLoaderSimple` - Model loading

## Project Structure

```
imagechara/
├── main.py                    # Main entry point
├── parsers/                   # Parser module
│   ├── __init__.py
│   └── metadata_parser.py     # Metadata parser
├── ui/                        # UI module
│   ├── __init__.py
│   ├── image_panel.py         # Image display panel
│   ├── file_list_panel.py     # File list panel
│   ├── result_panel.py        # Result display panel
│   └── styles.py              # Theme and styles
├── utils/                     # Utility module
│   ├── __init__.py
│   └── helpers.py             # Helper functions
├── logo/                      # Application icons
└── requirements.txt           # Dependencies
```

## Usage

### Import Images
- Click "File" button to select image files
- Click "Dir" button to import a directory
- Drag and drop images directly into the window

### View Metadata
- Click on an image in the list to view its metadata
- Switch between Prompt, Params, Workflow, and Character tabs

### Edit Character Information
1. Select an image with character metadata (or any image to add new character info)
2. Go to the "Character" tab
3. Click "Edit" button to enter edit mode
4. Modify character information as needed
5. Click "Save" to save changes to the image
   - For WebP/JPEG files, a new PNG file will be created automatically

### Image Preview
- Scroll wheel: Zoom in/out
- Drag: Pan image
- Double-click: Reset to fit

### File Management
- Multi-select: Hold Ctrl to select multiple files, Shift for range selection
- Delete: Press Del key or right-click to delete selected files
- Clear: Click "Clear" button to remove all files from the list

### Export Data
- Copy: Copy current tab content to clipboard
- Export JSON: Save metadata as JSON file
- Export TXT: Save metadata as text file

## Building from Source

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=logo/logo.ico main.py
```

The executable will be in the `dist` directory.

## Requirements

- Python 3.10+
- Pillow
- tkinterdnd2

## Notes

- ComfyUI-generated images with embedded metadata are supported for reading
- WebP and JPEG images will be converted to PNG when saving character information
- Large thumbnail collections may use significant memory

## License

Open source project, contributions welcome!

## Version History

### v1.3.0

- **Renamed to 图灵注 ImageChara** - Reflecting expanded functionality beyond ComfyUI metadata
- **Character information editing** - Edit and save AI character data into images
- **Automatic format conversion** - WebP/JPEG automatically convert to PNG when saving character info
- **Multi-select support** - Select multiple files in both list and thumbnail views
- **Del key and right-click delete** - Quick file removal from list
- **Clear button improvement** - Now clears preview image as well
- **New file auto-selection** - Converted PNG files are automatically added and selected

### v1.2.0

- **Modern dark theme UI** (Catppuccin Mocha style)
- **English interface** with Chinese documentation
- **Enhanced metadata parser** for CLIPTextEncode nodes
- **Improved UTF-16 encoding detection** for WebP images
- **Dynamic preview panel width** for maximized windows
- **Fixed type error** handling for list-type metadata values
- **Optimized thumbnail selection** with better border width
- **Improved tab switching** with proper selected state
- **Enhanced button layout** with better spacing
- **Hand cursor** for image drag operations
- **Fixed multi-file drag and drop** (Windows curly brace format)
- **Modular code structure** with parsers, ui, and utils modules
- **Image preview improvements** with zoom, pan, and reset
- **Image cache mechanism** for smoother zooming
- **Fixed thumbnail mode selection** after drag and drop

### v1.1.0

- Modular code structure
- Image preview with zoom, pan, reset
- Fixed multi-file drag and drop

### v1.0.0

- Initial release
- Basic metadata parsing
- PNG, WebP, JPEG support

---

## 功能特性(中文)

### 元数据读取
- 支持选择ComfyUI PNG、WebP和JPEG图片
- 支持拖拽PNG、WebP或JPEG图片到应用程序窗口或图片区域
- 自动读取图片的元数据，解析字段：
  - prompt（提示词）
  - workflow（工作流）
  - seed、steps、cfg、sampler_name等生成参数
  - AI角色信息（chara元数据）

### 角色信息注入
- 编辑并保存AI角色信息到图片中
- 支持的角色字段：名称、描述、性格、场景、第一条消息等
- 自动格式转换：保存角色信息时，WebP/JPEG图片自动转换为PNG格式
- 新生成的PNG文件自动添加到文件列表并选中

### 用户界面
- 现代深色主题UI（Catppuccin Mocha风格）
- 三栏布局设计：文件列表、图片预览、解析结果
- 支持文件列表和缩略图视图切换
- 列表和缩略图模式均支持多选
- Del键或右键菜单删除选中的文件
- 图片预览支持滚轮缩放、拖拽平移、双击复位
- 一键复制提示词、一键复制工作流JSON
- 支持将解析结果导出为JSON/TXT文件

## 使用说明

### 导入图片
- 点击"File"按钮选择图片文件
- 点击"Dir"按钮导入整个目录
- 直接拖拽图片到窗口中

### 查看元数据
- 点击列表中的图片查看其元数据
- 在Prompt、Params、Workflow、Character标签页之间切换

### 编辑角色信息
1. 选择一张包含角色元数据的图片（或任意图片以添加新的角色信息）
2. 切换到"Character"标签页
3. 点击"Edit"按钮进入编辑模式
4. 根据需要修改角色信息
5. 点击"Save"保存更改到图片
   - 对于WebP/JPEG文件，会自动创建新的PNG文件

### 图片预览
- 滚轮：缩放
- 拖拽：平移
- 双击：复位

### 文件管理
- 多选：按住Ctrl点击多选，按住Shift范围选择
- 删除：按Del键或右键删除选中的文件
- 清空：点击"Clear"按钮清空列表（同时清空预览）

### 导出数据
- Copy：复制当前标签页内容到剪贴板
- Export JSON：保存元数据为JSON文件
- Export TXT：保存元数据为文本文件

## 技术栈

- 语言：Python
- GUI：Tkinter（原生）
- 依赖库：Pillow、tkinterdnd2

## 项目结构

```
imagechara/
├── main.py                    # 主入口文件
├── parsers/                   # 解析器模块
│   ├── __init__.py
│   └── metadata_parser.py     # 元数据解析器
├── ui/                        # 界面模块
│   ├── __init__.py
│   ├── image_panel.py         # 图片显示面板
│   ├── file_list_panel.py     # 文件列表面板
│   ├── result_panel.py        # 结果显示面板
│   └── styles.py              # 主题样式
├── utils/                     # 工具模块
│   ├── __init__.py
│   └── helpers.py             # 工具函数
├── logo/                      # 应用图标
└── requirements.txt           # 依赖列表
```

## 版本历史

### v1.3.0
- **更名为图灵注 ImageChara** - 反映超越ComfyUI元数据的扩展功能
- **角色信息编辑** - 编辑并保存AI角色数据到图片
- **自动格式转换** - 保存角色信息时WebP/JPEG自动转换为PNG
- **多选支持** - 列表和缩略图模式均支持多选
- **Del键和右键删除** - 快速从列表中移除文件
- **清空按钮改进** - 现在同时清空预览图片
- **新文件自动选中** - 转换后的PNG文件自动添加并选中
