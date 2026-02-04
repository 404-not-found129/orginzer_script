import os
import shutil
import tkinter as tk
from tkinter import scrolledtext

# --- CONFIGURATION ---
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


def unique_destination(folder_path: str, filename: str) -> str:
    """Return a non-colliding destination path inside folder_path."""
    destination = os.path.join(folder_path, filename)
    if not os.path.exists(destination):
        return destination

    base, ext = os.path.splitext(filename)
    counter = 1
    while True:
        candidate = os.path.join(folder_path, f"{base}_{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


class OrganizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Downloads Organizer")
        self.root.geometry("520x420")

        # Title Label
        self.label = tk.Label(
            root,
            text="Folder Watcher: STOPPED",
            font=("Arial", 14, "bold"),
            fg="red"
        )
        self.label.pack(pady=10)

        # Buttons
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=5)

        self.start_btn = tk.Button(
            self.btn_frame,
            text="START WATCHING",
            bg="green",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.start_watching
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(
            self.btn_frame,
            text="STOP",
            bg="red",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.stop_watching,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        # Log Area
        tk.Label(root, text="Activity Log:", font=("Arial", 10)).pack(pady=(15, 0))
        self.log_area = scrolledtext.ScrolledText(root, width=60, height=16, state="disabled")
        self.log_area.pack(pady=5)

        # Watch variables
        self.running = False
        self.poll_ms = 800  # how often to scan Downloads
        self._seen = set()
        self._after_id = None

        # Prime seen set so we don't reorganize old files immediately
        self._prime_seen()

    def _prime_seen(self):
        try:
            with os.scandir(source_dir) as entries:
                for entry in entries:
                    if entry.is_file():
                        self._seen.add(entry.name)
        except FileNotFoundError:
            # Downloads folder missing/unusual profile; keep seen empty
            pass

    def log_message(self, message: str):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def start_watching(self):
        if self.running:
            return

        self.running = True
        self.label.config(text="Folder Watcher: RUNNING", fg="green")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log_message(f"--- Started Watching: {source_dir} ---")

        self._schedule_poll()

    def stop_watching(self):
        if not self.running:
            return

        self.running = False
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

        self.label.config(text="Folder Watcher: STOPPED", fg="red")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log_message("--- Stopped Watching ---")

    def _schedule_poll(self):
        self._after_id = self.root.after(self.poll_ms, self._poll_once)

    def _poll_once(self):
        if not self.running:
            return

        try:
            with os.scandir(source_dir) as entries:
                for entry in entries:
                    if not entry.is_file():
                        continue

                    # Skip files we already processed/observed
                    if entry.name in self._seen:
                        continue

                    self._seen.add(entry.name)
                    self._maybe_move(entry.path, entry.name)

        except FileNotFoundError:
            self.log_message(f"Error: Source directory not found: {source_dir}")
        except PermissionError as e:
            self.log_message(f"Error: Permission issue scanning folder: {e}")
        except Exception as e:
            self.log_message(f"Error: Unexpected scan error: {e}")

        self._schedule_poll()

    def _maybe_move(self, path: str, filename: str):
        # Don't move the script itself
        try:
            script_name = os.path.basename(__file__)
            if filename == script_name:
                return
        except Exception:
            pass

        file_ext = os.path.splitext(filename)[1].lower()

        for folder_name, extensions in dest_dirs.items():
            if file_ext not in extensions:
                continue

            folder_path = os.path.join(source_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            destination = unique_destination(folder_path, filename)

            try:
                shutil.move(path, destination)
                msg = f"Moved: {filename} -> {folder_name}"
                print(msg)
                self.log_message(msg)
            except Exception as e:
                self.log_message(f"Error moving {filename}: {e}")
            return  # stop after first matching category


if __name__ == "__main__":
    root = tk.Tk()
    app = OrganizerApp(root)
    root.mainloop()

## 1. What This Script Does
This tool acts as a background "janitor" for your Downloads folder. Instead of letting files pile up, this script watches the folder in real-time.

**When you download a file, it automatically moves it:**
* **Images** (`.jpg`, `.png`, etc.) → Moves to a `Downloaded Images` folder.
* **Docs** (`.pdf`, `.docx`, etc.) → Moves to a `Downloaded Docs` folder.
* **Installers** (`.exe`, `.msi`) → Moves to a `Downloaded Software` folder.
* **Zips** (`.zip`, `.rar`) → Moves to a `Downloaded Zips` folder.

**Safety Feature:** If a file with the same name already exists, this script will NOT overwrite it. It renames the new file (e.g., `image_1.png`) to keep your data safe.

---

## 2. Requirements (Before You Run)
You must have Python installed. You also need to install one external library called `watchdog` that allows the code to "watch" folders.

**How to install the library:**
1. Open PyCharm.
2. Click the **"Terminal"** tab at the bottom of the screen.
3. Type the following command and hit Enter:
   `pip install watchdog`

---

## 3. How to Run the Script
1. Open the file `organizer.py` in PyCharm.
2. Look for the line that says `source_dir`. **Make sure this path points to your actual Downloads folder.**
   * *Example:* `C:/Users/your name/Downloads`
3. Right-click anywhere in the code editor and select **"Run 'file at the top of the page'"**.
4. You will see a message in the console: *"Running... Watching for new files."*
5. **Test it:** Download an image from Google Images. Watch it magically disappear from Downloads and appear in the `Downloaded Images` folder!

**Note:** The script needs to stay running to work. To stop it, just press the red "Stop" square in PyCharm.
