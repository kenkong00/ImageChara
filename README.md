# ComfyUI Metadata Reader

A Windows desktop tool for reading and parsing metadata embedded in ComfyUI-generated images (PNG, WebP, JPEG), including workflows, prompts, seeds, and sampling parameters.

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

- Support for ComfyUI PNG, WebP, and JPEG images
- Drag and drop support for single or multiple images
- Automatic metadata parsing:
  - Prompt (positive & negative)
  - Workflow JSON
  - Generation parameters (seed, steps, CFG, sampler, model)
- Modern dark theme UI
- Three-panel layout: file list, image preview, metadata display
- Thumbnail and list view modes
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
comfyui-metadata-reader/
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
└── requirements.txt           # Dependencies
```

## Usage

1. **Import Images**
   - Click "File" button to select image files
   - Click "Dir" button to import a directory
   - Drag and drop images directly into the window
2. **View Metadata**
   - Click on an image in the list to view its metadata
   - Switch between Prompt, Params, and Workflow tabs
3. **Image Preview**
   - Scroll wheel: Zoom in/out
   - Drag: Pan image
   - Double-click: Reset to fit
4. **Export Data**
   - Copy: Copy current tab content to clipboard
   - Export JSON: Save metadata as JSON file
   - Export TXT: Save metadata as text file

## Building from Source

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

The executable will be in the `dist` directory.

## Requirements

- Python 3.10+
- Pillow
- tkinterdnd2

## Notes

- Only ComfyUI-generated images with embedded metadata are supported
- Some WebP images may have incomplete EXIF data parsing
- Large thumbnail collections may use significant memory

## License

Open source project, contributions welcome!

## Version History

### v1.2.0

- Modern dark theme UI (Catppuccin Mocha style)
- English interface
- Enhanced metadata parser for CLIPTextEncode nodes
- Improved UTF-16 encoding detection for WebP images
- Dynamic preview panel width for maximized windows

### v1.1.0

- Modular code structure
- Image preview with zoom, pan, reset
- Fixed multi-file drag and drop

### v1.0.0

- Initial release
- Basic metadata parsing
- PNG, WebP, JPEG support




## 功能特性(中文)

- 支持选择ComfyUI PNG、WebP和JPEG图片
- 支持拖拽PNG、WebP或JPEG图片到应用程序窗口或图片区域
- 自动读取图片的元数据，解析字段：
  - prompt（提示词）
  - workflow（工作流）
  - seed、steps、cfg、sampler_name等生成参数
- 界面清晰展示：提示词、种子、步数、CFG、采样器、模型信息
- 提供一键复制提示词、一键复制工作流JSON按钮
- 支持将解析结果导出为JSON/TXT文件
- 友好的错误提示（非ComfyUI图片、文件损坏等）
- 三栏布局设计：文件列表、图片预览、解析结果
- 支持导入整个目录的图片（追加模式）
- 支持文件列表和缩略图视图切换
- 支持批量选择图片文件
- 图片预览支持滚轮缩放、拖拽平移、双击复位

## 技术栈

- 语言：Python
- GUI：Tkinter（原生）
- 依赖库：Pillow、tkinterdnd2

## 项目结构

```
comfyui出图查看器/
├── main.py                    # 主入口文件
├── parsers/                   # 解析器模块
│   ├── __init__.py
│   └── metadata_parser.py     # 元数据解析器
├── ui/                        # 界面模块
│   ├── __init__.py
│   ├── image_panel.py         # 图片显示面板
│   ├── file_list_panel.py     # 文件列表面板
│   └── result_panel.py        # 结果显示面板
└── utils/                     # 工具模块
    ├── __init__.py
    └── helpers.py             # 工具函数
```


