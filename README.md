# portfolio
ロボットエンジニアを目指す未経験者のポートフォリオです。 学生時代の研究成果や、就業後に制作したプロジェクトをまとめています。

**English:**
This is a portfolio for someone who wants to become a robotics engineer. It shows projects from school and projects I made after starting work.

# 1.物体検出アプリ（YOLOv12）

## ℹ️ アプリの概要
本アプリは、YOLOv12を用いて画像内の物体を検出し、結果をWebブラウザ上に表示するアプリです。ロボットが環境を認識する視覚として開発しました。
**補足:**アップロードした画像は保存されません。

## ⚙️ 使用技術
- Python
- Streamlit
- OpenCV
- Ultralytics YOLOv12

## 🔄 機能
- 画像ファイルのアップロード
- YOLOv12による物体検出
- アノテーション画像の表示
- ラベルごとの予測精度の表示

## 🚀 実行方法
# 環境構築からアプリの起動まで一括で実行
```bash
#下記を実行後、1を選択してサーバーを構築するか、または2を選択して実行
sh ./setup.sh portfolio
```

# アプリの起動(個別に)
```bash
streamlit run app.py
