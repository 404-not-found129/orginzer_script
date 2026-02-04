import os
import shutil
import tkinter as tk
from tkinter import scrolledtext, ttk
import sys

# --- CONFIGURATION ---
user_home = os.path.expanduser("~")
source_dir = os.path.join(user_home, "Downloads")

dest_dirs = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".ico", ".svg"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".webm"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
    "Installers": [".exe", ".msi", ".bat"],
    "System_DLLs": [".dll", ".sys", ".ini", ".cfg", ".log", ".asi"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".html", ".css", ".json", ".lua"]
}

# --- THEME COLORS ---
COLOR_BG = "#1e1e1e"        # Dark Gray Background
COLOR_FG = "#ffffff"        # White Text
COLOR_ACCENT = "#007acc"    # Blue Accent
COLOR_BTN_START = "#2ea043" # Green
COLOR_BTN_STOP = "#da3633"  # Red
COLOR_LOG_BG = "#0d1117"    # Almost Black
COLOR_LOG_FG = "#58a6ff"    # Terminal Blue/Green

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
        self.root.title("Downloads Organizer Pro")
        self.root.geometry("600x450")
        self.root.configure(bg=COLOR_BG)

        # --- HEADER ---
        header_frame = tk.Frame(root, bg=COLOR_BG)
        header_frame.pack(pady=(20, 10), fill=tk.X)

        self.title_label = tk.Label(
            header_frame,
            text="AUTO-ORGANIZER",
            font=("Segoe UI", 18, "bold"),
            bg=COLOR_BG,
            fg=COLOR_FG
        )
        self.title_label.pack()

        self.status_label = tk.Label(
            header_frame,
            text="STATUS: STOPPED",
            font=("Consolas", 10),
            bg=COLOR_BG,
            fg=COLOR_BTN_STOP
        )
        self.status_label.pack(pady=5)

        # --- CONTROLS ---
        btn_frame = tk.Frame(root, bg=COLOR_BG)
        btn_frame.pack(pady=10)

        # Custom styled buttons using standard tk for color control
        self.start_btn = tk.Button(
            btn_frame,
            text="▶ START WATCHING",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_BTN_START,
            fg="white",
            activebackground="#268a3b",
            activeforeground="white",
            relief="flat",
            padx=15, pady=8,
            cursor="hand2",
            command=self.start_watching
        )
        self.start_btn.pack(side=tk.LEFT, padx=10)

        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹ STOP",
            font=("Segoe UI", 10, "bold"),
            bg="#30363d",  # Dimmed when disabled
            fg="white",
            relief="flat",
            padx=15, pady=8,
            state="disabled",
            command=self.stop_watching
        )
        self.stop_btn.pack(side=tk.LEFT, padx=10)

        # --- LOG TERMINAL ---
        log_label = tk.Label(root, text="ACTIVITY LOG", font=("Segoe UI", 9, "bold"), bg=COLOR_BG, fg="#8b949e")
        log_label.pack(pady=(20, 5), anchor="w", padx=20)

        self.log_area = scrolledtext.ScrolledText(
            root,
            width=70,
            height=12,
            bg=COLOR_LOG_BG,
            fg=COLOR_LOG_FG,
            insertbackground="white", # cursor color
            font=("Consolas", 9),
            relief="flat",
            state="disabled"
        )
        self.log_area.pack(pady=(0, 20), padx=20, fill=tk.BOTH, expand=True)

        # --- LOGIC VARIABLES ---
        self.running = False
        self.poll_ms = 1000
        self._seen = set()
        self._after_id = None

        # Initial scan to ignore existing files
        self._prime_seen()

    def _prime_seen(self):
        try:
            if os.path.exists(source_dir):
                with os.scandir(source_dir) as entries:
                    for entry in entries:
                        if entry.is_file():
                            self._seen.add(entry.name)
        except Exception:
            pass

    def log_message(self, message: str, color=None):
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"> {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")

    def start_watching(self):
        if self.running: return

        self.running = True
        self.status_label.config(text="STATUS: RUNNING", fg=COLOR_BTN_START)

        # Update Button Styles
        self.start_btn.config(state="disabled", bg="#30363d")
        self.stop_btn.config(state="normal", bg=COLOR_BTN_STOP, cursor="hand2", activebackground="#b62a28")

        self.log_message(f"Monitoring started for: {source_dir}")
        self._schedule_poll()

    def stop_watching(self):
        if not self.running: return

        self.running = False
        if self._after_id:
            self.root.after_cancel(self._after_id)
            self._after_id = None

        self.status_label.config(text="STATUS: STOPPED", fg=COLOR_BTN_STOP)

        # Reset Button Styles
        self.start_btn.config(state="normal", bg=COLOR_BTN_START)
        self.stop_btn.config(state="disabled", bg="#30363d", cursor="arrow")

        self.log_message("Monitoring stopped.")

    def _schedule_poll(self):
        self._after_id = self.root.after(self.poll_ms, self._poll_once)

    def _poll_once(self):
        if not self.running: return

        try:
            if not os.path.exists(source_dir):
                self.log_message(f"Source dir not found: {source_dir}")
                self._schedule_poll()
                return

            with os.scandir(source_dir) as entries:
                for entry in entries:
                    if not entry.is_file(): continue

                    # If it's a new file (not in seen set)
                    if entry.name not in self._seen:
                        # Add to seen immediately to prevent double processing
                        self._seen.add(entry.name)
                        self._maybe_move(entry.path, entry.name)

        except Exception as e:
            self.log_message(f"Scan error: {e}")

        self._schedule_poll()

    def _maybe_move(self, path: str, filename: str):
        # Safety: Don't move the script itself
        if filename == os.path.basename(__file__) or filename.endswith(".exe"):
            return

        file_ext = os.path.splitext(filename)[1].lower()

        for folder_name, extensions in dest_dirs.items():
            if file_ext in extensions:
                folder_path = os.path.join(source_dir, folder_name)
                os.makedirs(folder_path, exist_ok=True)

                dest = unique_destination(folder_path, filename)

                try:
                    # Wait a tiny bit for large downloads to finish writing?
                    # For simple logic, we just try move.
                    shutil.move(path, dest)
                    self.log_message(f"MOVED: {filename} -> {folder_name}")
                except Exception as e:
                    self.log_message(f"Error moving {filename}: {e}")

                return

if __name__ == "__main__":
    try:
        # High DPI fix for Windows
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    root = tk.Tk()
    app = OrganizerApp(root)
    root.mainloop()