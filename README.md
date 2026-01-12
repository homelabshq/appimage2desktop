# AppImage Desktop Generator

A Python CLI tool that automatically generates `.desktop` files for AppImages and integrates them into your Linux desktop environment's application launcher.

## Features

- 🚀 **Automatic Integration**: Generates `.desktop` files and places them where your desktop environment can find them
- 🔍 **Smart Detection**: Automatically extracts app information (name, description, categories) from AppImages
- 🎨 **Icon Handling**: Extracts and installs icons from AppImages to the correct system location
- ⚙️ **Customizable**: Override detected information with command-line options
- 📁 **Multiple Locations**: Supports both user (`~/.local/share/applications`) and system-wide installation
- 🛡️ **Error Handling**: Gracefully handles malformed AppImages and missing resources

## Installation

### Method 1: Direct Download
```bash
curl -fsSL https://kanishkk.xyz/appimage2desktop | bash
```

### Method 2: Clone Repository
```bash
git clone https://github.com/homelabshq/appimage2desktop.git
cd appimage2desktop
chmod +x appimage2desktop.py

# Optional: Create symlink for easier access
ln -s $(pwd)/appimage2desktop.py ~/.local/bin/appimage2desktop
```

## Requirements

- Python 3.6+
- Linux with desktop environment (GNOME, KDE, XFCE, etc.)
- AppImages with extraction support (`--appimage-extract`) (optional)

## Usage

### Basic Usage

Generate a desktop file with auto-detected information:
```bash
python3 appimage2desktop.py MyApp.AppImage
```

### Advanced Options

```bash
# Custom application name and description
python3 appimage2desktop.py MyApp.AppImage \
    --name "My Custom App" \
    --comment "A fantastic application for productivity"

# Specify custom output directory
python3 appimage2desktop.py MyApp.AppImage \
    --output-dir ~/.local/share/applications

# Set custom categories (follows freedesktop.org specification)
python3 appimage2desktop.py MyApp.AppImage \
    --categories "Graphics;Photography;Utility;"

# List available desktop directories
python3 appimage2desktop.py --list-dirs
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `appimage` | Path to the AppImage file (required) |
| `-n, --name` | Override application name |
| `-c, --comment` | Override application description |
| `--categories` | Set desktop categories (e.g., "Graphics;Utility;") |
| `-o, --output-dir` | Specify output directory for .desktop file |
| `--list-dirs` | List available desktop file directories |

## How It Works

1. **AppImage Analysis**: The tool extracts the AppImage contents temporarily using `--appimage-extract`
2. **Information Extraction**: Parses any existing `.desktop` files and extracts metadata
3. **Icon Processing**: Finds the best available icon and copies it to `~/.local/share/icons/`
4. **Desktop File Generation**: Creates a properly formatted `.desktop` file
5. **Integration**: Places the file in the appropriate directory where desktop environments look for applications

## Directory Structure

The tool uses the following directories:

- **Desktop Files**: 
  - `~/.local/share/applications/` (user applications, default)
  - `/usr/share/applications/` (system-wide, requires sudo)
  - `/usr/local/share/applications/` (local system-wide)

- **Icons**: 
  - `~/.local/share/icons/` (user icons)

## Examples

### Example 1: Basic Integration
```bash
$ python3 appimage2desktop.py Firefox.AppImage
Analyzing AppImage: Firefox.AppImage
✓ Desktop file created: /home/user/.local/share/applications/Firefox.desktop
✓ Success! Desktop file created at: /home/user/.local/share/applications/Firefox.desktop
The application should now appear in your application launcher.
```

### Example 2: Custom Configuration
```bash
$ python3 appimage2desktop.py MyApp.AppImage \
    --name "My Awesome App" \
    --comment "The best app ever created" \
    --categories "Utility;Development;"
    
Analyzing AppImage: MyApp.AppImage
✓ Desktop file created: /home/user/.local/share/applications/My-Awesome-App.desktop
✓ Success! Desktop file created at: /home/user/.local/share/applications/My-Awesome-App.desktop
The application should now appear in your application launcher.
```

### Example 3: Checking Available Directories
```bash
$ python3 appimage2desktop.py --list-dirs
Available desktop file directories:
  1. /home/user/.local/share/applications (exists: ✓, writable: ✓)
  2. /usr/share/applications (exists: ✓, writable: ✗)
  3. /usr/local/share/applications (exists: ✓, writable: ✗)
```

## Generated Desktop File Format

The tool generates desktop files following the [freedesktop.org Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html):

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=Application Name
Comment=Application description
Exec=/path/to/app.AppImage
Icon=/home/user/.local/share/icons/app-icon.png
Terminal=false
Categories=Application;Utility;
StartupNotify=true
```

## Troubleshooting

### AppImage Won't Extract
If you get extraction errors:
```bash
# Make sure the AppImage is executable
chmod +x MyApp.AppImage

# Test manual extraction
./MyApp.AppImage --appimage-extract
```

### Desktop File Not Appearing
- Refresh your desktop environment's application cache:
  ```bash
  # For GNOME
  sudo update-desktop-database ~/.local/share/applications/
  
  # For KDE
  kbuildsycoca5 --noincremental
  ```
- Log out and log back in
- Check if the desktop file was created in the correct location

### Permission Issues
For system-wide installation:
```bash
sudo python3 appimage2desktop.py MyApp.AppImage \
    --output-dir /usr/share/applications
```

## Supported Desktop Environments

This tool works with any desktop environment that follows the freedesktop.org standards, including:

- GNOME
- KDE Plasma
- XFCE
- MATE
- Cinnamon
- Elementary OS
- And many others

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
```bash
git clone https://github.com/homelabshq/appimage2desktop.git
cd appimage2desktop

# Run the script in development mode
python3 appimage2desktop.py --help
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [AppImage project](https://appimage.org/) for the portable application format
- [freedesktop.org](https://www.freedesktop.org/) for desktop integration standards
- The Linux desktop community for making application integration possible

## Related Projects

- [AppImageLauncher](https://github.com/TheAssassin/AppImageLauncher) - Full AppImage integration suite
- [appimaged](https://github.com/AppImage/appimaged) - Daemon for automatic AppImage integration
- [AppImageKit](https://github.com/AppImage/AppImageKit) - Tools for creating AppImages

---

⭐ If this tool helped you, please consider giving it a star on GitHub!
