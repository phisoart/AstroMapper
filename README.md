# AstroMapper

AstroMapper is a modern GUI application built with PySide6 for managing, visualizing, and annotating large-scale images (e.g., microscopy, bio-imaging). It provides project-based management, ROI (Region of Interest) tools, logging, and a variety of user-friendly features for efficient image analysis.

---

## Features

- **Modern PySide6-based GUI**
- Project-based image, ROI, and log management
- ROI (Region of Interest) creation, editing, and visualization
- Image zoom, pan, and sub-image preview
- Recent projects, settings dialog, license dialog, and more
- Custom dark theme with QSS styling
- Rich resource support (icons, images, color/well info, etc.)

---

## Directory Structure

```
AstroMapper/
├── src/
│   ├── main.py                # Main entry point
│   ├── config/                # App and project settings (json, yaml)
│   ├── core/
│   │   └── roi/               # ROI data structures and management
│   ├── ui/
│   │   ├── main_window.py     # Main window logic
│   │   ├── dialogs/           # Settings and license dialogs
│   │   ├── styles/            # QSS style files
│   │   └── widgets/           # ImageWidget, LogWidget, ToolBar, etc.
│   └── utils/                 # Config, settings, and helper utilities
├── res/
│   ├── images/                # Icons, logos, button images
│   └── data/                  # Color, well, and point info (json)
├── requirements.txt           # Python dependencies
├── AstroMapper.spec           # PyInstaller build spec
└── README.md                  # (This file)
```

---

## Main Components

- **src/main.py**  
  Application entry point. Initializes the UI, main window, and connects signals.

- **src/ui/main_window.py**  
  Main window layout, project creation/opening, status bar, and overall app flow.

- **src/ui/widgets/**  
  - `image_widget.py`: Image display, zoom/pan, ROI visualization
  - `log_widget.py`: ROI list, logging, settings dialog integration
  - `tool_bar.py`, `title_bar.py`, `status_bar.py`, `init_view.py`: UI components

- **src/core/roi/ROI.py**  
  ROI data structures and management classes

- **src/utils/**  
  - `config.py`, `settings.py`: Project/image/settings management
  - `helper.py`: Helper functions and event handlers

- **res/images/**  
  App icons, logos, and button images

- **res/data/**  
  Color, well, and point info in JSON format

---

## Installation & Usage

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   (Requires Python 3.8+ and packages such as PySide6, Pillow, etc.)

2. **Run the application**
   ```bash
   python src/main.py
   ```

3. **Build Windows executable (optional)**
   ```bash
   pyinstaller AstroMapper.spec
   ```

---

## Typical Workflow

1. Create or open a project
2. Load an image (supports large images)
3. Create and edit ROIs (with color, well, note, etc.)
4. Manage logs and settings
5. Use sub-image preview, crosshair, and other visualization tools

---

## Screenshots

> (You can add screenshots of the main window, ROI editing, and dialogs here for better documentation.)

---

## Contribution & Support

- Pull requests and issues are welcome!
- For questions or feedback, please contact: [phisoart on GitHub](https://github.com/phisoart/AstroMapper)

---

## License

See `res/license.txt` and the in-app license dialog for details.

---

If you need more detailed usage instructions, developer/contributor guide, or want to add badges, please let me know!
You can copy this as your final README.md. 