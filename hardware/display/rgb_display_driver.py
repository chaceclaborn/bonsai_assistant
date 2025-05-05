# File: hardware/display/rgb_display_driver.py

import platform
from datetime import datetime

try:
    import tkinter as tk
except ImportError:
    tk = None

if platform.system() != "Windows":
    import board
    import digitalio
    import busio
    from adafruit_rgb_display import ssd1351
    from PIL import Image, ImageDraw, ImageFont


class RGBDisplayDriver:
    def __init__(self, width=128, height=128, rotation=180):
        self.width = width
        self.height = height
        self.rotation = rotation
        self.is_simulated = platform.system() == "Windows"
        self.display = None

        self._last_displayed = {
            "header": None,
            "time": None,
            "moisture": None,
            "pump": None
        }

        if self.is_simulated:
            print("ℹ️ Running in simulation mode (tkinter).")
            self._create_simulator()
        else:
            try:
                self._init_hardware()
                print("✅ Display hardware initialized.")
            except Exception as e:
                print(f"⚠️ Display hardware init failed: {e}")
                self.is_simulated = True
                self._create_simulator()

    def _create_simulator(self):
        self.root = tk.Tk()
        self.root.title("OLED Simulator")
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="black")
        self.canvas.pack()

    def _init_hardware(self):
        spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        rst_pin = digitalio.DigitalInOut(board.D27)

        self.display = ssd1351.SSD1351(
            spi=spi,
            cs=cs_pin,
            dc=dc_pin,
            rst=rst_pin,
            width=self.width,
            height=self.height,
            rotation=self.rotation
        )

    def clear(self):
        if self.is_simulated:
            self.canvas.delete("all")
            self.root.update()
        else:
            from PIL import Image
            image = Image.new("RGB", (self.width, self.height), "black")
            self.display.image(image)
        print("🩹 Display cleared.")

    def draw_status(self, moisture=None, pump_status="OFF", runtime_sec=0):
        from PIL import Image, ImageDraw, ImageFont

        current_time = datetime.now().strftime("%I:%M %p").lstrip("0")
        moisture_str = f"{moisture}%" if moisture is not None else "---"
        pump_line = f"Pump: {pump_status} | {int(runtime_sec)} sec"

        try:
            font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            font_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
            font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
        except IOError:
            font_header = font_time = font_body = ImageFont.load_default()

        image = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(image)

        y = 5
        for key, text in {
            "header": "Bonsai Assistant",
            "time": current_time,
            "moisture": f"Moisture %: {moisture_str}",
            "pump": pump_line
        }.items():
            font = font_header if key == "header" else font_time if key == "time" else font_body
            x = (self.width - draw.textlength(text, font=font)) // 2
            draw.text((x, y), text, font=font, fill=(0, 255, 0))
            y += 22 if key == "header" else 18 if key == "time" else 15

        if not self.is_simulated:
            self.display.image(image)
        else:
            print(f"[Simulated OLED Output] Moisture: {moisture_str}, Pump: {pump_line}")

        if self.is_simulated:
            self.root.update()


if __name__ == "__main__":
    import time
    oled = RGBDisplayDriver()
    moisture = None
    pump_status = "OFF"
    runtime_sec = 0

    while True:
        oled.draw_status(moisture, pump_status, runtime_sec)
        runtime_sec += 1
        time.sleep(1)
