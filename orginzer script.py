import os
import shutil
import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION ---
# Set this to True to make the script run automatically when Windows starts.
# Set to False if you want to run it manually only.
ENABLE_STARTUP_ON_BOOT = True

# --- AUTO-DETECT PATH ---
user_home = os.path.expanduser("~")
source_dir = os.path.join(user_home, "Downloads")

dest_dirs = {
    "Downloaded Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".ico", ".svg"],
    "Downloaded Videos": [".mp4", ".mkv", ".mov", ".avi", ".webm"],
    "Downloaded Docs": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
    "Downloaded Installers": [".exe", ".msi", ".bat"],
    "System & DLLs": [".dll", ".sys", ".ini", ".cfg", ".log", ".asi"],
    "Downloaded Zips": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Downloaded Code": [".py", ".js", ".html", ".css", ".json", ".lua"]
}

def setup_startup():
    """Creates a batch file in the Windows Startup folder to run this script automatically."""
    try:
        # 1. Get the path to the startup folder
        startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        bat_path = os.path.join(startup_folder, "start_organizer.bat")

        # 2. Check if already installed
        if os.path.exists(bat_path):
            return # Already set up, nothing to do

        # 3. Create the batch file pointing to this script
        # We use pythonw.exe instead of python.exe so it runs in the background (no black window)
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        script_path = os.path.abspath(__file__)

        with open(bat_path, "w") as bat_file:
            bat_file.write(f'"{python_exe}" "{script_path}"')

        print(f"SUCCESS: Added to Windows Startup folder.\nLocation: {bat_path}")

    except Exception as e:
        print(f"Could not set up startup: {e}")

class MoverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        with os.scandir(source_dir) as entries:
            for entry in entries:
                if entry.is_file():
                    self.move_file(entry)

    def move_file(self, entry):
        if entry.name == os.path.basename(__file__): return

        file_ext = os.path.splitext(entry.name)[1].lower()
        for folder_name, extensions in dest_dirs.items():
            if file_ext in extensions:
                folder_path = os.path.join(source_dir, folder_name)
                os.makedirs(folder_path, exist_ok=True)

                destination = os.path.join(folder_path, entry.name)
                if os.path.exists(destination):
                    base, ext = os.path.splitext(entry.name)
                    counter = 1
                    while os.path.exists(os.path.join(folder_path, f"{base}_{counter}{ext}")):
                        counter += 1
                    destination = os.path.join(folder_path, f"{base}_{counter}{ext}")

                try:
                    shutil.move(entry.path, destination)
                    print(f"Moved: {entry.name} -> {folder_name}")
                except Exception as e:
                    print(f"Error moving {entry.name}: {e}")

if __name__ == "__main__":
    if ENABLE_STARTUP_ON_BOOT:
        setup_startup()

    print(f"Running... Watching: {source_dir}")
    print("Press Ctrl+C to stop manually.")

    observer = Observer()
    event_handler = MoverHandler()
    observer.schedule(event_handler, source_dir, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()