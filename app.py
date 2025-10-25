import configparser
import ctypes
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
import winreg
import os
import win32gui
import win32ui
import win32con
import subprocess
import shutil
from PIL import Image, ImageTk


if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.example.ProUninstaller")


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    full_path = os.path.join(base_path, relative_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource not found: {full_path}")
    return full_path

class ToolTip:
    def __init__(self, editor, widget, text):
        self.editor = editor
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.widget.bind("<Enter>", self.showtip)
        self.widget.bind("<Leave>", self.hidetip)

    def showtip(self, event=None):
        if self.tipwindow:
            return
        # Calculate position relative to the main window
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        self.ToolTip_label = tk.Label(
            tw,
            text=self.text,
            bg="#ffff00",       # 🟡 Bright yellow background
            fg="black",         # 🖤 Black text for contrast
            font=("Consolas", 11, "italic"),
            relief="solid",
            borderwidth=1,
            padx=6,
            pady=3
        )
        self.ToolTip_label.pack()

    def hidetip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None


# --- Extract icon from EXE/ICO with fallbacks ---
def extract_icon(icon_path, size=(32, 32)):
    try:
        if not icon_path or not os.path.exists(icon_path):
            return None
        large, small = win32gui.ExtractIconEx(icon_path, 0)
        if not large and not small:
            return None
        hicon = large[0] if large else small[0]
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, size[0], size[1])
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        win32gui.DrawIconEx(hdc.GetHandleOutput(), 0, 0, hicon, size[0], size[1], 0, None, win32con.DI_NORMAL)
        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer('RGBA', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRA', 0, 1)
        img = img.resize(size, Image.Resampling.LANCZOS)
        win32gui.DestroyIcon(hicon)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

# --- Fallback default icon (if app icon missing) ---
def get_default_icon(size=(32, 32)):
    img = Image.new("RGBA", size, (90, 90, 90, 255))
    return ImageTk.PhotoImage(img)

# --- Fetch installed apps ---
def get_installed_apps():
    apps = []
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"),
    ]
    for root, path in reg_paths:
        try:
            with winreg.OpenKey(root, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            values = {}
                            for j in range(winreg.QueryInfoKey(subkey)[1]):
                                k, v, _ = winreg.EnumValue(subkey, j)
                                values[k] = v
                            if "DisplayName" not in values:
                                continue
                            name = values.get("DisplayName", "")
                            icon_path = values.get("DisplayIcon", "")
                            install_location = values.get("InstallLocation", "")
                            uninstall_string = values.get("UninstallString", "")
                            size_val = values.get("EstimatedSize", "")
                            if isinstance(size_val, int):
                                size_val = f"{round(size_val / 1024, 2)} MB"
                            else:
                                size_val = "Unknown"

                            # clean icon path
                            if icon_path and "," in icon_path:
                                icon_path = icon_path.split(",")[0].strip('"')

                            # Try fallback EXE if missing
                            if not icon_path or not os.path.exists(icon_path):
                                if install_location and os.path.exists(install_location):
                                    for f in os.listdir(install_location):
                                        if f.lower().endswith(".exe"):
                                            icon_path = os.path.join(install_location, f)
                                            break

                            apps.append({
                                "name": name,
                                "icon": icon_path,
                                "size": size_val,
                                "location": install_location,
                                "uninstall_string": uninstall_string,
                                "reg_key": (root, path, subkey_name)
                            })
                    except Exception:
                        continue
        except Exception:
            continue
    apps.sort(key=lambda x: x["name"].lower())
    return apps

checked_state = {}
icons_cache = {}

def get_question_icon(size=(32, 32)):
    try:
        question_icon_path = resource_path(r"icons\\question_mark.png")
        if os.path.exists(question_icon_path):
            img = Image.open(question_icon_path).resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
    except Exception:
        pass
    # fallback to gray default if even question_mark.png missing
    return get_default_icon(size)

def load_apps():
    for item in tree.get_children():
        tree.delete(item)
    checked_state.clear()
    apps = get_installed_apps()
    for app in apps:
        icon_img = extract_icon(app["icon"]) if app["icon"] else None
        if not icon_img:
            icon_img = get_question_icon()  # ← show question_mark.png instead of gray box
        icons_cache[app["name"]] = icon_img
        item_id = tree.insert(
            "",
            "end",
            text="   " + app["name"],
            image=icon_img,
            values=(app["size"], "⬜", app["location"], app["uninstall_string"], app["reg_key"])
        )
        checked_state[item_id] = False
    update_check_column()

def update_check_column():
    for item_id, state in checked_state.items():
        tree.set(item_id, "Select", "✅" if state else "⬜")

def toggle_checkbox(event):
    row_id = tree.identify_row(event.y)
    if not row_id or not tree.exists(row_id):
        return
    checked_state[row_id] = not checked_state.get(row_id, False)
    tree.set(row_id, "Select", "✅" if checked_state[row_id] else "⬜")

# --- Uninstall selected apps ---
def uninstall_app():
    selected_items = [i for i, v in checked_state.items() if v and tree.exists(i)]
    if not selected_items:
        messagebox.showwarning("Warning", "Please select one or more applications to uninstall.")
        return

    selected_apps = []
    for item in selected_items:
        app_name = tree.item(item, "text").strip()
        values = tree.item(item, "values")
        selected_apps.append((item, app_name, values))

    app_names = [a[1] for a in selected_apps]
    confirm = messagebox.askyesno(
        "Confirm Uninstall",
        "You are about to uninstall the following apps:\n\n" + "\n".join(app_names) +
        "\n\nThis action cannot be undone!",
        icon='warning'
    )
    if not confirm:
        return

    for item, app_name, values in selected_apps:
        install_location = values[2]
        uninstall_string = values[3]
        reg_key = values[4]
        try:
            if uninstall_string:
                subprocess.run(uninstall_string, shell=True, check=False)
            root_key, path, subkey_name = eval(reg_key)
            try:
                with winreg.OpenKey(root_key, path, 0, winreg.KEY_ALL_ACCESS) as key:
                    winreg.DeleteKey(key, subkey_name)
            except Exception:
                pass
            if install_location and os.path.exists(install_location):
                shutil.rmtree(install_location, ignore_errors=True)
            if tree.exists(item):
                tree.delete(item)
                del checked_state[item]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to uninstall {app_name}: {e}")

    messagebox.showinfo("Done", "All selected applications were uninstalled successfully.")
    load_apps()

# --- Tooltip ---
tooltip_window = None
def show_tooltip_at_item(event):
    global tooltip_window
    row_id = tree.identify_row(event.y)
    if not row_id:
        hide_tooltip()
        return
    location = tree.set(row_id, "Location")
    if not location:
        hide_tooltip()
        return
    if tooltip_window:
        tooltip_window.destroy()
    tooltip_window = tk.Toplevel(root)
    tooltip_window.overrideredirect(True)
    tooltip_window.attributes("-topmost", True)
    label = tk.Label(
        tooltip_window,
        text=location,
        bg="#333333",
        fg="#ffffff",
        relief="solid",
        borderwidth=1,
        padx=5,
        pady=2,
        font=("Segoe UI", 9)
    )
    label.pack()
    tooltip_window.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

def hide_tooltip():
    global tooltip_window
    if tooltip_window:
        tooltip_window.destroy()
        tooltip_window = None


def save_window_geometry():
    config = configparser.ConfigParser()

    if os.path.exists(config_file):
        config.read(config_file)

    if not config.has_section("Geometry"):
        config.add_section("Geometry")
    config["Geometry"]["size"] = root.geometry()
    config["Geometry"]["state"] = root.state()

    with open(config_file, "w") as f:
        config.write(f)
        

def on_closing():
    save_window_geometry()
    root.destroy()

def load_window_geometry():

    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        if "Geometry" in config:
            geometry = config["Geometry"].get("size", "")
            state = config["Geometry"].get("state", "normal")

            if geometry:
                root.geometry(geometry)
                root.update_idletasks()
                root.update()

            if state == "zoomed":
                root.state("zoomed")
            elif state == "iconic": 
                root.iconify()
        
        
# --- UI ---
root = tb.Window(themename="darkly")
root.title("Applications Uninstaller")
root.geometry("1200x850")

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.SouRav.Chessai")

try:
    root.iconbitmap(resource_path(r"icons/icon.ico"))

except:
    pass
data_dir = os.path.join(os.path.expanduser("~"), ".ProUninstaller")
os.makedirs(data_dir, exist_ok=True)
config_file = os.path.join(data_dir, "config.ini")


frame = ttk.Frame(root)
frame.pack(fill="both", expand=True, padx=15, pady=15)

columns = ("Size", "Select", "Location", "UninstallString", "RegKey")
tree = ttk.Treeview(frame, columns=columns, show="tree headings")
tree.heading("#0", text="Application Name", anchor="center")
tree.heading("Size", text="Size", anchor="center")
tree.heading("Select", text="Select", anchor="center")
tree.column("#0", width=400)
tree.column("Size", width=120, anchor="center")
tree.column("Select", width=100, anchor="center")
tree.column("Location", width=0, stretch=False)
tree.column("UninstallString", width=0, stretch=False)
tree.column("RegKey", width=0, stretch=False)

style = tb.Style()
style.configure("mystyle.Treeview", rowheight=50, font=("Segoe UI", 13))
tree.configure(style="mystyle.Treeview")

vsb = tb.Scrollbar(frame, bootstyle="round", orient="vertical", command=tree.yview)
tree.configure(yscroll=vsb.set)
vsb.pack(side="right", fill="y")
tree.pack(fill="both", expand=True)

def on_enter(e): vsb.configure(bootstyle="round,primary")
def on_leave(e): vsb.configure(bootstyle="round")
vsb.bind("<Enter>", on_enter)
vsb.bind("<Leave>", on_leave)

tree.bind("<Button-1>", toggle_checkbox)
tree.bind("<Motion>", show_tooltip_at_item)
tree.bind("<Leave>", lambda e: hide_tooltip())

# --- Buttons ---
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

refresh_icon = ImageTk.PhotoImage(Image.open(resource_path(r"icons\\refresh.png")).resize((25, 25)))
refresh_btn = tb.Button(button_frame, image=refresh_icon, command=load_apps, bootstyle="primary")
refresh_btn.pack(side="left", padx=30)
ToolTip(None, refresh_btn, "Refresh the list")

uninstall_icon = ImageTk.PhotoImage(Image.open(resource_path(r"icons\\uninstall.png")).resize((20, 20)))
uninstall_btn = tb.Button(button_frame, image=uninstall_icon, text=" Uninstall", compound="left",
                          command=uninstall_app, bootstyle="danger")
uninstall_btn.pack(side="left", padx=5)
ToolTip(None, uninstall_btn, "Uninstall selected applications")

warning_label = tb.Label(root,
                        text="⚠️ WARNING: Uninstalling will delete files and registry entries. Use with caution!",
                        foreground="red",
                        font=("Segoe UI", 10, "bold"),
                        background=root.cget("bg"))
warning_label.pack(pady=10)

load_window_geometry()
load_apps()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
