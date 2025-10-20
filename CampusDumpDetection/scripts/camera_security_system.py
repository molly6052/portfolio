#! /usr/bin/python

# =========================
# 必要なライブラリのインポート
# =========================
from imutils.video import VideoStream, FPS
import face_recognition  # 顔認識用（今回は未使用）
import imutils
import pickle
import datetime
import requests  # LINE通知用

# TensorFlow Lite / OpenCV / 基本ライブラリ
import argparse
import sys
import numpy as np
import cv2
import time
from time import sleep
import multiprocessing as mp
try:
    from tflite_runtime.interpreter import Interpreter  # Raspberry Piなど軽量環境用
except:
    import tensorflow as tf  # PCなどフル版TensorFlow用

# =========================
# LINE通知を送信する関数
# =========================
def send_message(Discovery_time):
    """
    指定した時刻の画像をLINE Notifyで送信する
    """
    url = "https://notify-api.line.me/api/notify" 
    token = "lH5OCpCNwTMQD7SIJk3lflA0IqNkKjHjk8m8N52x2Fc"  # LINE Notify トークン
    headers = {"Authorization" : "Bearer "+ token}
    # 対象画像を指定して送信
    files = {'imageFile': open("/home/idd/Desktop/ras-img/{}.jpg".format(Discovery_time), "rb")}
    message =  (Discovery_time,"侵入者あり")
    payload = {"message" :  message} 
    r = requests.post(url, headers = headers, params=payload, files=files)


# =========================
# グローバル変数（検出結果や描画設定）
# =========================
lastresults = None
processes = []
frameBuffer = None
results = None
fps = ""  # 表示用FPS
detectfps = ""
framecount = 0
detectframecount = 0
time1 = 0
time2 = 0

# 描画設定
box_color = (255, 128, 0)
box_thickness = 1
label_background_color = (125, 175, 75)
label_text_color = (255, 255, 255)
percentage = 0.0

# COCOクラスラベル
LABELS = [
    '???','person','bicycle','car','motorcycle','airplane','bus','train','truck','boat',
    'traffic light','fire hydrant','???','stop sign','parking meter','bench','bird','cat','dog','horse',
    'sheep','cow','elephant','bear','zebra','giraffe','???','backpack','umbrella','???',
    '???','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball','kite','baseball bat',
    'baseball glove','skateboard','surfboard','tennis racket','bottle','???','wine glass','cup','fork','knife',
    'spoon','bowl','banana','apple','sandwich','orange','broccoli','carrot','hot dog','pizza',
    'donut','cake','chair','couch','potted plant','bed','???','dining table','???','???',
    'toilet','???','tv','laptop','mouse','remote','keyboard','cell phone','microwave','oven',
    'toaster','sink','refrigerator','???','book','clock','vase','scissors','teddy bear','hair drier',
    'toothbrush'
]

# 不法投棄の多い家具・家電等、検出したいオブジェクト
osg = ['chair','bed','dining table','toilet','laptop','tv','remote','microwave','oven','toaster','sink','refrigerator']

# 画像調整用パラメータ（コントラスト、明るさ）
alpha = 2.0
beta = 30

# =========================
# TFLiteモデルで物体検出するクラス
# =========================
class ObjectDetectorLite():
    def __init__(self, model_path='detect.tflite', num_threads=12):
        """
        モデルを読み込み、TFLiteインタプリタを初期化
        """
        try:
            self.interpreter = Interpreter(model_path=model_path, num_threads=num_threads)
        except:
            self.interpreter = tf.lite.Interpreter(model_path=model_path, num_threads=num_threads)
        try:
            self.interpreter.allocate_tensors()
        except:
            pass
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def _boxes_coordinates(self, image, boxes, classes, scores, max_boxes_to_draw=5, min_score_thresh=.5):
        """
        検出結果（ボックス、クラス、スコア）から座標情報を抽出
        """
        if not max_boxes_to_draw:
            max_boxes_to_draw = boxes.shape[0]
        number_boxes = min(max_boxes_to_draw, boxes.shape[0])
        person_boxes = []

        for i in range(number_boxes):
            if scores is None or scores[i] > min_score_thresh:
                box = tuple(boxes[i].tolist())
                ymin, xmin, ymax, xmax = box
                _, im_height, im_width, _ = image.shape
                left, right, top, bottom = [int(z) for z in (xmin * im_width, xmax * im_width, ymin * im_height, ymax * im_height)]
                person_boxes.append([(left, top), (right, bottom), scores[i], LABELS[classes[i]]])
        return person_boxes

    def detect(self, image, threshold=0.1):
        """
        画像を入力としてTFLiteモデルで物体検出を実行
        """
        self.interpreter.set_tensor(self.input_details[0]['index'], image)
        start_time = time.time()
        self.interpreter.invoke()  # 推論
        stop_time = time.time()
        print("time: ", stop_time - start_time)

        # 推論結果を取得
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])
        num = self.interpreter.get_tensor(self.output_details[3]['index'])

        # ボックス座標を変換して返す
        return self._boxes_coordinates(image,
                                       np.squeeze(boxes[0]),
                                       np.squeeze(classes[0]+1).astype(np.int32),
                                       np.squeeze(scores[0]),
                                       min_score_thresh=threshold)

# =========================
# 検出結果を画像に重ねて描画
# =========================
def overlay_on_image(frames, object_infos, camera_width, camera_height):
    """
    検出された物体をフレームに描画し、FPS情報も追加
    """
    color_image = frames

    if object_infos is None:
        return color_image

    img_cp = color_image.copy()

    for obj in object_infos:
        # バウンディングボックス描画
        box_left, box_top = int(obj[0][0]), int(obj[0][1])
        box_right, box_bottom = int(obj[1][0]), int(obj[1][1])
        cv2.rectangle(img_cp, (box_left, box_top), (box_right, box_bottom), box_color, box_thickness)

        # ラベルとスコアを描画
        percentage = int(obj[2] * 100)
        label_text = f"{obj[3]} ({percentage}%)"
        label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        label_left = box_left
        label_top = max(1, box_top - label_size[1])
        label_right = label_left + label_size[0]
        label_bottom = label_top + label_size[1]
        cv2.rectangle(img_cp, (label_left-1, label_top-1), (label_right+1, label_bottom+1), label_background_color, -1)
        cv2.putText(img_cp, label_text, (label_left, label_bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.5, label_text_color, 1)

    # FPS情報を描画
    cv2.putText(img_cp, fps,       (camera_width-170,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (38,0,255), 1, cv2.LINE_AA)
    cv2.putText(img_cp, detectfps, (camera_width-170,30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (38,0,255), 1, cv2.LINE_AA)

    return img_cp

# =========================
# 人物や指定オブジェクトを検出したときの処理
# =========================
def cont_mov(res):
    """
    検出結果(res)を解析し、人や指定家具・家電等(osg)が同時に検出された場合にLINE通知
    """
    old = time.time()
    if not res:
        return res, old

    res1 = np.array(res, dtype=object)
    res1[:,3] = sorted(res1[:,3], key=LABELS.index)

    # person + 家具・家電等が同時に検出された場合
    if res1[0][3] == "person" and len(set(res1[:,3]) & set(osg)) != 0:
        dt_now = datetime.datetime.now()
        Discovery_time = dt_now.strftime('%Y年%m月%d日%H時%M分%S秒')
        print(Discovery_time)
        # 画像を保存してLINE通知
        cv2.imwrite(f"/home/idd/Desktop/ras-img/{Discovery_time}.jpg", imdraw)
        send_message(Discovery_time)
        count.append('send')
        return res, old
    else:
        return res, old

# =========================
# メイン処理
# =========================
if __name__ == '__main__':

    # コマンドライン引数を設定
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/mobilenet_ssd_v2_coco_quant_postprocess.tflite", help="Path of the detection model.")
    parser.add_argument("--usbcamno", type=int, default=0, help="USB Camera number.")
    parser.add_argument("--camera_type", default="usb_cam", help="set usb_cam or raspi_cam")
    parser.add_argument("--camera_width", type=int, default=640, help="width.")
    parser.add_argument("--camera_height", type=int, default=480, help="height.")
    parser.add_argument("--vidfps", type=int, default=150, help="Frame rate.")
    parser.add_argument("--num_threads", type=int, default=4, help="Threads.")
    args = parser.parse_args()

    # 引数を変数に格納
    model         = args.model
    usbcamno      = args.usbcamno
    camera_type   = args.camera_type
    camera_width  = args.camera_width
    camera_height = args.camera_height
    vidfps        = args.vidfps
    num_threads   = args.num_threads

    # =========================
    # カメラ初期化
    # =========================
    if camera_type == "usb_cam":
        cam = cv2.VideoCapture(usbcamno)
        cam.set(cv2.CAP_PROP_FPS, 30)
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)
        window_name = "USB Camera"
    elif camera_type == "raspi_cam":
        from picamera.array import PiRGBArray
        from picamera import PiCamera
        cam = PiCamera()
        cam.resolution = (camera_width, camera_height)
        stream =
