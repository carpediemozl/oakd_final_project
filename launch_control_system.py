import subprocess
import time
import os

# --- 配置区域 ---
# 获取当前虚拟环境的Python解释器路径
VENV_PYTHON = os.path.join(os.environ.get("VIRTUAL_ENV", "."), "bin", "python3")

# 定义两个“士兵”脚本的路径
VIDEO_SCRIPT = os.path.expanduser("~/oakd_final_project/depthai-python/examples/ColorCamera/rgb_preview.py")
CONTROL_SCRIPT = os.path.expanduser("~/oakd_final_project/wasd_controller.py")
# ----------------

print("正在启动OAK-D一体化控制系统...")
print(f"使用的Python解释器: {VENV_PYTHON}")

# 检查脚本文件是否存在
if not os.path.exists(VIDEO_SCRIPT):
    print(f"错误: 视频脚本未找到! 路径: {VIDEO_SCRIPT}")
    exit()
if not os.path.exists(CONTROL_SCRIPT):
    print(f"错误: 控制脚本未找到! 路径: {CONTROL_SCRIPT}")
    exit()

# 定义启动命令
# 'gnome-terminal' 是树莓派桌面默认的终端程序
launch_video_cmd = ['lxterminal', '-e', f'bash -c "{VENV_PYTHON} {VIDEO_SCRIPT}; exec bash"']
launch_control_cmd = ['lxterminal', '-e', f'bash -c "{VENV_PYTHON} {CONTROL_SCRIPT}; exec bash"']
video_process = None
control_process = None

try:
    print("正在启动OAK-D视频窗口...")
    video_process = subprocess.Popen(launch_video_cmd)
    time.sleep(3) # 等待视频窗口启动

    print("正在启动WASD控制器...")
    control_process = subprocess.Popen(launch_control_cmd)

    print("\n控制系统已启动！")
    print("您现在应该能看到一个视频窗口和另一个控制器终端。")
    print("请在'WASD控制器'终端中按键来控制云台。")
    print("要关闭所有程序，请关闭本'总指挥'终端窗口，或按 Ctrl+C。")

    # 等待进程结束
    control_process.wait()

except KeyboardInterrupt:
    print("\n接收到中断信号，正在关闭所有进程...")
finally:
    if video_process:
        video_process.terminate()
    if control_process:
        control_process.terminate()
    print("所有进程已关闭。")
