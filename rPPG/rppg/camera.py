import time

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
import paho.mqtt.client as mqtt
import io
from PIL import Image
import numpy as np

class Camera(QThread):
    """Wraps cv2.VideoCapture and emits Qt signals with frames in RGB format.

    The :py:`run` function launches a loop that waits for new frames in
    the VideoCapture and emits them with a `new_frame` signal.  Calling
    :py:`stop` stops the loop and releases the camera.
    """

    frame_received = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        """Initialize Camera instance

        Args:
            video (int or string): ID of camera or video filename
            parent (QObject): parent object in Qt context
            limit_fps (float): force FPS limit, delay read if necessary.
        """

        QThread.__init__(self, parent=parent)
        mqtt_server = "8.134.199.5"
        mqtt_port = 1883
        mqtt_user = "admin"
        mqtt_password = "HKUaiot7310"
        mqtt_topic = "camera/image"

        self.client = mqtt.Client()
        self.client.username_pw_set(mqtt_user, mqtt_password)
        
        def on_message(client, userdata, message):

            try:
                # 解析收到的图像数据
                
                image_data = message.payload
                image = Image.open(io.BytesIO(image_data))
                self.frame_received.emit(np.array(image))
                image.save("received_image.jpg")

            except Exception as e:
                print("Error processing image:", str(e))

        self.client.on_message = on_message    

        # 连接到MQTT服务器
        self.client.connect(mqtt_server, mqtt_port, keepalive=60)

        # 订阅MQTT主题
        self.client.subscribe(mqtt_topic, qos=0)
        self._running = False


    def run(self):
        # 开始监听MQTT消息
        self._running = True
        self.client.loop_forever()
        
        # while self._running:
        #     ret, frame = self._cap.read()
        #     last_time = time.perf_counter()

        #     if not ret:
        #         self._running = False
        #         raise RuntimeError("No frame received")
        #     else:
        #         self.frame_received.emit(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        #     while (time.perf_counter() - last_time) < self._delay:
        #         time.sleep(0.001)

    def stop(self):
        self._running = False
        time.sleep(0.1)
        self._cap.release()
