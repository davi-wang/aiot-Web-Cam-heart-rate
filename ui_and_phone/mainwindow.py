import cv2
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QGridLayout, QHBoxLayout, QLabel
import pyqtgraph as pg
import paho.mqtt.client as mqtt
#from umqtt.simple import MQTTClient
from rppg import RPPG
#import ujson
import requests
from . import helpers
# 云 MQTT 服务器配置
cloud_mqtt_host = "101.200.38.5"  # 云 MQTT 服务器地址
cloud_mqtt_port = 1883               # 云 MQTT 服务器端口
cloud_mqtt_topic = "heart"      # 云 MQTT 主题
cloud_mqtt_client = mqtt.Client()
cloud_mqtt_client.connect(cloud_mqtt_host, cloud_mqtt_port)


class MainWindow(QMainWindow):
    def __init__(self, app, rppg: RPPG, winsize=(600, 400), graphwin=150,
                 legend=False, blur_roi=-1):
        QMainWindow.__init__(self)
        self._app = app

        self.rppg = rppg
        self.rppg.rppg_updated.connect(self.on_rppg_updated)
        self.rppg.new_hr.connect(self.update_hr)

        self.graphwin = graphwin

        self.img = None
        self.lines = []
        self.plots = []
        self.auto_range_factor = 0.05

        self.hr_label = None

        self.init_ui(winsize=winsize)

        if legend:
            self._add_legend()
        self.blur_roi = blur_roi
        self.register_homeassistant_sensor()

    def init_ui(self, winsize):
        pg.setConfigOptions(antialias=True, foreground="k", background="w")
        self.setWindowTitle("AIOT PROJECT")
        self.setGeometry(0, 0, winsize[0], winsize[1])

        layout = pg.GraphicsLayoutWidget()
        self.setCentralWidget(layout)

        self.img = pg.ImageItem(axisOrder="row-major")
        vb = layout.addViewBox(col=0, row=0, rowspan=3, invertX=True,
                               invertY=True, lockAspect=True)
        vb.addItem(self.img)

        p1 = layout.addPlot(row=0, col=1, colspan=1)
        p1.hideAxis("left")
        p1.hideAxis("bottom")
        self.lines.append(p1.plot(pen=pg.mkPen("k", width=3)))
        self.plots.append(p1)

        if self.rppg.num_processors > 1:
            p2 = layout.addPlot(row=1, col=1, colspan=1)
            p2.hideAxis("left")
            p2.hideAxis("bottom")
            self.lines.append(p2.plot())
            self.plots.append(p2)
            for _ in range(2, self.rppg.num_processors):
                l, p = helpers.add_multiaxis_plot(p2, pen=pg.mkPen(width=3))
                self.lines.append(l)
                self.plots.append(p)
        for p in self.plots:
            p.disableAutoRange()

        self.hr_label = layout.addLabel(text="User-----heart rate-----:", row=4, col=0,
                                        size="40pt")

    def register_homeassistant_sensor(self):
        ha_api_url = "http://101.200.38.5:8123/api/states/sensor.heart_rate"
        sensor_state = 0
        sensor_attributes = {
            "unit_of_measurement": "bpm",
            "friendly_name": "Heart Rate",
        }
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI4NjdhOGIwZGI3ODg0NjEzOTM1NGIxZGUwY2EwMGQwNCIsImlhdCI6MTcwMTcwNzExMywiZXhwIjoyMDE3MDY3MTEzfQ.-VoSEQ0ujnuLRsffLv9PzA7YNBB7v7B1XGUAdBMKZk0",  # Replace with your Home Assistant access token
            "Content-Type": "application/json",
        }
        payload = {
            "state": sensor_state,
            "attributes": sensor_attributes,
        }
        response = requests.post(ha_api_url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Sensor entity registered successfully.")
        else:
            print("Failed to register sensor entity. Status code:", response.status_code)

    @staticmethod
    def _customize_legend(l, fs="10pt", margins=(5, 0, 5, 0)):
        l.layout.setContentsMargins(*margins)
        if fs is not None:
            for _, label in l.items:
                label.setText(label.text, size=fs)

    def _add_legend(self):
        layout = self.centralWidget()
        p = layout.addPlot(row=2, col=1)
        p.hideAxis("left")
        p.hideAxis("bottom")
        legend = pg.LegendItem(verSpacing=2)
        self._customize_legend(legend)
        legend.setParentItem(p)
        for l, n in zip(self.lines, self.rppg.processor_names):
            legend.addItem(l, n)

    def update_hr(self, hr):
        self.hr_label.setText("User-Heart rate={:5.1f} b/m".format(hr))
        if hr > 0:
            cloud_mqtt_client.publish(cloud_mqtt_topic, round(hr, 3))
            ha_api_url = "http://101.200.38.5:8123/api/states/sensor.heart_rate"
            sensor_state = round(hr, 3)
            headers = {
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI4NjdhOGIwZGI3ODg0NjEzOTM1NGIxZGUwY2EwMGQwNCIsImlhdCI6MTcwMTcwNzExMywiZXhwIjoyMDE3MDY3MTEzfQ.-VoSEQ0ujnuLRsffLv9PzA7YNBB7v7B1XGUAdBMKZk0",
                "Content-Type": "application/json",
            }
            payload = {
                "state": sensor_state,
            }
            response = requests.post(ha_api_url, json=payload, headers=headers)

            if response.status_code == 200:
                print("Sensor state updated successfully.")
            else:
                print("Failed to update sensor state. Status code:", response.status_code)

    def on_rppg_updated(self, results):
        ts = results.ts(self.graphwin)
        img = results.rawimg
        roi = results.roi
        roi.pixelate_face(img, self.blur_roi)
        roi.draw_roi(img)

        self.img.setImage(img)

        print("%.3f" % results.dt, results.roi, "FPS:", int(results.fps))

    def set_pen(self, color=None, width=1, index=0):
        if index > len(self.lines):
            raise IndexError(f"index {index} too high for {len(self.lines)} lines")
        pen = pg.mkPen(color or "k", width=width)
        self.lines[index].setPen(pen)

    def execute(self):
        self.show()
        self.rppg.start()
        return self._app.exec_()

    def closeEvent(self, event):
        self.rppg.finish()

    def keyPressEvent(self, e):
        if e.key() == ord("Q"):
            self.close()
