import time
from adafruit_servokit import ServoKit

# --- 您可以修改这里的“魔法数字” ---

# 水平舵机 (Pan Servo) 的参数
PAN_CHANNEL = 1  # 水平舵机连接在PCA9685的1号通道
PAN_CENTER_ANGLE = 90  # 水平舵机的中心位置 (90度是正中间)
PAN_RANGE_OF_MOTION = 60  # 水平舵机来回摆动的总范围 (比如60度)

# 垂直舵机 (Tilt Servo) 的参数
TILT_CHANNEL = 0  # 垂直舵机连接在PCA9685的0号通道
TILT_CENTER_ANGLE = 90  # 垂直舵机的中心位置 (90度是平视)
TILT_RANGE_OF_MOTION = 30  # 垂直舵机来回摆动的总范围 (比如30度)

# --- 代码主体部分 ---

# 计算转动范围
pan_min_angle = PAN_CENTER_ANGLE - (PAN_RANGE_OF_MOTION / 2)
pan_max_angle = PAN_CENTER_ANGLE + (PAN_RANGE_OF_MOTION / 2)

tilt_min_angle = TILT_CENTER_ANGLE - (TILT_RANGE_OF_MOTION / 2)
tilt_max_angle = TILT_CENTER_ANGLE + (TILT_RANGE_OF_MOTION / 2)

# 初始化PCA9685
kit = ServoKit(channels=16)

# 获取舵机对象
pan_servo = kit.servo[PAN_CHANNEL]
tilt_servo = kit.servo[TILT_CHANNEL]

# 设置脉宽范围以确保180度运动
pan_servo.set_pulse_width_range(500, 2500)
tilt_servo.set_pulse_width_range(500, 2500)

try:
    print("舵机小范围扫描测试开始！按 Ctrl+C 退出。")
    
    # 先让舵机都回到中间位置
    pan_servo.angle = PAN_CENTER_ANGLE
    tilt_servo.angle = TILT_CENTER_ANGLE
    time.sleep(2)

    while True:
        print(f"水平扫描: 从 {pan_min_angle}度 到 {pan_max_angle}度")
        # 水平舵机从最小角度到最大角度
        for angle in range(int(pan_min_angle), int(pan_max_angle), 1):
            pan_servo.angle = angle
            time.sleep(0.02) # 减慢速度，让运动更平滑
        
        # 水平舵机从最大角度回到最小角度
        for angle in range(int(pan_max_angle), int(pan_min_angle), -1):
            pan_servo.angle = angle
            time.sleep(0.02)

        print(f"垂直扫描: 从 {tilt_min_angle}度 到 {tilt_max_angle}度")
        # 垂直舵机从最小角度到最大角度
        for angle in range(int(tilt_min_angle), int(tilt_max_angle), 1):
            tilt_servo.angle = angle
            time.sleep(0.02)

        # 垂直舵机从最大角度回到最小角度
        for angle in range(int(tilt_max_angle), int(tilt_min_angle), -1):
            tilt_servo.angle = angle
            time.sleep(0.02)


except KeyboardInterrupt:
    print("\n程序被中断。将舵机归位...")
    pan_servo.angle = PAN_CENTER_ANGLE
    tilt_servo.angle = TILT_CENTER_ANGLE
    time.sleep(1)
    print("测试结束。")
