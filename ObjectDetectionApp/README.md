# 物体検出アプリ（YOLOv12）

## ℹ️ アプリの概要
本アプリは、YOLOv12を用いて画像内の物体を検出し、結果をWebブラウザ上に表示するアプリです。ロボットが環境を認識する視覚として開発しました。

下記のリンクに本アプリを公開しています。

https://portfolio-nxdksjr5wg8pk28awedfy4.streamlit.app/

**補足:**
アップロードした画像は保存されません。

## ⚙️ 使用技術
- <img src="https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white">
- <img src="https://img.shields.io/badge/-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white">
- <img src="https://img.shields.io/badge/-OpenCV-3776AB?style=flat&logo=opencv&logoColor=white">
- <img src="https://img.shields.io/badge/-YOLO-3776AB?style=flat&logo=yolo&logoColor=white">

## 🔄 機能
- 画像ファイルのアップロード
- YOLOv12による物体検出
- アノテーション画像の表示
- ラベルごとの予測精度の表示

## 🚀 実行方法（ローカル環境）
# 環境構築からアプリの起動まで一括で実行
```bash
# 下記を実行後、1を選択してサーバーを構築するか、または2を選択して実行
sh ./setup.sh portfolio
```

# アプリの起動(個別に)
```bash
# Streamlitアプリを起動（ブラウザが自動で開きます）
streamlit run app.py
```

## 参考
- https://github.com/sunsmarterjie/yolov12?tab=readme-ov-file
- https://colab.research.google.com/github/roboflow-ai/notebooks/blob/main/notebooks/train-yolov12-object-detection-model.ipynb#scrollTo=BFOfDnL_Ia8Y
- https://docs.ultralytics.com/ja/models/yolo12/#overview
