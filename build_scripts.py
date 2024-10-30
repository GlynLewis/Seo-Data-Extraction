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
    f'--add-data=.env{separator}.' if os.path.exists('.env') else '',
    f'--add-data=src/config.py{separator}src',
    '--noconsole',
    '--hidden-import=PyQt6',
    '--hidden-import=aiohttp',
    '--hidden-import=asyncio',
    '--hidden-import=pandas',
    '--hidden-import=bs4',
    '--hidden-import=lxml',
    main_script
])