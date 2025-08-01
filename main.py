from machine import Pin, I2C, PWM
from time import sleep, ticks_ms, ticks_diff
import ssd1306

# --- OLED SETUP ---
i2c = I2C(0, scl=Pin(1), sda=Pin(0))  # GP1=SCL, GP0=SDA
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# --- PWM OUTPUT TO ESC ---
pwm_pin = PWM(Pin(16))  # GP16
pwm_pin.freq(50)  # 50Hz = 20ms period

# --- ESC PWM PULSE RANGE ---
MIN_USEC = 1000  # 1.0 ms pulse = 0% throttle
MAX_USEC = 2000  # 2.0 ms pulse = 100% throttle

def set_pwm_usec(usec):
    # 20ms period = 50Hz; 65535 = 100% duty in 16-bit range
    duty_u16 = int(usec * 65535 / 20000)
    pwm_pin.duty_u16(duty_u16)

# --- ESC ARMING ---
oled.fill(0)
oled.text("Arming ESC...", 0, 0)
oled.show()
set_pwm_usec(MIN_USEC)
sleep(10)  # Wait for ESC to arm

# --- KY-040 Rotary Encoder ---
clk = Pin(14, Pin.IN, Pin.PULL_UP)
dt = Pin(15, Pin.IN, Pin.PULL_UP)

last_clk = clk.value()
duty_percent = 0  # Start at 0%

def update_display():
    oled.fill(0)
    oled.text("Duty Cycle:", 0, 0)
    oled.text("{}%".format(duty_percent), 0, 20)
    oled.show()

update_display()

# --- MAIN LOOP ---
while True:
    current_clk = clk.value()
    current_dt = dt.value()
    
    if current_clk != last_clk:
        if current_dt != current_clk:
            duty_percent += 1
        else:
            duty_percent -= 1
        
        # Clamp value between 0 and 100
        duty_percent = max(0, min(100, duty_percent))
        
        # Convert to microseconds
        pulse = MIN_USEC + int((MAX_USEC - MIN_USEC) * (duty_percent / 100))
        set_pwm_usec(pulse)
        update_display()

    last_clk = current_clk
    sleep(0.001)  # Debounce