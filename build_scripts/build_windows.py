import PyInstaller.__main__
import os

def build_windows():
    project_root = os.path.abspath(os.path.dirname(__file__))
    main_script = os.path.join(project_root, 'main.py')

    PyInstaller.__main__.run([
        '--name=SEODataExtraction',
        '--windowed',
        '--onefile',
        '--add-data=src;src',
        '--add-data=.env;.',
        '--add-data=src/config.py;src',
        '--noconsole',
        main_script
    ])

if __name__ == "__main__":
    build_windows()