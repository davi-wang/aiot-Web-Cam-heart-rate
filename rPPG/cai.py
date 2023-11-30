import cv2
import paho.mqtt.client as mqtt

# MQTT Broker 地址和端口
mqtt_server = "127.0.0.1"
mqtt_port = 1883
mqtt_user = "admin"
mqtt_password = "admin123"
mqtt_topic = "camera/image"


def main():
    # 创建 MQTT 客户端
    client = mqtt.Client()
    client.username_pw_set(username=mqtt_user, password=mqtt_password)

    # 连接到 MQTT Broker
    client.connect(mqtt_server, mqtt_port, 60)

    # 打开电脑默认摄像头
    cap = cv2.VideoCapture(0)  # 0表示第一个摄像头，如果有多个摄像头可以尝试使用1、2等来切换

    while True:
        ret, frame = cap.read()  # 读取视频流的一帧

        # 发布原始图像数据到 MQTT 主题
        ret, buffer = cv2.imencode('.jpg', frame)
        client.publish(mqtt_topic, bytearray(buffer))

        if cv2.waitKey(1) & 0xFF == ord('q'):  # 按 'q' 键退出循环
            break

    # 释放摄像头资源
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
