# ラズベリーパイを使った構内不法投棄に対する簡易監視システムの構築

本研究は、琉球大学工学部の卒業研究として実施された**「構内不法投棄監視システム」** の開発プロジェクトです。  
私はプログラミング未経験の後輩学生の研究テーマを技術面でサポートし、Raspberry PiとAIを用いた監視システムのプロトタイプを構築しました。

---

## ○ 概要

- **目的**: 夜間の不法投棄を低コストで検知  
- **コスト**: 約2万円  
- **特徴**: Raspberry Pi、赤外線カメラ、モバイルバッテリー、モバイルルーターをタッパー内に収納し、バッテリー駆動で運用  
- **成果**: 夜間でも人物を正確に検知、低コストでプロトタイプ完成  
- **開発期間**: 2022年6月〜2023年3月  

私は **技術補助（システム設計・実装・評価）** として開発に関わり、主に**機械学習モデルの選定・Raspberry Pi設定・SSH通信構築**などを担当しました。  

工夫した点としては、Raspberry Pi上で高精度な物体検出を実現するために、軽量化された **TensorFlow Lite の MobileNet モデル**を採用したことです。  

しかし、Raspberry Pi単体では夜間の物体検知が困難であったため、人物と特定の粗大ごみが同時にカメラに映った際に、学内の **Linuxサーバーへ画像をSSH送信**し、暗い画像を明るく補正できる深層学習モデルを活用して夜間でも安定した検知を可能にしました。

---

**補足**  
> - 最終的に稼働していた本番コードはLinuxサーバー上に保管されており、個人では保有していません。  
> - 本リポジトリに含まれるコードは、当時の試作版の一部です。  
> - 公開の目的は、「システム設計・開発の実績」を示すことです。

---

## ○ システムの概要

大学キャンパス内の不法投棄を検知するため、低コストで導入可能な監視システムを構築しました。  
Raspberry Pi と赤外線カメラを用いて人物を検知し、夜間を含めた不法投棄の早期把握を目指しました。  

学内では異動の時期になると深夜・早朝に不法投棄が発生し、撤去費用に年間200万円以上を要していました。  
常時人員を配置するのは困難なため、AIによる自動検知・通知システムを開発しました。

---

### 🖥 システム実機

![システム実機](images/HeardWare.png)

| 項目 | 内容 |
|------|------|
| デバイス | **Raspberry Pi 4 Model B** |
| OS | **Raspberry Pi OS (Bullseye)** |
| カメラ | **Arducam IMX519 オートフォーカスカメラ** |
| 通信 | **SSH経由でLinuxサーバーへ画像送信** |
| Linuxサーバー | **Ubuntu 20.04（低照度画像強化モデル実行）** |
| 通知 | **LINE Notify APIで警備担当へ通知** |
| 物体検出モデル | **TensorFlow Lite（MobileNetベース）** |

**実証実験**  
> 2023年3月に実施し、夜間でも人を正確に検知できることを確認。

---

## ○ 使用技術

- <img src="https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white"> 画像処理・通知スクリプト  
- <img src="https://img.shields.io/badge/-OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white"> カメラ制御・画像前処理  
- <img src="https://img.shields.io/badge/-TensorFlowLite-FF6F00?style=flat&logo=tensorflow&logoColor=white"> 物体検出（軽量推論）  
- <img src="https://img.shields.io/badge/-LowLightImageEnhancement-4F8EF7?style=flat"> 低照度画像強化（Dual Illumination）  
- <img src="https://img.shields.io/badge/-YOLOv8-00FFFF?style=flat&logo=yolo&logoColor=black"> 人物検出（サーバー側）  

---

## ○ システム機能

1. **カメラで撮影（赤外線対応）**  
2. **TensorFlow Lite による人物・ゴミ検知**  
   - 家具や家電などの対象物を検出  
3. **連続検知判定**  
   - 人物とゴミが同時に撮影された場合に画像を送信  
4. **低照度画像強化（夜間対応）**  
   - Linuxサーバーのフォルダを監視し、自動でPythonスクリプトを実行  
5. **YOLOv8 による人物検出（Linuxサーバー上）**  
6. **LINE Notify 通知**  
   - 検出画像を添付し、警備担当にリアルタイム通知  

---

### 概要図

![概要図](images/SystemView.jpg)

**セキュリティ上の問題**  
> 学内のセキュリティ上の問題により、Raspberry Piから外部ネットワークを経由したサーバーへの画像送信は制限されていたため、まず**LINE通知を送信**し、その後に**Linuxサーバーへ画像転送**を実施しました。

---

## ○ 担当

| 区分 | 内容 |
|------|------|
| **学生チーム（3名）** | システム実装・検証 |
| **指導教員** | 研究監修 |

---

## ○ 結果

- 夜間でも人物の検知に成功（明度補正後は精度向上）  
- 昼間は高精度に人物を認識  
- 約2万円という低コストでシステムのプロトタイプを構築  

**画像比較**

| Before | After |
|--------|-------|
| ![通知画像](images/notify_img.jpg) | ![低照度強化画像](images/notify_img_DUAL_g0.8_l0.15.jpg) |

---

## ○ 参考

- [Dual Illumination Estimation for Robust Exposure Correction (CVPR 2021)](https://arxiv.org/pdf/1910.13688)  
- [Python Implementation of Low-light Image Enhancement Techniques](https://github.com/pvnieo/Low-light-Image-Enhancement)  
- [TensorFlow Lite for Python – Official Guide](https://www.tensorflow.org/lite/guide/python?hl=ja)  
- [Arducam IMX519 Autofocus Camera Guide](https://www.arducam.com/docs/cameras-for-raspberry-pi/)  
- [Picamera2 Official Documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)
