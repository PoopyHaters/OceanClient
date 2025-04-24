import tkinter as tk
from tkinter import ttk
import json
import os
from time import time
from pynput import mouse
import threading

key = input("Enter your key: ")

class OverlayApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Overlay App")
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_dir, "packdisplay.json")
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.9)
        self.window.overrideredirect(True)
        config = self.load_config()
        x, y = config["x"], config["y"]
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
            pass  # Image not found, proceed without it
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
        self.inner_frame.bind("<Button-1>", self.start_drag)
        self.inner_frame.bind("<B1-Motion>", self.on_drag)
        self.inner_frame.bind("<ButtonRelease-1>", self.stop_drag)
        if hasattr(self, 'image_label'):
            self.image_label.bind("<Button-1>", self.start_drag)
            self.image_label.bind("<B1-Motion>", self.on_drag)
            self.image_label.bind("<ButtonRelease-1>", self.stop_drag)
        self.text_label.bind("<Button-1>", self.start_drag)
        self.text_label.bind("<B1-Motion>", self.on_drag)
        self.text_label.bind("<ButtonRelease-1>", self.stop_drag)
        self.drag_start_x = 0
        self.drag_start_y = 0

    def load_config(self):
        try:
            if not os.path.exists(self.config_path):
                return {"x": 50, "y": 50}
            with open(self.config_path, "r") as f:
                data = json.load(f)
                return {"x": data.get("x", 50), "y": data.get("y", 50)}
        except (json.JSONDecodeError, KeyError, IOError):
            return {"x": 50, "y": 50}

    def save_config(self, x, y):
        data = {"x": x, "y": y}
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

class CPSOverlay:
    def __init__(self, window):
        self.window = window
        self.window.title("CPS Overlay")
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_dir, "config.json")
        self.config = self.load_config()
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
        self.drag_data = {"x": 0, "y": 0}
        self.canvas.bind("<Button-2>", lambda e: self.reset())
        self.start_mouse_listener()
        self.update_cps()

    def load_config(self):
        try:
            if not os.path.exists(self.config_path):
                default_config = {"x": 0, "y": 0}
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, PermissionError):
            return {"x": 0, "y": 0}

    def save_config(self, x, y):
        self.config["x"] = x
        self.config["y"] = y
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
        current_time = time()
        self.left_click_times = [t for t in self.left_click_times if current_time - t <= 1.0]
        self.right_click_times = [t for t in self.right_click_times if current_time - t <= 1.0]
        self.left_cps = len(self.left_click_times) / 1.0 if self.left_click_times else 0.0
        self.right_cps = len(self.right_click_times) / 1.0 if self.right_click_times else 0.0
        cps_str = f"{int(self.left_cps)}-{int(self.right_cps)}"
        self.canvas.itemconfig(self.label, text=f"CPS: {cps_str}")
        self.window.after(10, self.update_cps)

    def reset(self):
        self.left_click_times = []
        self.right_click_times = []
        self.left_cps = 0.0
        self.right_cps = 0.0
        self.canvas.itemconfig(self.label, text="CPS: 0-0")


if __name__ == "__main__" and key == "oceanv1ontop":
    root = tk.Tk()
    root.withdraw()
    overlay_app_window = tk.Toplevel(root)
    overlay_app_window.attributes('-topmost', True)
    overlay_app = OverlayApp(overlay_app_window)
    cps_overlay_window = tk.Toplevel(root)
    cps_overlay_window.attributes('-topmost', True)
    cps_overlay = CPSOverlay(cps_overlay_window)
    root.mainloop()
elif key != "oceanv1ontop":
    print("Your key is invalid. Please get a key at discord.gg/PQdr94S2Ja")