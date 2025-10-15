import streamlit as st
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
import time

model = YOLO("yolo12n.pt")

st.markdown("<div style='text-align: center;'><h1>物体検出アプリ</h1></div>", unsafe_allow_html=True)

st.divider()
st.write("## アプリの概要")
st.markdown("&emsp;本アプリは、YOLOv12を用いて画像内の物体を検出し、結果をWebブラウザ上に表示するアプリです。ロボットが環境を認識する視覚として開発しました。", unsafe_allow_html=True)
st.divider()
st.write("## 画像の準備")
st.write("")

uploaded_file = st.file_uploader("画像ファイルをアップロードしてください。", type=["jpg", "jpeg", "png"])

# フォームを2列（アップロード画像、アノテーション画像）に分ける
col1, col2 = st.columns(2)

if uploaded_file is not None:
    # OpenCVで画像読み込み
    file_bytes = np.frombuffer(uploaded_file.read(), np.uint8)
    ## BGRで読み込み
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Streamlitで表示する場合はRGBに変換
    uploaded_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    with col1:
        st.image(uploaded_img, caption="アップロード画像", width=None)

    # 推論ボタン
    if st.button("推論開始"):
        with st.spinner("データを処理中です..."):
            ## YOLO12で推論（RGB画像を入力）
            results = model(uploaded_img)
            time.sleep(1)
        st.success("処理が完了しました！")

        annotated_img = img.copy()

        labels = []
        for result in results:
            ## result.boxesはultralyticsのBoxesオブジェクト
            for box, score, cls in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                x1, y1, x2, y2 = map(int, box)
                label = f"{model.names[int(cls)]}: {score:.2f}"
                labels.append([model.names[int(cls)], round(score.item()*100,1)])
                ## バウンディングボックス表示
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                ## ラベル表示
                cv2.putText(
                    annotated_img, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                )

        # OpenCVにより、アノテーション画像をBGRからRGBに変換してStreamlitで表示
        with col2:
            st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB), caption="アノテーション画像", width=None)

        st.divider()
        st.write("## 物体検出の予測精度")
        df = pd.DataFrame(labels, columns=["クラス名", "予測精度"]).set_index("クラス名")

        # Streamlit上に表示
        st.dataframe(df.style.format({"予測精度": "{:.1f} %"}))
