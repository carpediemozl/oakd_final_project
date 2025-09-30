import cv2
import depthai as dai
from adafruit_servokit import ServoKit
import time

# --- 您可以修改这里的“魔法数字” ---

# 舵机通道配置 (根据您的实际接线)
TILT_CHANNEL = 0  # 垂直舵机 (上下)
PAN_CHANNEL = 1   # 水平舵机 (左右)

# 舵机初始/中心位置 (您通过手动校准找到的最佳角度)
TILT_CENTER_ANGLE = 90.0
PAN_CENTER_ANGLE = 90.0

# 每次按键，舵机转动的角度 (步进大小)
STEP_SIZE = 1.0

# --- 初始化舵机 ---
print("正在初始化PCA9685舵机控制器...")
kit = ServoKit(channels=16)
tilt_servo = kit.servo[TILT_CHANNEL]
pan_servo = kit.servo[PAN_CHANNEL]
# 设置脉宽以确保180度运动
tilt_servo.set_pulse_width_range(500, 2500)
pan_servo.set_pulse_width_range(500, 2500)

# 将舵机移动到初始中心位置
current_tilt_angle = TILT_CENTER_ANGLE
current_pan_angle = PAN_CENTER_ANGLE
tilt_servo.angle = current_tilt_angle
pan_servo.angle = current_pan_angle
print("舵机已归中。")

# --- 初始化OAK-D相机 ---
print("正在初始化OAK-D相机...")
pipeline = dai.Pipeline()
# 创建彩色相机节点
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
# 创建输出队列
xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

# --- 主程序 ---
print("OAK-D手动云台控制台已启动！")
print("---------------------------------")
print("     [W] - 向上")
print("[A] - 向左  [S] - 向下  [D] - 向右")
print("     [SPACE] - 归中")
print("     [Q] - 退出")
print("---------------------------------")
print("请确保OAK-D视频窗口处于激活状态以接收键盘指令。")

# 连接并启动设备
with dai.Device(pipeline) as device:
    q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    while True:
        # 从OAK-D获取一帧图像
        in_rgb = q_rgb.tryGet()

        if in_rgb is not None:
            frame = in_rgb.getCvFrame()
            # 显示图像
            cv2.imshow("OAK-D 云台控制台", frame)

        # 等待键盘输入 (这是整个程序最关键的部分！)
        key = cv2.waitKey(1)

        # --- 根据键盘输入控制舵机 ---
        
        # 退出
        if key == ord('q'):
            print("正在退出...")
            break
        
        # 归中
        elif key == ord(' '):
            current_tilt_angle = TILT_CENTER_ANGLE
            current_pan_angle = PAN_CENTER_ANGLE
            print(f"归中: Pan={current_pan_angle}, Tilt={current_tilt_angle}")

        # 向上 (Tilt)
        elif key == ord('w'):
            current_tilt_angle -= STEP_SIZE
            print(f"向上: Tilt={current_tilt_angle}")

        # 向下 (Tilt)
        elif key == ord('s'):
            current_tilt_angle += STEP_SIZE
            print(f"向下: Tilt={current_tilt_angle}")

        # 向左 (Pan)
        elif key == ord('a'):
            current_pan_angle += STEP_SIZE # 注意：根据云台安装方向，可能需要改为 -=
            print(f"向左: Pan={current_pan_angle}")

        # 向右 (Pan)
        elif key == ord('d'):
            current_pan_angle -= STEP_SIZE # 注意：根据云台安装方向，可能需要改为 +=
            print(f"向右: Pan={current_pan_angle}")

        # 限制角度在0-180度之间，防止舵机堵转
        current_pan_angle = max(0, min(180, current_pan_angle))
        current_tilt_angle = max(0, min(180, current_tilt_angle))

        # 发送最终指令给舵机
        pan_servo.angle = current_pan_angle
        tilt_servo.angle = current_tilt_angle

# 结束时关闭所有窗口
cv2.destroyAllWindows()
print("程序已退出。")
