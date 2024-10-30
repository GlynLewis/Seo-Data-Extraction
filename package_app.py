import subprocess
import sys
import os
import shutil
import time

steps = [
    "Install PyInstaller",
    "Create spec file",
    "Edit spec file",
    "Build executable",
    "Test executable",
    "Create installer (optional)",
    "Prepare distribution package"
]

total_steps = len(steps)

def get_current_step():
    if os.path.exists('.packaging_step'):
        with open('.packaging_step', 'r') as f:
            return int(f.read().strip())
    return 0

def update_progress(step):
    progress = (step / total_steps) * 100
    print(f"Progress: [{'#' * int(progress / 2)}{' ' * (50 - int(progress / 2))}] {progress:.1f}%")
    print(f"Step {step}/{total_steps}: {steps[step - 1]}")
    with open('.packaging_step', 'w') as f:
        f.write(str(step))



def step1():
    print("Installing PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install PyInstaller. Please install it manually.")
    update_progress(1)

def step2():
    print("Creating spec file...")
    main_script = "main.py"  # Updated to use the new main.py location
    app_name = "SEODataExtraction"
    
    if not os.path.exists(main_script):
        print(f"Error: Main script '{main_script}' not found.")
        return

    try:
        subprocess.check_call([
            "pyi-makespec",
            "--name=" + app_name,
            "--windowed",
            "--add-data=src:src" if sys.platform != 'win32' else "--add-data=src;src",
            main_script
        ])
        print(f"Spec file '{app_name}.spec' created successfully.")
    except subprocess.CalledProcessError:
        print("Failed to create spec file. Please check your PyInstaller installation and try again.")
    update_progress(2)

def step3():
    print("Editing spec file...")
    spec_file = "SEODataExtraction.spec"
    
    if not os.path.exists(spec_file):
        print(f"Error: Spec file '{spec_file}' not found. Please run step 2 first.")
        return

    with open(spec_file, 'r') as f:
        content = f.read()

    # Add hidden imports
    hidden_imports = [
        'PyQt6', 'aiohttp', 'asyncio', 'pandas', 'bs4', 'lxml',
        'src.config', 'src.csv_handler', 'src.dataforseo_api',
        'src.web_scraper', 'src.main_processor'
    ]
    hidden_imports_str = ", ".join(f"'{imp}'" for imp in hidden_imports)
    content = content.replace(
        "hiddenimports=[]",
        f"hiddenimports=[{hidden_imports_str}]"
    )

    # Ensure all necessary data files are included
    data_files = [
        ('src', 'src'),
        ('data', 'data'),
        ('.env', '.'),
    ]
    data_files_str = ", ".join(f"('{src}', '{dst}')" for src, dst in data_files)
    content = content.replace(
        "datas=[]",
        f"datas=[{data_files_str}]"
    )

    with open(spec_file, 'w') as f:
        f.write(content)

    print(f"Spec file '{spec_file}' has been updated with hidden imports and data files.")
    update_progress(3)

def step4():
    print("Building executable...")
    
    try:
        if sys.platform == 'darwin':
            subprocess.check_call([sys.executable, "build_scripts/build_macos.py"])
        elif sys.platform.startswith('win'):
            subprocess.check_call([sys.executable, "build_scripts/build_windows.py"])
        else:
            print("Unsupported platform")
            return
        
        print("Executable built successfully.")
        
        # Check if the executable was created
        if sys.platform.startswith('win'):
            exe_path = os.path.join("dist", "SEODataExtraction.exe")
        else:
            exe_path = os.path.join("dist", "SEODataExtraction")
        
        if os.path.exists(exe_path):
            print(f"Executable created at: {exe_path}")
        else:
            print("Warning: Executable file not found in the expected location.")
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to build the executable. Error: {e}")
        print("Please check the output for errors.")
    update_progress(4)


def step5():
    print("Testing executable...")
    
    exe_path = os.path.join("dist", "SEODataExtraction", "SEODataExtraction")
    
    if not os.path.exists(exe_path):
        print(f"Error: Executable not found at {exe_path}")
        return

    print(f"Executable found at: {exe_path}")
    print("Attempting to run the executable...")

    try:
        # Run the executable and capture output
        process = subprocess.Popen(exe_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Increase timeout to 30 seconds
        timeout = 30
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                break
            time.sleep(1)
            print(".", end="", flush=True)
        
        if process.poll() is None:
            print("\nExecutable is still running after 30 seconds.")
            process.terminate()
        else:
            print("\nExecutable exited before the 30-second timeout.")

        stdout, stderr = process.communicate()
        
        print("\nStdout:")
        print(stdout)
        print("Stderr:")
        print(stderr)

        print("Please check if the application window appeared and functioned correctly.")
        user_input = input("Did the application window appear? (yes/no): ").lower()
        
        if user_input == 'yes':
            print("Test successful!")
        else:
            print("Test failed. The application window did not appear.")
            print("Checking for common macOS issues...")
            
            # Check for macOS-specific issues
            if "Qt internal error" in stderr:
                print("Qt internal error detected. This might be due to macOS security settings.")
                print("Try running 'xattr -cr dist/SEODataExtraction/SEODataExtraction' in the terminal and then run the test again.")
            
            if "This application failed to start because no Qt platform plugin could be initialized" in stderr:
                print("Qt platform plugin issue detected.")
                print("Make sure the PyQt6 plugins are correctly packaged with the application.")
                print("You may need to modify the .spec file to include the plugins explicitly.")

    except Exception as e:
        print(f"Error occurred while testing the executable: {str(e)}")

    update_progress(5)

def step6():
    print("Creating installer (optional)...")
    print("Note: This step is optional and depends on your specific requirements.")
    print("For macOS, you might want to create a DMG file.")
    print("For Windows, you could use tools like Inno Setup or NSIS.")
    
    choice = input("Do you want to create an installer? (yes/no): ").lower()
    if choice != 'yes':
        print("Skipping installer creation.")
        update_progress(6)
        return

    if sys.platform == 'darwin':  # macOS
        print("For macOS, you can create a DMG file using the 'create-dmg' tool.")
        print("Install it with: brew install create-dmg")
        print("Then run: create-dmg --volname 'SEO Data Extraction' --window-pos 200 120 --window-size 600 300 --icon-size 100 --icon 'SEODataExtraction.app' 200 150 --hide-extension 'SEODataExtraction.app' --app-drop-link 400 150 'SEODataExtraction.dmg' 'dist/SEODataExtraction/'")
    elif sys.platform.startswith('win'):  # Windows
        print("For Windows, you can use Inno Setup or NSIS to create an installer.")
        print("Please refer to their documentation for specific instructions.")

    print("Installer creation is a manual step. Please create the installer according to your needs.")
    input("Press Enter when you've completed creating the installer...")

    update_progress(6)

def step7():
    print("Preparing distribution package...")

    # Create a distribution directory
    dist_dir = "SEODataExtraction_dist"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

    # Copy the executable and necessary files
    shutil.copytree("dist/SEODataExtraction", os.path.join(dist_dir, "SEODataExtraction"))

    # Copy documentation
    shutil.copy("README.md", dist_dir)
    
    # Create a simple instruction file
    with open(os.path.join(dist_dir, "INSTRUCTIONS.txt"), "w") as f:
        f.write("SEO Data Extraction Tool\n")
        f.write("=========================\n\n")
        f.write("1. To run the application, double-click on the 'SEODataExtraction' executable.\n")
        f.write("2. Follow the on-screen instructions to use the tool.\n")
        f.write("3. For more detailed information, please refer to the README.md file.\n")

    print(f"Distribution package prepared in the '{dist_dir}' directory.")
    update_progress(7)

def run_step(step_number):
    if step_number == 1:
        step1()
    elif step_number == 2:
        step2()
    elif step_number == 3:
        step3()
    elif step_number == 4:
        step4()
    elif step_number == 5:
        step5()
    elif step_number == 6:
        step6()
    elif step_number == 7:
        step7()
    else:
        print(f"Invalid step number: {step_number}")

if __name__ == "__main__":
    print("Starting packaging process...")
    current_step = get_current_step()

    while True:
        print(f"\nCurrent step: {current_step + 1}")
        print("Available options:")
        print("1. Run the next step")
        print("2. Run a specific step")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            if current_step < total_steps:
                run_step(current_step + 1)
                current_step += 1
            else:
                print("All steps completed!")
        elif choice == '2':
            step_to_run = int(input(f"Enter the step number to run (1-{total_steps}): "))
            if 1 <= step_to_run <= total_steps:
                run_step(step_to_run)
                current_step = step_to_run
            else:
                print("Invalid step number.")
        elif choice == '3':
            print("Exiting the packaging process.")
            break
        else:
            print("Invalid choice. Please try again.")

    print("Packaging process completed!")