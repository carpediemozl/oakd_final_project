import RPi.GPIO as GPIO
import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685

# --- 1. 配置 (CONFIG) ---
# 定义每个马达对应的控制引脚
# 这个配置完全匹配您描述的接线
MOTOR_PINS = {
    # 马达 0 (对应 L298N 的通道 A)
    0: {'in1': 5,  'in2': 6,  'pwm_channel': 2},
    # 马达 1 (对应 L298N 的通道 B)
    1: {'in1': 13, 'in2': 19, 'pwm_channel': 3},
    # 马达 2 (我们暂时只配置两个，您可以后续添加)
    # 2: {'in1': 26, 'in2': 21, 'pwm_channel': 4}, 
}

class HapticController:
    """
    一个用于控制L298N和PCA9685驱动的震动马达的类。
    """
    def __init__(self, motor_config):
        self.config = motor_config
        self.motor_ids = list(self.config.keys())
        
        # 初始化 I2C 和 PCA9685
        try:
            self.i2c = busio.I2C(SCL, SDA)
            self.pca = PCA9685(self.i2c)
            self.pca.frequency = 1000  # PWM频率，1000Hz对马达来说是个不错的值
            print("PCA9685 初始化成功。")
        except ValueError:
            print("错误: 无法找到I2C设备。请运行 'sudo i2cdetect -y 1' 检查硬件连接。")
            exit()
            
        # 初始化 GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for motor_id in self.motor_ids:
            pins = self.config[motor_id]
            GPIO.setup(pins['in1'], GPIO.OUT)
            GPIO.setup(pins['in2'], GPIO.OUT)
            # 默认设置为停止状态
            GPIO.output(pins['in1'], GPIO.LOW)
            GPIO.output(pins['in2'], GPIO.LOW)
        print("GPIO 初始化成功。")

    def set_vibration(self, motor_id, intensity):
        """
        设置单个马达的震动强度。

        :param motor_id: 马达编号 (例如 0, 1)
        :param intensity: 强度值，从 0.0 (停止) 到 1.0 (最强)
        """
        if motor_id not in self.motor_ids:
            print(f"错误: 马达 {motor_id} 不存在。")
            return
            
        if not 0.0 <= intensity <= 1.0:
            print("错误: 强度值必须在 0.0 和 1.0 之间。")
            return

        pins = self.config[motor_id]
        
        # 只有当强度大于一个很小的值时才启动马达
        if intensity > 0.01:
            # 设置 L298N 为正转 (IN1=HIGH, IN2=LOW) 来启动马达
            # 如果您的马达不转，可以尝试将这里设为 (IN1=LOW, IN2=HIGH)
            GPIO.output(pins['in1'], GPIO.HIGH)
            GPIO.output(pins['in2'], GPIO.LOW)
            
            # PCA9685 使用 16 位精度 (0-65535) 来控制PWM占空比
            # 我们将 0.0-1.0 的强度值映射到这个范围
            duty_cycle = int(intensity * 65535)
            self.pca.channels[pins['pwm_channel']].duty_cycle = duty_cycle
        else:
            # 如果强度为0，则停止马达
            GPIO.output(pins['in1'], GPIO.LOW)
            GPIO.output(pins['in2'], GPIO.LOW)
            self.pca.channels[pins['pwm_channel']].duty_cycle = 0

    def cleanup(self):
        """在程序结束时调用，用于安全地停止所有马达并清理GPIO资源。"""
        print("\n正在停止所有马达并清理资源...")
        for motor_id in self.motor_ids:
            self.set_vibration(motor_id, 0)
        GPIO.cleanup()
        print("清理完成。")
# --- 3. 主程序：交互式震动强度测试台 ---
if __name__ == "__main__":
    # 创建 HapticController 的实例
    haptics = HapticController(MOTOR_PINS)
    
    # 定义我们要测试的强度等级 (0.25 = 25%)
    intensity_levels = [0.25, 0.5, 0.75, 1.0]
    
    try:
        print("\n--- 交互式震动强度测试 ---")
        print("程序将依次测试每个马达在不同强度下的震动效果。")
        print("每个强度等级将持续2秒，中间间隔1秒。")
        print("按 Ctrl+C 可以随时退出测试。\n")
        
        # 等待用户确认开始
        input("准备好后，请按 Enter 键开始测试...")

        # 遍历所有已配置的马达
        for motor_id in haptics.motor_ids:
            print(f"\n>>> 开始测试马达 {motor_id} <<<")
            
            # 遍历所有强度等级
            for intensity in intensity_levels:
                print(f"  - 测试强度: {int(intensity * 100)}%")
                
                # 设置震动
                haptics.set_vibration(motor_id, intensity)
                
                # 持续震动2秒
                time.sleep(2)
                
                # 停止震动，并等待1秒，方便感受间隔
                haptics.set_vibration(motor_id, 0)
                time.sleep(1)
            
            print(f">>> 马达 {motor_id} 测试完成 <<<\n")
            time.sleep(1) # 在测试下一个马达前，额外停顿1秒

        print("--- 所有测试完成 ---")

    except KeyboardInterrupt:
        # 如果用户按下 Ctrl+C，我们也能安全地退出
        print("\n\n检测到手动中断。")
    finally:
        # 无论程序是正常结束还是被中断，都必须执行清理操作
        haptics.cleanup()