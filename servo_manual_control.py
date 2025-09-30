from adafruit_servokit import ServoKit

# --- 请根据您的实际接线修改这里的通道号 ---
TILT_CHANNEL = 0  # 垂直舵机 (上下)
PAN_CHANNEL = 1   # 水平舵机 (左右)
# -----------------------------------------

# 初始化PCA9685
kit = ServoKit(channels=16)

# 获取舵机对象
tilt_servo = kit.servo[TILT_CHANNEL]
pan_servo = kit.servo[PAN_CHANNEL]

# 设置脉宽范围以确保180度运动
tilt_servo.set_pulse_width_range(500, 2500)
pan_servo.set_pulse_width_range(500, 2500)

# 将舵机移动到初始的90度位置
tilt_servo.angle = 90
pan_servo.angle = 90

print("舵机手动校准工具已启动！")
print("---------------------------------")
print("使用说明:")
print("  - 输入 'p 角度' 来控制水平舵机 (pan)。例如: p 120")
print("  - 输入 't 角度' 来控制垂直舵机 (tilt)。例如: t 75")
print("  - 角度范围是 0 到 180。")
print("  - 输入 'q' 或按 Ctrl+C 退出程序。")
print("---------------------------------")

while True:
    try:
        # 获取用户输入
        command = input("请输入指令 (例如 'p 90' 或 't 45'): ")

        # 退出条件
        if command.lower() == 'q':
            print("退出程序。")
            break

        # 解析指令
        parts = command.split()
        if len(parts) != 2:
            print("指令格式错误！请重新输入。")
            continue

        servo_choice = parts[0].lower()
        angle_value = float(parts[1])

        # 检查角度范围
        if not (0 <= angle_value <= 180):
            print("角度超出范围！请输入0到180之间的数字。")
            continue

        # 控制舵机
        if servo_choice == 'p':
            pan_servo.angle = angle_value
            print(f"水平舵机已移动到 {angle_value} 度。")
        elif servo_choice == 't':
            tilt_servo.angle = angle_value
            print(f"垂直舵机已移动到 {angle_value} 度。")
        else:
            print("舵机选择错误！请输入 'p' 或 't'。")

    except ValueError:
        print("角度值无效！请输入一个数字。")
    except KeyboardInterrupt:
        print("\n程序被中断。退出。")
        break
    except Exception as e:
        print(f"发生未知错误: {e}")
        break

# 程序结束时，可以选择让舵机停留在最后位置，或者归中
# pan_servo.angle = 90
# tilt_servo.angle = 90
# print("舵机已归中。")
