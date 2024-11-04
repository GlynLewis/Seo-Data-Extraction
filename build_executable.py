import PyInstaller.__main__
import os
import sys
import shutil

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.dirname(__file__))

# Define the path to your main.py file
main_script = os.path.join(project_root, 'main.py')

# Determine the appropriate separator for --add-data
separator = ';' if sys.platform.startswith('win') else ':'

# Build the executable
PyInstaller.__main__.run([
    '--name=SEODataExtraction',
    '--windowed',
    '--onefile',
    f'--add-data=src{separator}src',
    '--hidden-import=aiohttp',
    '--hidden-import=asyncio',
    '--hidden-import=bs4',
    '--hidden-import=urllib',
    '--hidden-import=gzip',
    '--hidden-import=io',
    '--hidden-import=PyQt6',
    '--hidden-import=pandas',
    '--hidden-import=beautifulsoup4',
    '--hidden-import=src.constants',
    '--hidden-import=src.csv_handler',
    '--hidden-import=src.utils',
    '--hidden-import=src.gui.main_window',
    '--hidden-import=src.gui.worker',
    '--hidden-import=src.gui.utils',
    '--collect-all=PyQt6',
    '--noconsole',
    '--version-file=file_version_info.txt',
    main_script
])

# Copy app_config.json to dist directory
config_src = os.path.join(project_root, 'app_config.json')
config_dst = os.path.join(project_root, 'dist', 'app_config.json')
shutil.copy2(config_src, config_dst)
print(f"\nCopied {config_src} to {config_dst}")
