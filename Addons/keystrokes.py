import tkinter as tk
import keyboard
import threading
import json
import os
from time import time


class KeystrokeOverlay:
    def __init__(self, root):
        self.root = root
        self.root.title("Keystroke Overlay")

        # Load configuration
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_dir, "keystroke_config.json")
        self.config = self.load_config()

        # Set window position from config
        initial_x = self.config.get("x", 10)
        initial_y = self.config.get("y", 10)

        # ENLARGED: Increased window size
        self.root.geometry(f"210x270+{initial_x}+{initial_y}")
        self.root.wm_attributes('-transparentcolor', 'black')
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)  # Remove window borders

        # Key state tracking
        self.pressed_keys = set()

        # Create UI elements
        self.create_ui()

        # Bind mouse events for dragging
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.drag_data = {"x": 0, "y": 0}

        # Start keyboard listener
        self.start_keyboard_listener()

    def load_config(self):
        if not os.path.exists(self.config_path):
            default_config = {"x": 10, "y": 10}
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_config(self):
        self.config["x"] = self.root.winfo_x()
        self.config["y"] = self.root.winfo_y()
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def create_ui(self):
        # Create canvas with transparent background
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # ENLARGED: Define key positions and sizes (50% larger)
        key_size = 60
        padding = 15

        # W key (top)
        w_x, w_y = 105, 60
        self.w_rect = self.create_key_rect(w_x, w_y, key_size, 'W')

        # A key (left)
        a_x, a_y = w_x - key_size - padding, w_y + key_size + padding
        self.a_rect = self.create_key_rect(a_x, a_y, key_size, 'A')

        # S key (bottom middle)
        s_x, s_y = w_x, a_y
        self.s_rect = self.create_key_rect(s_x, s_y, key_size, 'S')

        # D key (right)
        d_x, d_y = w_x + key_size + padding, a_y
        self.d_rect = self.create_key_rect(d_x, d_y, key_size, 'D')

        # Space bar (adjusted position)
        space_width = 215  # ENLARGED: Wider space bar
        space_height = 45  # ENLARGED: Taller space bar
        # Adjusted position - lower than before
        space_y = a_y + key_size  # Place it below the bottom row keys with padding
        space_x = 105  # Center horizontally
        self.space_rect = self.create_space_rect(space_x, space_y, space_width, space_height)

    def create_key_rect(self, x, y, size, key_text):
        outline_color = "#555555"
        fill_color = "#333333"
        text_color = "#FFFFFF"

        rect_id = self.canvas.create_rectangle(
            x - size / 2, y - size / 2, x + size / 2, y + size / 2,
            fill=fill_color, outline=outline_color, width=2,  # ENLARGED: Thicker outline
            tags=f"{key_text.lower()}_key"
        )

        text_id = self.canvas.create_text(
            x, y,
            text=key_text,
            font=("Arial", 18, "bold"),  # ENLARGED: Larger font
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
            fill=fill_color, outline=outline_color, width=2,  # ENLARGED: Thicker outline
            tags="space_key"
        )

        text_id = self.canvas.create_text(
            x, y,
            text="SPACE",
            font=("Arial", 18, "bold"),  # ENLARGED: Larger font
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

        # Start keyboard hook in a separate thread
        keyboard_thread = threading.Thread(target=lambda: keyboard.hook(on_key_event))
        keyboard_thread.daemon = True
        keyboard_thread.start()

    def update_key_visual(self, key, is_pressed):
        # Map key to tag
        tag = f"{key}_key"

        # Update key appearance based on state
        if is_pressed:
            self.canvas.itemconfig(tag, fill="#4a86e8")  # Blue when pressed
        else:
            self.canvas.itemconfig(tag, fill="#333333")  # Gray when released

    def start_drag(self, event):
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()

    def on_drag(self, event):
        x = event.x_root - self.drag_data["x"]
        y = event.y_root - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

    def stop_drag(self, event):
        self.save_config()


if __name__ == "__main__":
    root = tk.Tk()
    app = KeystrokeOverlay(root)
    root.mainloop()