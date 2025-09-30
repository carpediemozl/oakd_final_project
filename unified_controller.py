import cv2
import depthai as dai
from adafruit_servokit import ServoKit
import time
import sys
import select
import tty
import termios

# --- 您可以修改这里的“魔法数字” ---
TILT_CHANNEL = 0  # 垂直舵机 (上下)
PAN_CHANNEL = 1   # 水平舵机 (左右)
TILT_CENTER_ANGLE = 90.0
PAN_CENTER_ANGLE = 90.0
STEP_SIZE = 1.0
# -----------------------------------------

# --- 初始化舵机 ---
print("正在初始化PCA9685舵机控制器...")
kit = ServoKit(channels=16)
tilt_servo = kit.servo[TILT_CHANNEL]
pan_servo = kit.servo[PAN_CHANNEL]
tilt_servo.set_pulse_width_range(500, 2500)
pan_servo.set_pulse_width_range(500, 2500)
current_tilt_angle = TILT_CENTER_ANGLE
current_pan_angle = PAN_CENTER_ANGLE
tilt_servo.angle = current_tilt_angle
pan_servo.angle = current_pan_angle
print("舵机已归中。")

# --- 初始化OAK-D相机 ---
print("正在初始化OAK-D相机...")
pipeline = dai.Pipeline()
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

# --- 这是一个用来检查是否有键盘输入的函数 (非阻塞) ---
def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

# 保存终端的旧设置
old_settings = termios.tcgetattr(sys.stdin)

try:
    # 设置终端为“原始模式”，这样可以立刻读取到按键
    tty.setcbreak(sys.stdin.fileno())

    print("\n一体化控制台已启动！")
    print("---------------------------------")
    print("     [W] - 向上")
    print("[A] - 向左  [S] - 向下  [D] - 向右")
    print("     [SPACE] - 归中")
    print("     [Q] - 退出")
    print("---------------------------------")
    print("请直接按键，无需回车。")

    # 连接并启动设备
    with dai.Device(pipeline) as device:
        q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        while True:
            # 1. 处理视频流
            in_rgb = q_rgb.tryGet()
            if in_rgb is not None:
                frame = in_rgb.getCvFrame()
                cv2.imshow("OAK-D 一体化控制台", frame)
            
            # 必须要有这行，即使时间很短，它负责处理窗口的刷新
            cv2.waitKey(1)

            # 2. 处理键盘输入 (非阻塞)
            if isData():
                key = sys.stdin.read(1).lower()

                if key == 'q':
                    print("\n正在退出...")
                    break
                
                elif key == ' ':
                    current_tilt_angle = TILT_CENTER_ANGLE
                    current_pan_angle = PAN_CENTER_ANGLE
                
                # --- 这里的逻辑是修正过的 ---
                elif key == 'w': current_tilt_angle += STEP_SIZE
                elif key == 's': current_tilt_angle -= STEP_SIZE
                elif key == 'a': current_pan_angle -= STEP_SIZE
                elif key == 'd': current_pan_angle += STEP_SIZE
                
                # 限制角度在0-180度之间
                current_pan_angle = max(0, min(180, current_pan_angle))
                current_tilt_angle = max(0, min(180, current_tilt_angle))

                print(f"指令: Pan={current_pan_angle:.1f}, Tilt={current_tilt_angle:.1f}")

            # 3. 更新舵机角度
            pan_servo.angle = current_pan_angle
            tilt_servo.angle = current_tilt_angle
            
            # 短暂延时，避免CPU占用过高
            time.sleep(0.01)

finally:
    # 程序退出时，恢复终端的设置，非常重要！
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    # 归中舵机
    pan_servo.angle = PAN_CENTER_ANGLE
    tilt_servo.angle = TILT_CENTER_ANGLE
    cv2.destroyAllWindows()
    print("\n程序已退出，舵机已归中。")
