import pygame
import os
import pyautogui
import tkinter as tk
from tkinter import ttk
import keyboard
import threading
import json
from time import time, sleep
from pynput import mouse

def is_pixel_red(x, y):
    try:
        pixel_color = pyautogui.pixel(x, y)
        return pixel_color[0] > 200 and pixel_color[1] < 50 and pixel_color[2] < 50
    except Exception:
        return False

def main_pixel_detection():
    pygame.mixer.init()
    screen_width, screen_height = pyautogui.size()
    middle_x = screen_width // 2
    middle_y = screen_height // 2
    script_dir = os.path.dirname(os.path.abspath(__file__))
    hitsound = os.path.join(script_dir, "hit.mp3")
    try:
        pygame.mixer.music.load(hitsound)
    except Exception:
        return
    canPlay = True
    try:
        while True:
            if is_pixel_red(middle_x, middle_y) and canPlay:
                try:
                    pygame.mixer.music.play()
                    canPlay = False
                    sleep(0.2)
                except Exception:
                    pass
            elif not is_pixel_red(middle_x, middle_y):
                if not canPlay:
                    canPlay = True
    except KeyboardInterrupt:
        pygame.mixer.quit()

class KeystrokeOverlay:
    def __init__(self, window):
        self.window = window
        self.window.title("Keystroke Overlay")
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_dir, "keystroke_config.json")
        self.config = self.load_config()
        initial_x = self.config.get("x", 10)
        initial_y = self.config.get("y", 10)
        self.enabled = self.config.get("enabled", True)
        self.window.geometry(f"210x270+{initial_x}+{initial_y}")
        self.window.wm_attributes('-transparentcolor', 'black')
        self.window.attributes('-topmost', True)
        self.window.overrideredirect(True)
        self.pressed_keys = set()
        self.create_ui()
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<Button-3>", self.toggle_visibility)
        self.drag_data = {"x": 0, "y": 0}
        self.start_keyboard_listener()
        self.update_visibility()

    def load_config(self):
        try:
            if not os.path.exists(self.config_path):
                default_config = {"x": 10, "y": 10, "enabled": True}
                with open(self.config_path, 'w') as f:
                    json.dump(default_config.default_config, f, indent=4)
                return default_config
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"x": 10, "y": 10, "enabled": True}

    def save_config(self):
        self.config["x"] = self.window.winfo_x()
        self.config["y"] = self.window.winfo_y()
        self.config["enabled"] = self.enabled
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except (IOError, PermissionError):
            pass

    def create_ui(self):
        self.canvas = tk.Canvas(self.window, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        key_size = 60
        padding = 15
        w_x, w_y = 105, 60
        self.w_rect = self.create_key_rect(w_x, w_y, key_size, 'W')
        a_x, a_y = w_x - key_size - padding, w_y + key_size + padding
        self.a_rect = self.create_key_rect(a_x, a_y, key_size, 'A')
        s_x, s_y = w_x, a_y
        self.s_rect = self.create_key_rect(s_x, s_y, key_size, 'S')
        d_x, d_y = w_x + key_size + padding, a_y
        self.d_rect = self.create_key_rect(d_x, d_y, key_size, 'D')
        space_width = 215
        space_height = 45
        space_y = a_y + key_size
        space_x = 105
        self.space_rect = self.create_space_rect(space_x, space_y, space_width, space_height)

    def create_key_rect(self, x, y, size, key_text):
        outline_color = "#555555"
        fill_color = "#333333"
        text_color = "#FFFFFF"
        rect_id = self.canvas.create_rectangle(
            x - size / 2, y - size / 2, x + size / 2, y + size / 2,
            fill=fill_color, outline=outline_color, width=2,
            tags=f"{key_text.lower()}_key"
        )
        text_id = self.canvas.create_text(
            x, y,
            text=key_text,
            font=("Arial", 18, "bold"),
            fill=text_color,
            tags=f"{key_text.lower()}_text"
        )
        return rect_id

    def create_space_rect(self, x, y, width, height):
        outline_color = "#555555"
        fill_color = "#333333"
        text_color = "#FFFFFF"
        rect_id = self.canvas.create_rectangle(
            x - width / 2, y - height / 2, x + width / 2, y + height / 2,
            fill=fill_color, outline=outline_color, width=2,
            tags="space_key"
        )
        text_id = self.canvas.create_text(
            x, y,
            text="SPACE",
            font=("Arial", 18, "bold"),
            fill=text_color,
            tags="space_text"
        )
        return rect_id

    def start_keyboard_listener(self):
        def on_key_event(e):
            if e.event_type == keyboard.KEY_DOWN:
                key = e.name.lower()
                if key in ['w', 'a', 's', 'd', 'space']:
                    if key not in self.pressed_keys:
                        self.pressed_keys.add(key)
                        self.update_key_visual(key, True)
            elif e.event_type == keyboard.KEY_UP:
                key = e.name.lower()
                if key in ['w', 'a', 's', 'd', 'space']:
                    if key in self.pressed_keys:
                        self.pressed_keys.remove(key)
                        self.update_key_visual(key, False)
        keyboard_thread = threading.Thread(target=lambda: keyboard.hook(on_key_event))
        keyboard_thread.daemon = True
        keyboard_thread.start()

    def update_key_visual(self, key, is_pressed):
        tag = f"{key}_key"
        if is_pressed:
            self.canvas.itemconfig(tag, fill="#4a86e8")
        else:
            self.canvas.itemconfig(tag, fill="#333333")

    def start_drag(self, event):
        self.drag_data["x"] = event.x_root - self.window.winfo_x()
        self.drag_data["y"] = event.y_root - self.window.winfo_y()

    def on_drag(self, event):
        x = event.x_root - self.drag_data["x"]
        y = event.y_root - self.drag_data["y"]
        self.window.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        self.save_config()

    def toggle_visibility(self, event):
        self.enabled = not self.enabled
        self.update_visibility()
        self.save_config()

    def update_visibility(self):
        if self.enabled:
            self.window.deiconify()
        else:
            self.window.withdraw()

class OverlayApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Overlay App")
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_dir, "packdisplay.json")
        self.config = self.load_config()
        self.enabled = self.config.get("enabled", True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.9)
        self.window.overrideredirect(True)
        x, y = self.config["x"], self.config["y"]
        self.frame = ttk.Frame(self.window, style="Overlay.TFrame")
        self.frame.pack(fill="both", expand=True)
        style = ttk.Style()
        style.configure("Overlay.TFrame", background="#212121")
        self.inner_frame = ttk.Frame(self.frame, style="Overlay.TFrame")
        self.inner_frame.pack(pady=10)
        try:
            self.pack_image = tk.PhotoImage(file=os.path.join(self.script_dir, "pack.png"))
            self.image_label = ttk.Label(self.inner_frame, image=self.pack_image, background="#212121")
            self.image_label.pack(side='left', padx=(0,5))
        except tk.TclError:
            pass
        self.text_label = ttk.Label(
            self.inner_frame,
            text="Qomic 16x (Mashup)",
            font=("Inter", 14),
            foreground="white",
            background="#212121"
        )
        self.text_label.pack(side='left')
        self.window.update_idletasks()
        req_width = self.frame.winfo_reqwidth()
        req_height = self.frame.winfo_reqheight()
        try:
            self.window.geometry(f"{req_width}x{req_height}+{int(x)}+{int(y)}")
        except (ValueError, tk.TclError):
            self.window.geometry(f"{req_width}x{req_height}+50+50")
        self.frame.bind("<Button-1>", self.start_drag)
        self.frame.bind("<B1-Motion>", self.on_drag)
        self.frame.bind("<ButtonRelease-1>", self.stop_drag)
        self.frame.bind("<Button-3>", self.toggle_visibility)
        self.inner_frame.bind("<Button-1>", self.start_drag)
        self.inner_frame.bind("<B1-Motion>", self.on_drag)
        self.inner_frame.bind("<ButtonRelease-1>", self.stop_drag)
        self.inner_frame.bind("<Button-3>", self.toggle_visibility)
        if hasattr(self, 'image_label'):
            self.image_label.bind("<Button-1>", self.start_drag)
            self.image_label.bind("<B1-Motion>", self.on_drag)
            self.image_label.bind("<ButtonRelease-1>", self.stop_drag)
            self.image_label.bind("<Button-3>", self.toggle_visibility)
        self.text_label.bind("<Button-1>", self.start_drag)
        self.text_label.bind("<B1-Motion>", self.on_drag)
        self.text_label.bind("<ButtonRelease-1>", self.stop_drag)
        self.text_label.bind("<Button-3>", self.toggle_visibility)
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.update_visibility()

    def load_config(self):
        try:
            if not os.path.exists(self.config_path):
                default_config = {"x": 50, "y": 50, "enabled segnali di trading": True}
                with open(self.config_path, "w") as f:
                    json.dump(default_config, f, indent=4)
                return default_config
            with open(self.config_path, "r") as f:
                data = json.load(f)
                return {"x": data.get("x", 50), "y": data.get("y", 50), "enabled": data.get("enabled", True)}
        except (json.JSONDecodeError, KeyError, IOError):
            return {"x": 50, "y": 50, "enabled": True}

    def save_config(self, x, y):
        data = {"x": x, "y": y, "enabled": self.enabled}
        try:
            with open(self.config_path, "w") as f:
                json.dump(data, f, indent=4)
        except (IOError, PermissionError):
            pass

    def start_drag(self, event):
        self.drag_start_x = event.x_root - self.window.winfo_x()
        self.drag_start_y = event.y_root - self.window.winfo_y()

    def on_drag(self, event):
        x = event.x_root - self.drag_start_x
        y = event.y_root - self.drag_start_y
        self.window.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        self.save_config(x, y)

    def toggle_visibility(self, event):
        self.enabled = not self.enabled
        self.update_visibility()
        self.save_config(self.window.winfo_x(), self.window.winfo_y())

    def update_visibility(self):
        if self.enabled:
            self.window.deiconify()
        else:
            self.window.withdraw()

class CPSOverlay:
    def __init__(self, window):
        self.window = window
        self.window.title("CPS Overlay")
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_dir, "config.json")
        self.config = self.load_config()
        self.enabled = self.config.get("enabled", True)
        initial_x = self.config.get("x", 0)
        initial_y = self.config.get("y", 0)
        try:
            self.window.geometry(f"140x40+{int(initial_x)}+{int(initial_y)}")
        except (ValueError, tk.TclError):
            self.window.geometry("140x40+0+0")
        self.window.attributes('-topmost', True)
        self.window.attributes('-alpha', 0.9)
        self.window.overrideredirect(True)
        self.left_click_times = []
        self.right_click_times = []
        self.left_cps = 0.0
        self.right_cps = 0.0
        self.canvas = tk.Canvas(self.window, bg='#212121', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.create_oval(0, 0, 28, 28, fill='#212121', outline='#212121')
        self.canvas.create_oval(152, 0, 180, 28, fill='#212121', outline='#212121')
        self.canvas.create_oval(0, 12, 28, 40, fill='#212121', outline='#212121')
        self.canvas.create_oval(152, 12, 180, 40, fill='#212121', outline='#212121')
        self.canvas.create_rectangle(14, 0, 166, 40, fill='#212121', outline='#212121')
        self.canvas.create_rectangle(0, 14, 180, 26, fill='#212121', outline='#212121')
        try:
            self.label = self.canvas.create_text(70, 20, text="CPS: 0-0", font=("Inter", 12, "bold"), fill="white")
        except tk.TclError:
            self.label = self.canvas.create_text(70, 20, text="CPS: 0-0", font=("Courier New", 12, "bold"), fill="white")
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<Button-3>", self.toggle_visibility)
        self.drag_data = {"x": 0, "y": 0}
        self.start_mouse_listener()
        self.update_cps()
        self.update_visibility()

    def load_config(self):
        try:
            if not os.path.exists(self.config_path):
                default_config = {"x": 0, "y": 0, "enabled": True}
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, PermissionError):
            return {"x": 0, "y": 0, "enabled": True}

    def save_config(self, x, y):
        self.config["x"] = x
        self.config["y"] = y
        self.config["enabled"] = self.enabled
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except (IOError, PermissionError):
            pass

    def start_mouse_listener(self):
        def on_click(x, y, button, pressed):
            if pressed:
                if button == mouse.Button.left:
                    self.left_click_times.append(time())
                elif button == mouse.Button.right:
                    self.right_click_times.append(time())
        listener = mouse.Listener(on_click=on_click)
        listener_thread = threading.Thread(target=listener.start, daemon=True)
        listener_thread.start()

    def start_drag(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_drag(self, event):
        x = event.x_root - self.drag_data["x"]
        y = event.y_root - self.drag_data["y"]
        self.window.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        x = self.window.winfo_x()
        y = self.window.winfo_y()
        self.save_config(x, y)
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0

    def update_cps(self):
        if self.enabled:
            current_time = time()
            self.left_click_times = [t for t in self.left_click_times if current_time - t <= 1.0]
            self.right_click_times = [t for t in self.right_click_times if current_time - t <= 1.0]
            self.left_cps = len(self.left_click_times) / 1.0 if self.left_click_times else 0.0
            self.right_cps = len(self.right_click_times) / 1.0 if self.right_click_times else 0.0
            cps_str = f"{int(self.left_cps)}-{int(self.right_cps)}"
            self.canvas.itemconfig(self.label, text=f"CPS: {cps_str}")
        self.window.after(10, self.update_cps)

    def toggle_visibility(self, event):
        self.enabled = not self.enabled
        self.update_visibility()
        self.save_config(self.window.winfo_x(), self.window.winfo_y())

    def update_visibility(self):
        if self.enabled:
            self.window.deiconify()
        else:
            self.window.withdraw()

def run_overlays():
    root = tk.Tk()
    root.withdraw()
    overlay_app_window = tk.Toplevel(root)
    overlay_app_window.attributes('-topmost', True)
    overlay_app = OverlayApp(overlay_app_window)
    cps_overlay_window = tk.Toplevel(root)
    cps_overlay_window.attributes('-topmost', True)
    cps_overlay = CPSOverlay(cps_overlay_window)
    keystroke_overlay_window = tk.Toplevel(root)
    keystroke_overlay_window.attributes('-topmost', True)
    keystroke_overlay = KeystrokeOverlay(keystroke_overlay_window)
    root.mainloop()

if __name__ == "__main__":
    key = input("Enter your key: ")
    if key == "oceanv1ontop":
        # Run pixel detection in a separate thread
        pixel_thread = threading.Thread(target=main_pixel_detection, daemon=True)
        pixel_thread.start()
        # Run overlays in the main thread
        run_overlays()
    else:
        print("Your key is invalid. Please get a key at discord.gg/PQdr94S2Ja")