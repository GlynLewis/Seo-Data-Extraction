import os
import sys
import subprocess
import logging

# Set up logging
logging.basicConfig(filename='build.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def run_command(command):
    logging.info(f"Running command: {command}")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        logging.error(f"Command failed with return code {process.returncode}")
        logging.error(f"STDOUT:\n{stdout.decode()}")
        logging.error(f"STDERR:\n{stderr.decode()}")
        raise subprocess.CalledProcessError(process.returncode, command, stdout, stderr)
    return stdout.decode()

def build_windows():
    logging.info("Starting Windows build...")
    try:
        run_command("pyinstaller --name=SEODataExtraction --windowed --onefile --add-data src;src --add-data .env;. --add-data src/config.py;src main.py")
        logging.info("Windows build completed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Windows build failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # Change to the project root directory
        os.chdir(project_root)
        logging.info(f"Current working directory: {os.getcwd()}")
        logging.info(f"Contents of current directory: {os.listdir()}")
        
        if sys.platform.startswith('win'):
            build_windows()
        else:
            logging.error("This script is intended to run on Windows only.")
            sys.exit(1)

        logging.info("Build process completed successfully!")
    except Exception as e:
        logging.exception("An error occurred during the build process")
        sys.exit(1)