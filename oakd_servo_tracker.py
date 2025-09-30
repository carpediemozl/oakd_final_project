import cv2
import depthai as dai
import time
from board import SCL, SDA
import busio
from adafruit_servokit import ServoKit

# --- 1. 配置 (CONFIG) ---
# [修改] 画面尺寸现在与AI模型的输入尺寸完全匹配
FRAME_WIDTH = 300
FRAME_HEIGHT = 300

PCA9685_CHANNELS = 16
PAN_CHANNEL = 1
TILT_CHANNEL = 0
PAN_MIN_ANGLE = 10
PAN_MAX_ANGLE = 170
TILT_MIN_ANGLE = 30
TILT_MAX_ANGLE = 100
PAN_P_GAIN = 0.03
TILT_P_GAIN = 0.04
CONFIDENCE_THRESHOLD = 0.5
# 【新增/修改】从校准脚本中获得的精确中心点
PAN_CENTER_ANGLE = 90.0
TILT_CENTER_ANGLE = 54.0
SMOOTHING_FACTOR = 0.15
# 【新增】误差死区，单位：像素。这是解决抖动的关键！
# 意思是如果人脸中心离画面中心的距离小于5个像素，我们就忽略不计
ERROR_DEADBAND_PIXELS = 20

# 【新增】目标丢失多少帧后才开始复位。这是一个“宽限期”。
# 假设摄像头约30fps，30帧就意味着目标消失1秒后才复位。
TARGET_LOST_THRESHOLD_FRAMES = 60

# --- 2. 舵机控制类 (Servo Controller Class) ---
class ServoController:
    # ... (这个类非常完美，无需任何改动) ...
    def __init__(self, channels, pan_ch, tilt_ch):
        try:
            self.i2c = busio.I2C(SCL, SDA)
            self.kit = ServoKit(channels=channels, i2c=self.i2c)
            print("PCA9685 初始化成功。")
        except ValueError:
            print("错误: 无法找到I2C设备。请运行 'sudo i2cdetect -y 1' 检查硬件连接。")
            exit()
        self.pan_servo = self.kit.servo[pan_ch]
        self.tilt_servo = self.kit.servo[tilt_ch]
        self.pan_servo.set_pulse_width_range(500, 2500)
        self.tilt_servo.set_pulse_width_range(500, 2500)
        self.current_pan_angle = PAN_CENTER_ANGLE
        self.current_tilt_angle = TILT_CENTER_ANGLE
    def center_all(self):
        self.set_pan(PAN_CENTER_ANGLE)
        self.set_tilt(TILT_CENTER_ANGLE)
        print("舵机已归中。")
    def set_pan(self, angle):
        self.current_pan_angle = max(PAN_MIN_ANGLE, min(PAN_MAX_ANGLE, angle))
        self.pan_servo.angle = self.current_pan_angle
    def set_tilt(self, angle):
        self.current_tilt_angle = max(TILT_MIN_ANGLE, min(TILT_MAX_ANGLE, angle))
        self.tilt_servo.angle = self.current_tilt_angle

# --- 3. OAK-D 管道设置 (OAK-D Pipeline Setup) ---
pipeline = dai.Pipeline()

cam_rgb = pipeline.create(dai.node.ColorCamera)
# [修改] 设置预览尺寸以匹配AI模型
cam_rgb.setPreviewSize(FRAME_WIDTH, FRAME_HEIGHT)
cam_rgb.setInterleaved(False)
cam_rgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

# [修改] 使用正确、更高级的 MobileNetDetectionNetwork 节点
detection_nn = pipeline.create(dai.node.MobileNetDetectionNetwork)
detection_nn.setBlobPath("face-detection-retail-0004_openvino_2022.1_4shave.blob")
# 这个高级节点拥有 setConfidenceThreshold 方法，我们可以再次使用它！
detection_nn.setConfidenceThreshold(CONFIDENCE_THRESHOLD)
detection_nn.setNumInferenceThreads(2)
detection_nn.input.setBlocking(False)

cam_rgb.preview.link(detection_nn.input)

xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

xout_nn = pipeline.create(dai.node.XLinkOut)
xout_nn.setStreamName("nn")
detection_nn.out.link(xout_nn.input)

# --- 4. 主程序 (Main Program) ---
if __name__ == "__main__":
    # 确保顶部的配置区已经定义了 TARGET_LOST_THRESHOLD_FRAMES = 30
    
    servos = ServoController(PCA9685_CHANNELS, PAN_CHANNEL, TILT_CHANNEL)
    servos.center_all()
    time.sleep(1)

    with dai.Device(pipeline) as device:
        q_rgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        q_nn = device.getOutputQueue(name="nn", maxSize=4, blocking=False)
        frame = None
        detections = []
        
        target_pan_angle = PAN_CENTER_ANGLE
        target_tilt_angle = TILT_CENTER_ANGLE
        
        # 【新增】目标丢失帧数计数器
        frames_since_target_lost = 0

        print("追踪程序启动，按 'q' 退出。")
        
        while True:
            in_rgb = q_rgb.tryGet()
            in_nn = q_nn.tryGet()

            if in_rgb is not None:
                frame = in_rgb.getCvFrame()

            if in_nn is not None:
                detections = in_nn.detections

            if frame is not None and len(detections) > 0:
                # --- 如果找到了目标 ---
                # 【修改】将丢失计数器清零
                frames_since_target_lost = 0
                
                target = detections[0]
                
                bbox = target.xmin, target.ymin, target.xmax, target.ymax
                target_x = int((bbox[0] + bbox[2]) * FRAME_WIDTH / 2)
                target_y = int((bbox[1] + bbox[3]) * FRAME_HEIGHT / 2)

                error_pan = target_x - (FRAME_WIDTH / 2)
                error_tilt = target_y - (FRAME_HEIGHT / 2)

                if abs(error_pan) < ERROR_DEADBAND_PIXELS: error_pan = 0
                if abs(error_tilt) < ERROR_DEADBAND_PIXELS: error_tilt = 0
                
                pan_adjustment = error_pan * PAN_P_GAIN
                tilt_adjustment = error_tilt * TILT_P_GAIN
                
                # 更新追踪的目标角度
                target_pan_angle = servos.current_pan_angle - pan_adjustment
                target_tilt_angle = servos.current_tilt_angle - tilt_adjustment

                # 绘制信息
                cv2.rectangle(frame, (int(bbox[0]*FRAME_WIDTH), int(bbox[1]*FRAME_HEIGHT)), 
                                     (int(bbox[2]*FRAME_WIDTH), int(bbox[3]*FRAME_HEIGHT)), (255, 0, 0), 2)
                cv2.circle(frame, (target_x, target_y), 5, (0, 255, 0), -1)

            else:
                # --- 如果没有找到目标 ---
                # 【修改】将丢失计数器加一
                frames_since_target_lost += 1

            # 【修改】只有当目标持续丢失超过阈值时，才执行复位
            if frames_since_target_lost > TARGET_LOST_THRESHOLD_FRAMES:
                target_pan_angle = PAN_CENTER_ANGLE
                target_tilt_angle = TILT_CENTER_ANGLE

            # 平滑逻辑保持不变，它会平滑地朝向最新的 target_angle 移动
            new_pan = servos.current_pan_angle + (target_pan_angle - servos.current_pan_angle) * SMOOTHING_FACTOR
            new_tilt = servos.current_tilt_angle + (target_tilt_angle - servos.current_tilt_angle) * SMOOTHING_FACTOR
            
            servos.set_pan(new_pan)
            servos.set_tilt(new_tilt)

            if frame is not None:
                cv2.putText(frame, f"Pan: {int(servos.current_pan_angle)} Tilt: {int(servos.current_tilt_angle)}", 
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.imshow("RGB Camera", frame)

            if cv2.waitKey(1) == ord('q'):
                break
    
    servos.center_all()
    cv2.destroyAllWindows()
    print("程序已退出。")