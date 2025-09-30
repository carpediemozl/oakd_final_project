import time
from board import SCL, SDA
import busio
from adafruit_servokit import ServoKit
import readchar # 需要安装一个新的库来读取单个按键

# --- 配置 ---
PCA9685_CHANNELS = 16
PAN_CHANNEL = 1   # 垂直舵机通道
TILT_CHANNEL = 0  # 水平舵机通道

# 舵机角度限制 (与主程序保持一致)
PAN_MIN_ANGLE = 10
PAN_MAX_ANGLE = 170
TILT_MIN_ANGLE = 40
TILT_MAX_ANGLE = 140

# --- 初始化舵机 ---
try:
    i2c = busio.I2C(SCL, SDA)
    kit = ServoKit(channels=PCA9685_CHANNELS, i2c=i2c)
    print("PCA9685 初始化成功。")
except ValueError:
    print("错误: 无法找到I2C设备。请运行 'sudo i2cdetect -y 1' 检查硬件连接。")
    exit()

pan_servo = kit.servo[PAN_CHANNEL]
tilt_servo = kit.servo[TILT_CHANNEL]
pan_servo.set_pulse_width_range(500, 2500)
tilt_servo.set_pulse_width_range(500, 2500)

# --- 校准主程序 ---
if __name__ == "__main__":
    # 从一个大概的中心点开始
    pan_angle = 90.0
    tilt_angle = 90.0
    
    pan_servo.angle = pan_angle
    tilt_servo.angle = tilt_angle
    
    print("\n--- 舵机校准程序 ---")
    print("使用 'w', 's' 控制垂直 (Tilt) 舵机")
    print("使用 'a', 'd' 控制水平 (Pan) 舵机")
    print("使用 'q' 退出并打印最终角度。")
    print("--------------------")

    while True:
        # 打印当前角度，方便记录
        print(f"\r当前角度 -> Pan: {pan_angle:.1f}, Tilt: {tilt_angle:.1f}", end="")
        
        # 读取单个按键输入
        key = readchar.readkey()

        # 根据按键调整角度
        if key == 'w':
            tilt_angle += 0.5
        elif key == 's':
            tilt_angle -= 0.5
        elif key == 'a':
            pan_angle += 0.5
        elif key == 'd':
            pan_angle -= 0.5
        elif key == 'q':
            break # 退出循环

        # 限制角度在安全范围内
        pan_angle = max(PAN_MIN_ANGLE, min(PAN_MAX_ANGLE, pan_angle))
        tilt_angle = max(TILT_MIN_ANGLE, min(TILT_MAX_ANGLE, tilt_angle))
        
        # 更新舵机位置
        pan_servo.angle = pan_angle
        tilt_servo.angle = tilt_angle

    # 退出后打印最终结果
    print("\n\n校准完成！")
    print("请将以下值更新到您的主追踪脚本中：")
    print(f"PAN_CENTER_ANGLE = {pan_angle:.1f}")
    print(f"TILT_CENTER_ANGLE = {tilt_angle:.1f}")