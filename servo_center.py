from adafruit_servokit import ServoKit
import time

# 初始化
kit = ServoKit(channels=16)

# 设置脉宽 (重要！)
kit.servo[0].set_pulse_width_range(500, 2500)
kit.servo[1].set_pulse_width_range(500, 2500)

# 将两个舵机都设置到90度中心位置
print("正在将舵机归中至90度...")
kit.servo[0].angle = 90
kit.servo[1].angle = 90
time.sleep(2) # 等待舵机转动到位
print("归中完成！现在可以断开舵机电源并开始组装。")
