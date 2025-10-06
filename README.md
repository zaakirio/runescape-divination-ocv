# RuneScape Divination Bot (OpenCV)

A computer vision-based bot for Divination training in RuneScape using OpenCV blob detection and HSV color filtering.

## Features

- **Wisp Detection**: Detects cyan/blue-green wisps using blob detection with shape and color analysis
- **Energy Rift Detection**: Identifies bright lime-green energy rifts for memory conversion
- **Camera Control**: Automatic camera rotation to find targets
- **Debug Visualization**: Saves detection masks and annotated images for tuning parameters
- **Randomized Timing**: Variable click durations and harvest times to appear more human-like

## Prerequisites

- Python 3.8 or higher
- macOS, Windows, or Linux
- RuneScape client running in windowed mode

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/zaakirio/runescape-divination-ocv.git
cd runescape-divination-ocv
```

### 2. Install UV 

This project uses **UV** for fast, reliable dependency management:

**On macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Install Dependencies

UV automatically creates a virtual environment and installs all dependencies with locked versions:

```bash
uv sync
```

This will install:
- `opencv-python` - Computer vision library for image processing
- `numpy` - Numerical computing library
- `pyautogui` - GUI automation for mouse/keyboard control

## Configuration

Before running the bot, you need to configure the screen capture region to match your RuneScape client window.

### Adjusting Screen Region

Edit `config.py` and modify the `ScreenConfig` class:

```python
class ScreenConfig:
    REGION_X = 300      # X coordinate of top-left corner
    REGION_Y = 300      # Y coordinate of top-left corner
    REGION_WIDTH = 400  # Width of capture region
    REGION_HEIGHT = 400 # Height of capture region
```

**To find your coordinates:**
1. Run Python in interactive mode: `python`
2. Import pyautogui: `import pyautogui`
3. Check mouse position: `pyautogui.position()` (move mouse to desired corner)
4. Update the values in `config.py`

### Tuning Detection Parameters

You can adjust detection sensitivity in `config.py`:

- **WispDetectionConfig**: HSV ranges, area filters, circularity thresholds
- **RiftDetectionConfig**: HSV ranges, minimum area, brightness thresholds
- **BotConfig**: Harvest timing, conversion timing, click durations

## Usage

### Running the Bot

**With UV (recommended):**
```bash
uv run main.py
```

### Stopping the Bot

Press `Ctrl+C` to stop the bot gracefully.

### Debug Mode

Debug mode is enabled by default in `config.py`:

```python
class DebugConfig:
    ENABLED = True
```

When enabled, the bot saves detection images to the `debug-screenshots/` folder:

- `original.png` - Original screenshot
- `mask.png` - HSV color mask for wisps
- `detected_objects.png` - Annotated detections (green = accepted, red = rejected)
- `rift_original.png` - Screenshot during rift detection
- `rift_mask.png` - HSV mask for energy rift
- `rift_detected.png` - Annotated rift detections

Use these images to tune your detection parameters if the bot isn't finding wisps or rifts correctly.

## Project Structure

```
runescape-divination-ocv/
├── main.py                 # Main entry point
├── config.py              # All configuration settings
├── pyproject.toml         # Project metadata and dependencies (UV/modern Python)
├── uv.lock                # Locked dependency versions for reproducibility
├── requirements.txt       # Legacy dependency list (for pip)
├── .venv/                 # Virtual environment (auto-created by UV)
├── controllers/
│   ├── bot.py            # Main bot logic and state management
│   └── camera.py         # Camera rotation controls
├── detectors/
│   ├── base.py           # Base detector class with shared functionality
│   ├── wisp_detector.py  # Wisp detection using blob detection
│   └── rift_detector.py  # Energy rift detection
├── utils/
│   ├── image_processor.py # Screenshot capture and image processing
│   └── geometry.py        # Contour analysis and shape calculations
└── debug-screenshots/     # Debug output images (created automatically)
```

## How It Works

1. **Capture**: Takes screenshots of the configured game region
2. **Color Filter**: Converts to HSV and filters for target colors (cyan for wisps, lime-green for rifts)
3. **Morphology**: Applies opening/closing operations to clean up the mask
4. **Blob Detection**: Finds contours and analyzes shape properties (area, circularity, aspect ratio)
5. **Filtering**: Rejects candidates that don't match expected characteristics
6. **Action**: Clicks on the best candidate (largest area) and waits for harvest/conversion

## Troubleshooting

### Bot Can't Find Wisps/Rifts

1. Check `debug-screenshots/` folder to see what the bot is detecting
2. Adjust HSV ranges in `config.py` if colors don't match
3. Verify screen region is correctly positioned over the game

### Import Errors

Make sure your virtual environment is activated:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Permission Issues (macOS)

You may need to grant accessibility permissions:
1. System Preferences → Security & Privacy → Privacy tab
2. Enable your terminal app under "Accessibility" and "Screen Recording"

## Disclaimer

This bot is for educational purposes only. Using automation tools may violate the game's terms of service and could result in account penalties. Use at your own risk.

## License

MIT License - See LICENSE file for details
