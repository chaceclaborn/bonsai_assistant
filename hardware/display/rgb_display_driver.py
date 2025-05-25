# File: hardware/display/rgb_display_driver.py

import platform
from datetime import datetime
import time

# Import PIL components
try:
    from PIL import Image, ImageDraw, ImageFont, ImageTk
except ImportError:
    print("Warning: PIL/Pillow not installed. Display features limited.")
    print("Install with: pip install Pillow")
    Image = None
    ImageDraw = None
    ImageFont = None
    ImageTk = None

# Import tkinter for simulation
try:
    import tkinter as tk
except ImportError:
    tk = None

# Platform-specific imports
if platform.system() != "Windows":
    try:
        import board
        import digitalio
        import busio
        from adafruit_rgb_display import ssd1351
    except ImportError as e:
        print(f"Display hardware import error: {e}")
        board = None
else:
    board = None


class RGBDisplayDriver:
    def __init__(self, width=128, height=128, rotation=180):
        self.width = width
        self.height = height
        self.rotation = rotation
        self.is_simulated = platform.system() == "Windows" or board is None
        self.display = None
        self._last_update = 0
        self._min_update_interval = 0.1  # Minimum time between updates

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
        """Create simple simulator window"""
        try:
            self.root = tk.Tk()
            self.root.title("OLED Simulator")
            self.root.geometry("256x256")  # 2x scale for visibility
            self.canvas = tk.Canvas(self.root, width=256, height=256, bg="black")
            self.canvas.pack()
            self.root.withdraw()  # Hide by default
        except:
            print("Could not create simulator window")
            self.root = None
            self.canvas = None

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
        """Clear the display"""
        if self.is_simulated:
            if self.canvas:
                self.canvas.delete("all")
                self.root.update_idletasks()
        else:
            from PIL import Image
            image = Image.new("RGB", (self.width, self.height), "black")
            self.display.image(image)
        print("🩹 Display cleared.")

    def draw_status(self, moisture=None, pump_status="OFF", runtime_sec=0):
        """Draw status with rate limiting to prevent overload"""
        # Rate limiting
        current_time = time.time()
        if current_time - self._last_update < self._min_update_interval:
            return
        self._last_update = current_time

        # Check if we have required imports
        if not Image or not ImageDraw or not ImageFont:
            print(f"[OLED] Missing PIL imports - Moisture: {moisture}% | Pump: {pump_status}")
            return

        current_time_str = datetime.now().strftime("%I:%M %p").lstrip("0")
        moisture_str = f"{moisture:.1f}%" if moisture is not None else "---"
        pump_line = f"Pump: {pump_status}"

        # Try to load nice fonts, fall back to default
        try:
            font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)  # Reduced from 16
            font_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)    # Reduced from 14
            font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)    # Reduced from 12
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)         # Reduced from 10
        except IOError:
            try:
                # Try alternative font paths
                font_header = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 14)
                font_time = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 12)
                font_body = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 11)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 9)
            except IOError:
                font_header = font_time = font_body = font_small = ImageFont.load_default()

        # Create image
        image = Image.new("RGB", (self.width, self.height), "black")
        draw = ImageDraw.Draw(image)

        # Store moisture value for color logic
        moisture_value = moisture

        # Draw content
        y = 6  # Reduced from 8
        
        # Header - "Bonsai Assistant"
        text = "Bonsai Assistant"
        bbox = draw.textbbox((0, 0), text, font=font_header)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, y), text, font=font_header, fill=(0, 255, 0))
        y += 24  # Reduced from 26
        
        # Time - now in green
        bbox = draw.textbbox((0, 0), current_time_str, font=font_time)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        draw.text((x, y), current_time_str, font=font_time, fill=(0, 255, 0))  # Green time
        y += 23
        
        # Moisture with color coding
        moisture_text = f"💧 {moisture_str}"
        bbox = draw.textbbox((0, 0), moisture_text, font=font_body)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        
        if moisture_value is not None:
            if moisture_value < 20:
                moisture_color = (255, 0, 0)  # Red
            elif moisture_value < 40:
                moisture_color = (255, 165, 0)  # Orange
            else:
                moisture_color = (0, 255, 0)  # Green
        else:
            moisture_color = (255, 255, 255)  # White
            
        draw.text((x, y), moisture_text, font=font_body, fill=moisture_color)
        y += 20
        
        # Pump status - green when OFF, blue when ON
        bbox = draw.textbbox((0, 0), pump_line, font=font_body)
        text_width = bbox[2] - bbox[0]
        x = (self.width - text_width) // 2
        
        pump_color = (0, 191, 255) if pump_status == "ON" else (0, 255, 0)  # Blue when ON, Green when OFF
        draw.text((x, y), pump_line, font=font_body, fill=pump_color)
        y += 20
        
        # Add status indicators at bottom
        # Draw indicator lights for sensor and pump
        indicator_y = self.height - 25
        indicator_size = 8
        spacing = 35
        
        # Calculate center position for indicators
        total_width = (2 * indicator_size) + spacing + 80  # rough estimate
        start_x = (self.width - total_width) // 2
        
        # Sensor indicator
        sensor_x = start_x
        sensor_connected = moisture_value is not None
        sensor_color = (0, 255, 0) if sensor_connected else (255, 255, 0)  # Green if connected, Yellow if not
        
        # Draw sensor indicator circle
        draw.ellipse([sensor_x, indicator_y, sensor_x + indicator_size, indicator_y + indicator_size], 
                     fill=sensor_color, outline=sensor_color)
        draw.text((sensor_x + indicator_size + 3, indicator_y - 2), "Sensor", 
                  font=font_small, fill=(200, 200, 200))
        
        # Pump indicator
        pump_x = sensor_x + spacing + 40
        pump_on = pump_status == "ON"
        pump_color = (0, 255, 0) if pump_on else (255, 255, 0)  # Green if ON, Yellow if OFF
        
        # Draw pump indicator circle
        draw.ellipse([pump_x, indicator_y, pump_x + indicator_size, indicator_y + indicator_size], 
                     fill=pump_color, outline=pump_color)
        draw.text((pump_x + indicator_size + 3, indicator_y - 2), "Pump", 
                  font=font_small, fill=(200, 200, 200))

        # Display the image
        if not self.is_simulated:
            try:
                self.display.image(image)
            except Exception as e:
                print(f"Display error: {e}")
        else:
            # Simulator output
            if self.canvas and ImageTk:
                try:
                    # Scale up image for visibility
                    scaled_image = image.resize((256, 256), Image.LANCZOS)
                    self.tk_image = ImageTk.PhotoImage(scaled_image)
                    self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
                    self.root.update_idletasks()
                except Exception as e:
                    print(f"Simulator display error: {e}")
                    # Fallback to console output
                    print(f"[OLED] {current_time_str} | Moisture: {moisture_str} | {pump_line}")
            else:
                # Console output as fallback
                print(f"[OLED] {current_time_str} | Moisture: {moisture_str} | {pump_line}")


# Test function
if __name__ == "__main__":
    import time
    oled = RGBDisplayDriver()
    moisture = 45.0
    pump_status = "OFF"
    runtime_sec = 0

    print("Testing display...")
    while True:
        oled.draw_status(moisture, pump_status, runtime_sec)
        
        # Simulate changing values
        moisture = 20 + (time.time() % 60)
        if int(time.time()) % 10 < 3:
            pump_status = "ON"
            runtime_sec += 1
        else:
            pump_status = "OFF"
            
        time.sleep(1)