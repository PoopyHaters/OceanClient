import pygame
import os
import pyautogui
def is_pixel_red(x, y):
    try:
        pixel_color = pyautogui.pixel(x, y)
        return pixel_color[0] > 200 and pixel_color[1] < 50 and pixel_color[2] < 50
    except Exception:
        return False
def main():
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
                    time.sleep(0.2)
                except Exception:
                    pass
            elif not is_pixel_red(middle_x, middle_y):
                if not canPlay:
                    canPlay = True
    except KeyboardInterrupt:
        pygame.mixer.quit()
if __name__ == "__main__":
    main()