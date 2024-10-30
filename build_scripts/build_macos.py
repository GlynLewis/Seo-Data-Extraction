import PyInstaller.__main__
import os
import sys

def build_macos():
    # Get the absolute path to the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Define the path to your main.py file
    main_script = os.path.join(project_root, 'main.py')

    PyInstaller.__main__.run([
        '--name=SEODataExtraction',
        '--windowed',
        '--onefile',
        f'--add-data={os.path.join(project_root, "src")}:src',
        f'--add-data={os.path.join(project_root, ".env")}:.',
        f'--add-data={os.path.join(project_root, "src", "config.py")}:src',
        '--noconsole',
        main_script
    ])

if __name__ == "__main__":
    build_macos()