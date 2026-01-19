# 📂 Automatic Downloads Organizer

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
