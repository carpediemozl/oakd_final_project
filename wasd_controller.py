import time
import sys
import tty
import termios
from adafruit_servokit import ServoKit

# --- 您可以修改这里的“魔法数字” ---
TILT_CHANNEL = 0  # 垂直舵机 (上下)
PAN_CHANNEL = 1   # 水平舵机 (左右)

# 您通过手动校准找到的最佳中心角度
TILT_CENTER_ANGLE = 90.0
PAN_CENTER_ANGLE = 90.0

# 每次按键，舵机转动的角度 (步进大小)
STEP_SIZE = 1.0
# -----------------------------------------

# --- 初始化舵机 ---
kit = ServoKit(channels=16)
tilt_servo = kit.servo[TILT_CHANNEL]
pan_servo = kit.servo[PAN_CHANNEL]
tilt_servo.set_pulse_width_range(500, 2500)
pan_servo.set_pulse_width_range(500, 2500)

current_tilt_angle = TILT_CENTER_ANGLE
current_pan_angle = PAN_CENTER_ANGLE
tilt_servo.angle = current_tilt_angle
pan_servo.angle = current_pan_angle

# --- 这是一个用来读取单个字符的函数 ---
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# --- 主程序 ---
print("WASD 实时舵机控制器已启动！(逻辑修正版)")
print("---------------------------------")
print("     [W] - 向上")
print("[A] - 向左  [S] - 向下  [D] - 向右")
print("     [SPACE] - 归中")
print("     [Q] - 退出")
print("---------------------------------")
print("请直接按键，无需回车。")

while True:
    try:
        key = getch().lower()

        if key == 'q':
            print("\n正在退出...")
            break
        
        elif key == ' ':
            current_tilt_angle = TILT_CENTER_ANGLE
            current_pan_angle = PAN_CENTER_ANGLE
            print(f"归中: Pan={current_pan_angle:.1f}, Tilt={current_tilt_angle:.1f}")

        # --- 这里的逻辑已经为您修正 ---
        elif key == 'w':
            current_tilt_angle += STEP_SIZE # 逻辑反转！
            print(f"向上: Tilt={current_tilt_angle:.1f}")

        elif key == 's':
            current_tilt_angle -= STEP_SIZE # 逻辑反转！
            print(f"向下: Tilt={current_tilt_angle:.1f}")

        elif key == 'a':
            current_pan_angle -= STEP_SIZE # 逻辑反转！
            print(f"向左: Pan={current_pan_angle:.1f}")

        elif key == 'd':
            current_pan_angle += STEP_SIZE # 逻辑反转！
            print(f"向右: Pan={current_pan_angle:.1f}")
        # --------------------------------

        # 限制角度在0-180度之间
        current_pan_angle = max(0, min(180, current_pan_angle))
        current_tilt_angle = max(0, min(180, current_tilt_angle))

        # 发送指令
        pan_servo.angle = current_pan_angle
        tilt_servo.angle = current_tilt_angle

    except KeyboardInterrupt:
        print("\n程序被中断。退出。")
        break

# 退出时归中
pan_servo.angle = PAN_CENTER_ANGLE
tilt_servo.angle = TILT_CENTER_ANGLE
print("舵机已归中。")
