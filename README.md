# ComfyUI Metadata Reader

A Windows desktop tool for reading and parsing metadata embedded in ComfyUI-generated images (PNG, WebP, JPEG), including workflows, prompts, seeds, and sampling parameters.

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
