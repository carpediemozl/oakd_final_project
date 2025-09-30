import time
import os

# 树莓派CPU温度文件的标准路径
# 这个文件里的值是千分之一摄氏度，例如 54321 代表 54.321°C
TEMP_FILE_PATH = "/sys/class/thermal/thermal_zone0/temp"

def get_cpu_temperature():
    """
    读取并解析树莓派的CPU温度。
    返回摄氏度为单位的浮点数，如果读取失败则返回 None。
    """
    try:
        with open(TEMP_FILE_PATH, 'r') as f:
            # 读取文件内容，移除末尾的换行符，并转换为浮点数
            temperature_milli_c = float(f.read().strip())
        
        # 将千分之一摄氏度转换为摄氏度
        return temperature_milli_c / 1000.0
    except (IOError, ValueError):
        # 如果文件读取失败或内容无法转换为数字，则返回 None
        return None

def main():
    """
    主函数，循环监控并显示温度。
    """
    print("--- 树莓派实时温度监控 ---")
    print("按 Ctrl+C 退出。")
    
    try:
        while True:
            cpu_temp = get_cpu_temperature()
            
            if cpu_temp is not None:
                # --- 可视化温度条 ---
                # 将温度映射到一个长度为25的条上 (每4°C增加一个'█')
                # 正常范围 (<= 60°C) 显示为绿色
                # 警告范围 (60°C - 80°C) 显示为黄色
                # 危险范围 (> 80°C) 显示为红色
                
                bar_length = int(cpu_temp / 4)
                bar = '█' * bar_length + ' ' * (25 - bar_length)
                
                # 根据温度设置颜色 (ANSI转义码)
                color_reset = "\033[0m"
                if cpu_temp <= 60:
                    color = "\033[92m" # 绿色
                elif cpu_temp <= 80:
                    color = "\033[93m" # 黄色
                else:
                    color = "\033[91m" # 红色

                # 使用 \r 将光标移回行首，实现单行刷新
                # 使用 :5.2f 格式化温度，使其占用5个字符宽度，保留2位小数，方便对齐
                print(f"\r{color}CPU 温度: {cpu_temp:5.2f}°C [{bar}]{color_reset}", end="")
            else:
                print("\r错误：无法读取温度。", end="")
            
            # 每秒刷新一次
            time.sleep(5)
            
    except KeyboardInterrupt:
        # 当用户按下 Ctrl+C 时，优雅地退出
        print("\n\n监控已停止。")

if __name__ == "__main__":
    main()