import RPi.GPIO as GPIO
import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
import readchar

# --- 1. 配置 (CONFIG) ---
# (这里的配置和您之前的 haptic_controller.py 保持一致)
MOTOR_PINS = {
    0: {'in1': 5,  'in2': 6,  'pwm_channel': 2},
    1: {'in1': 13, 'in2': 19, 'pwm_channel': 3},
}

# --- 2. HapticController 类 ---
# (这个类和您之前的 haptic_controller.py 完全一样)
class HapticController:
    def __init__(self, motor_config):
        self.config = motor_config
        self.motor_ids = list(self.config.keys())
        try:
            self.i2c = busio.I2C(SCL, SDA)
            self.pca = PCA9685(self.i2c)
            self.pca.frequency = 1000
            print("PCA9685 初始化成功。")
        except ValueError:
            print("错误: 无法找到I2C设备。请运行 'sudo i2cdetect -y 1' 检查硬件连接。")
            exit()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for motor_id in self.motor_ids:
            pins = self.config[motor_id]
            GPIO.setup(pins['in1'], GPIO.OUT)
            GPIO.setup(pins['in2'], GPIO.OUT)
            GPIO.output(pins['in1'], GPIO.LOW)
            GPIO.output(pins['in2'], GPIO.LOW)
        print("GPIO 初始化成功。")

    def set_vibration(self, motor_id, intensity):
        if motor_id not in self.motor_ids:
            print(f"错误: 马达 {motor_id} 不存在。")
            return
        intensity = max(0.0, min(1.0, intensity)) # 确保强度值在0-1之间
        pins = self.config[motor_id]
        if intensity > 0.01:
            GPIO.output(pins['in1'], GPIO.HIGH)
            GPIO.output(pins['in2'], GPIO.LOW)
            duty_cycle = int(intensity * 65535)
            self.pca.channels[pins['pwm_channel']].duty_cycle = duty_cycle
        else:
            GPIO.output(pins['in1'], GPIO.LOW)
            GPIO.output(pins['in2'], GPIO.LOW)
            self.pca.channels[pins['pwm_channel']].duty_cycle = 0

    def cleanup(self):
        print("\n正在停止所有马达并清理资源...")
        for motor_id in self.motor_ids:
            self.set_vibration(motor_id, 0)
        GPIO.cleanup()
        print("清理完成。")

# --- 3. 主程序：实时震动强度调谐器 ---
if __name__ == "__main__":
    haptics = HapticController(MOTOR_PINS)
    
    # 初始化控制变量
    current_motor_id = 0
    current_intensity = 0.0
    step = 0.05  # 每次按键增加/减少 5% 的强度

    try:
        print("\n--- 实时震动强度调谐器 ---")
        print("使用 'a' / 'd' 来增加 / 减少震动强度。")
        print("使用 's' 来切换控制的马达 (0 或 1)。")
        print("使用 'q' 退出。")
        print("---------------------------------")

        # 初始状态下，先让一个马达震动一下，确认它在工作
        haptics.set_vibration(current_motor_id, 0.1)
        time.sleep(0.1)
        haptics.set_vibration(current_motor_id, 0)

        while True:
            # 实时在终端显示当前状态
            # \r 让光标回到行首，end="" 防止换行，实现单行刷新
            print(f"\r控制中: 马达 {current_motor_id} | 当前强度: {current_intensity * 100:.0f}%  ", end="")
            
            # 读取键盘输入
            key = readchar.readkey()

            if key == 'd': # 增加强度
                current_intensity += step
            elif key == 'a': # 减少强度
                current_intensity -= step
            elif key == 's': # 切换马达
                # 停止当前马达
                haptics.set_vibration(current_motor_id, 0)
                # 切换ID
                current_motor_id = 1 - current_motor_id # 在 0 和 1 之间切换
                # 让新马达震动一下以提示
                haptics.set_vibration(current_motor_id, 0.1)
                time.sleep(0.1)
                haptics.set_vibration(current_motor_id, 0)
                # 重置强度，从0开始为新马达调谐
                current_intensity = 0.0
                print() # 换行以显示切换信息
                continue # 跳过本次循环的强度设置
            elif key == 'q': # 退出
                break

            # 确保强度值在 0.0 到 1.0 的范围内
            current_intensity = max(0.0, min(1.0, current_intensity))
            
            # 将新的强度应用到当前控制的马达上
            haptics.set_vibration(current_motor_id, current_intensity)

    except KeyboardInterrupt:
        print("\n\n检测到手动中断。")
    finally:
        haptics.cleanup()