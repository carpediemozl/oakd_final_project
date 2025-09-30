import time
from adafruit_servokit import ServoKit

# 初始化PCA9685，默认I2C地址，16个通道
kit = ServoKit(channels=16)

# 选择要控制的舵机通道
# kit.servo[0] 对应 Channel 0
# kit.servo[1] 对应 Channel 1
pan_servo = kit.servo[0]  # 水平转动的舵机
tilt_servo = kit.servo[1] # 垂直转动的舵机

# 设置舵机的脉宽范围 (DS3218舵机通常是500-2500us)
# 这一步很重要，可以确保舵机能转动180度
pan_servo.set_pulse_width_range(500, 2500)
tilt_servo.set_pulse_width_range(500, 2500)

try:
    print("舵机测试开始！按 Ctrl+C 退出。")
    
    # 先让舵机都回到中间位置 (90度)
    pan_servo.angle = 90
    tilt_servo.angle = 90
    time.sleep(1)

    print("开始来回转动...")
    while True:
        # 水平舵机从0度转到180度
        for angle in range(0, 180, 1):
            pan_servo.angle = angle
            time.sleep(0.01)
        time.sleep(0.5)
        
        # 水平舵机从180度转回0度
        for angle in range(180, 0, -1):
            pan_servo.angle = angle
            time.sleep(0.01)
        time.sleep(0.5)

        # 垂直舵机从90度转到180度 (向上看)
        for angle in range(90, 180, 1):
            tilt_servo.angle = angle
            time.sleep(0.01)
        time.sleep(0.5)

        # 垂直舵机从180度转回90度 (回到中间)
        for angle in range(180, 90, -1):
            tilt_servo.angle = angle
            time.sleep(0.01)
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n程序被中断。将舵机归位...")
    pan_servo.angle = 90
    tilt_servo.angle = 90
    time.sleep(1)
    print("测试结束。")
