import PyInstaller.__main__
import os
import sys

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.dirname(__file__))

# Define the path to your main.py file
main_script = os.path.join(project_root, 'main.py')

# Determine the appropriate separator for --add-data
separator = ';' if sys.platform.startswith('win') else ':'

PyInstaller.__main__.run([
    '--name=SEODataExtraction',
    '--windowed',
    '--onefile',
    f'--add-data=src{separator}src',
    f'--add-data=.env{separator}.',
    f'--add-data=src/config.py{separator}src',
    '--hidden-import=aiohttp',
    '--hidden-import=asyncio',
    '--hidden-import=bs4',
    '--hidden-import=urllib',
    '--hidden-import=gzip',
    '--hidden-import=io',
    '--hidden-import=PyQt6',
    '--noconsole',
    main_script
])