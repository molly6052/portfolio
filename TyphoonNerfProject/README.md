# 神経放射輝度場を用いた台風航空機観測映像からの壁雲3Dモデリングおよび高度測量

本研究は、琉球大学大学院 理工学研究科 知能機械システムプログラムにおける修士論文研究として2024年3月に発表されました。 <br>（詳細は `docs/修士論文_盛拓矢.pdf` を参照）

---

## ○ 概要

本リポジトリは、**航空機から撮影された台風内部の映像**を用い、
深層学習モデル「**Instant Neural Graphics Primitives (Instant-NGP)**」によって台風の**目の壁雲を3D再構成**し、
さらに**雲頂高度を測定**した際のPythonコードを、当時の実装に基づいて整理・公開したものです。

特に工夫した点は以下の通りです。

* 航空機観測画像から得られたGPS情報と、COLMAPで推定されたカメラ座標を正確に対応付けることで、**地理的スケールを保持した3D再構成**を実現。
* Instant-NGPをGPU環境で動作させる際に、**CUDAおよびライブラリのバージョン整合性を最適化**し、学習を高速化。
* 点群処理ではCloudCompareを活用し、**衛星データ（JAXAひまわり）との高度比較を自動化**。

**Instant-NGPでVR化した台風**

![台風VR化](images/TyphoonVR.gif)

**補足:**

> **観測映像・航空機データ自体は、本リポジトリに含めません。**

---

## ○ 背景・目的

* 台風の勢力評価は主に衛星画像（赤外観測）から推定されるが、分解能の制約により**雲頂高度や内部構造の定量的把握が困難**。
* 本研究では、航空機観測で得た**台風の目内部の高解像度映像**を、NeRF技術により立体的に再構成し、
  **気象衛星の推定結果を補完できる新たな解析手法**を提案した。
* 目標は、「雲頂高度を写真測量的に求め、衛星観測値と比較して有効性を確認」すること。

---

## ○ 分析フロー

| 手順         | 処理内容                           | 使用モデル・手法           |
| ---------- | ------------------------------ | ------------------ |
| データ準備      | 航空機観測映像の抽出・整形                  | OpenCV, EXIF解析     |
| 1. 画像前処理   | 歪み補正・輝度調整・リサイズ                 | OpenCV, NumPy      |
| 2. カメラ座標推定 | COLMAPによるStructure from Motion | COLMAP             |
| 3. NeRF変換  | COLMAP結果をInstant-NGP形式へ変換      | `colmap2nerf2.py`  |
| 4. NeRF学習  | Instant-NGPで3D再構成              | NVIDIA Instant-NGP |
| 5. 点群生成    | NeRF出力からPLY点群作成                | Open3D             |
| 6. 測量解析    | CloudCompareで雲頂高度計測・誤差解析       | CloudCompare       |
| 評価         | 雲頂高度と衛星データ比較                   | JAXAひまわり・ドロップゾンデ観測 |

---

![手順](images/Workflow_TyphoonNeRF.png)

---

## ○ 結果

| 測定対象                 | 平均高度誤差       | 備考                     |
| -------------------- | ------------ | ---------------------- |
| 雲頂高度（Instant-NGP再構成） | **±100 m以内** | JAXAひまわり雲頂高度との比較で高精度一致 |
| 雄大雲（積乱雲上層構造）         | **融解層高度と同等** | ドロップゾンデ観測値（RH=100%）と一致 |

**NeRF再構成結果**

| Reconstruction                                              | CloudCompare測量結果                                            |
| ------------------------------------------------------ | ----------------------------------------------------------- |
| <img src="images/nerf_reconstruction.png" width="320"> | <img src="images/cloudcompare_measurement.png" width="360"> |

> NeRF再構成により、航空機視点から撮影された複数枚の画像のみで、
> 台風内部の立体構造を定量的に再現可能であることを示しました。

---

## ○ 実行環境（参考メモ）

* OS: Ubuntu / Linuxサーバー環境
* Python: 3.9
* GPU: NVIDIA RTX A5000
* 主要ライブラリ

  * 画像処理: `opencv-python`, `numpy`, `matplotlib`
  * 3D再構成: `COLMAP(SfM)`, `Instant-NGP`
  * 点群解析: `Open3D`, `CloudCompare`
  * データ整形: `json`, `pandas`
* JSON構成ファイル:

  * `base_cam.json` … 基本カメラパラメータ
  * `transforms.json` … COLMAP出力をNeRF形式へ変換したデータ

> ※ 本リポジトリは**観測映像非公開・再現実行不可**です。環境構成・手順は**参考資料**として掲載しています。

---

## ○ 今後の改善点

* [ ] **再構成精度の向上**：カメラパラメータ最適化とノイズ除去
* [ ] **自動位置合わせアルゴリズムの導入**：GPSデータとカメラ座標の自動整合
* [ ] **汎化モデルの構築**：他台風事例への適用・統合解析
* [ ] **リアルタイム推論**：GPU最適化による学習時間短縮

---

## ○ 引用・参考文献

* 盛 拓矢・北島 栄司・山田 広幸・伊藤 耕介・宮田 龍太（2024）
  「神経放射輝度場を用いた台風航空機観測映像からの壁雲3Dモデリングおよび高度測量」
  琉球大学大学院 理工学研究科 修士論文
* Müller, T. et al. (2022). *Instant Neural Graphics Primitives with a Multiresolution Hash Encoding.*
* JAXA ひまわりデータアーカイブ
* CloudCompare: [https://www.cloudcompare.org/](https://www.cloudcompare.org/)
* COLMAP: [https://colmap.github.io/](https://colmap.github.io/)

> ※ 研究背景・手法・結果の詳細は `docs/修士論文_盛拓矢.pdf` を参照してください。

---

## ○ フォルダ構成（提案）

```
typhoon_nerf_project/
├── preprocessing/
│   ├── 2点1と2点3の前処理.ipynb
│   └── 2点2の画像の前処理と2点3のカメラ座標推定.ipynb
├── modeling/
│   ├── 2点4のInstantNGPの学習.ipynb
│   ├── 2点5の点群作成.ipynb
│   └── 2点6のCloudCompareを用いた点群測量.ipynb
├── scripts/
│   ├── colmap2nerf2.py
│   └── run2.py
├── data/
│   ├── base_cam.json
│   └── transforms.json
├── docs/
│   └── 修士論文_盛拓矢.pdf
└── README.md
```
