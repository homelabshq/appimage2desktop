#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import re

class AppImageDesktopGenerator:
    def __init__(self):
        self.desktop_dirs = [
            Path.home() / ".local/share/applications",  # User applications
            Path("/usr/share/applications"),             # System applications (requires sudo)
            Path("/usr/local/share/applications")       # Local system applications
        ]
    
    def extract_appimage_info(self, appimage_path):
        """Extract information from AppImage using --appimage-extract-and-run"""
        appimage_path = Path(appimage_path).resolve()
        
        if not appimage_path.exists():
            raise FileNotFoundError(f"AppImage not found: {appimage_path}")
        
        if not appimage_path.is_file():
            raise ValueError(f"Path is not a file: {appimage_path}")
        
        # Make AppImage executable
        os.chmod(appimage_path, 0o755)
        
        info = {
            'name': appimage_path.stem,
            'exec': str(appimage_path),
            'icon': None,
            'comment': '',
            'categories': 'Application;'
        }
        
        # Try to extract desktop file and icon from AppImage
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Extract AppImage contents
                result = subprocess.run(
                    [str(appimage_path), '--appimage-extract'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    squashfs_root = Path(temp_dir) / "squashfs-root"
                    if squashfs_root.exists():
                        info.update(self._parse_extracted_content(squashfs_root, appimage_path))
                        
            except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                print(f"Warning: Could not extract AppImage info: {e}")
        
        return info
    
    def _parse_extracted_content(self, squashfs_root, appimage_path):
        """Parse extracted AppImage content for desktop file and icon"""
        info = {}
        
        # Look for .desktop files
        desktop_files = list(squashfs_root.glob("*.desktop"))
        if not desktop_files:
            desktop_files = list(squashfs_root.glob("**/*.desktop"))
        
        if desktop_files:
            desktop_file = desktop_files[0]  # Use the first one found
            desktop_info = self._parse_desktop_file(desktop_file)
            info.update(desktop_info)
        
        # Look for icon files
        icon_extensions = ['.png', '.svg', '.xpm', '.ico']
        icon_files = []
        
        for ext in icon_extensions:
            icon_files.extend(squashfs_root.glob(f"**/*{ext}"))
        
        if icon_files:
            # Try to find the best icon (prefer larger sizes or main app icon)
            best_icon = self._select_best_icon(icon_files, info.get('name', ''))
            if best_icon:
                # Copy icon to a permanent location
                icon_dest = self._copy_icon(best_icon, appimage_path.stem)
                if icon_dest:
                    info['icon'] = str(icon_dest)
        
        return info
    
    def _parse_desktop_file(self, desktop_file_path):
        """Parse a .desktop file and extract relevant information"""
        info = {}
        
        try:
            with open(desktop_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple parser for .desktop files
            for line in content.split('\n'):
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Name':
                        info['name'] = value
                    elif key == 'Comment':
                        info['comment'] = value
                    elif key == 'Categories':
                        info['categories'] = value
                    elif key == 'Icon':
                        info['icon_name'] = value
                        
        except Exception as e:
            print(f"Warning: Could not parse desktop file {desktop_file_path}: {e}")
        
        return info
    
    def _select_best_icon(self, icon_files, app_name):
        """Select the best icon from available options"""
        if not icon_files:
            return None
        
        # Prefer PNG files
        png_icons = [f for f in icon_files if f.suffix.lower() == '.png']
        if png_icons:
            icon_files = png_icons
        
        # Try to find icon with app name in filename
        app_name_lower = app_name.lower()
        name_matches = [f for f in icon_files if app_name_lower in f.name.lower()]
        if name_matches:
            return name_matches[0]
        
        # Look for common icon names
        common_names = ['icon', 'logo', 'app', 'main']
        for common in common_names:
            matches = [f for f in icon_files if common in f.name.lower()]
            if matches:
                return matches[0]
        
        # Return the first available icon
        return icon_files[0]
    
    def _copy_icon(self, icon_path, app_name):
        """Copy icon to user's icon directory"""
        icon_dir = Path.home() / ".local/share/icons"
        icon_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a unique filename
        icon_dest = icon_dir / f"{app_name}{icon_path.suffix}"
        
        try:
            shutil.copy2(icon_path, icon_dest)
            return icon_dest
        except Exception as e:
            print(f"Warning: Could not copy icon: {e}")
            return None
    
    def create_desktop_file(self, appimage_path, output_dir=None, name=None, comment=None, categories=None):
        """Create a .desktop file for the AppImage"""
        
        # Extract AppImage information
        print(f"Analyzing AppImage: {appimage_path}")
        info = self.extract_appimage_info(appimage_path)
        
        # Override with user-provided values
        if name:
            info['name'] = name
        if comment:
            info['comment'] = comment
        if categories:
            info['categories'] = categories
        
        # Determine output directory
        if output_dir:
            desktop_dir = Path(output_dir)
        else:
            desktop_dir = self.desktop_dirs[0]  # Default to user applications
        
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        # Create desktop file content
        desktop_content = self._generate_desktop_content(info)
        
        # Write desktop file
        desktop_filename = f"{self._sanitize_filename(info['name'])}.desktop"
        desktop_path = desktop_dir / desktop_filename
        
        try:
            with open(desktop_path, 'w', encoding='utf-8') as f:
                f.write(desktop_content)
            
            # Make desktop file executable
            os.chmod(desktop_path, 0o755)
            
            print(f"✓ Desktop file created: {desktop_path}")
            return desktop_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to create desktop file: {e}")
    
    def _generate_desktop_content(self, info):
        """Generate .desktop file content"""
        icon_line = f"Icon={info['icon']}\n" if info.get('icon') else ""
        
        content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={info['name']}
Comment={info['comment']}
Exec={info['exec']}
{icon_line}Terminal=false
Categories={info['categories']}
StartupNotify=true
"""
        return content
    
    def _sanitize_filename(self, filename):
        """Sanitize filename for use in filesystem"""
        # Remove or replace invalid characters
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = re.sub(r'[-\s]+', '-', filename)
        return filename.strip('-')
    
    def list_desktop_directories(self):
        """List available desktop file directories"""
        print("Available desktop file directories:")
        for i, directory in enumerate(self.desktop_dirs, 1):
            exists = "✓" if directory.exists() else "✗"
            writable = "✓" if directory.exists() and os.access(directory, os.W_OK) else "✗"
            print(f"  {i}. {directory} (exists: {exists}, writable: {writable})")

def main():
    parser = argparse.ArgumentParser(
        description="Generate .desktop files for AppImages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s MyApp.AppImage
  %(prog)s MyApp.AppImage --name "My Application" --comment "A great app"
  %(prog)s MyApp.AppImage --output-dir ~/.local/share/applications
  %(prog)s --list-dirs
        """
    )
    
    parser.add_argument('appimage', nargs='?', help='Path to the AppImage file')
    parser.add_argument('-o', '--output-dir', help='Output directory for .desktop file')
    parser.add_argument('-n', '--name', help='Application name (overrides extracted name)')
    parser.add_argument('-c', '--comment', help='Application comment/description')
    parser.add_argument('--categories', help='Desktop categories (e.g., "Graphics;Photography;")')
    parser.add_argument('--list-dirs', action='store_true', help='List available desktop directories')
    
    args = parser.parse_args()
    
    generator = AppImageDesktopGenerator()
    
    if args.list_dirs:
        generator.list_desktop_directories()
        return
    
    if not args.appimage:
        parser.error("AppImage path is required (or use --list-dirs)")
    
    try:
        desktop_path = generator.create_desktop_file(
            args.appimage,
            output_dir=args.output_dir,
            name=args.name,
            comment=args.comment,
            categories=args.categories
        )
        
        print(f"\n✓ Success! Desktop file created at: {desktop_path}")
        print("The application should now appear in your application launcher.")
        
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
