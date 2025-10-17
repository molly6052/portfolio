# Judo VAR Support: 一本/時間切れの行動認識パイプライン（非公開データ前提）

本リポジトリは、柔道試合動画の「試合終了直前3秒」から、**一本（内股）**か**時間切れ**かを簡易分類するまでの実験コード群を、当時の実装に基づいて整理・公開したものです。  
※ コンペ提供データは**非公開**のため、**実行・再現は行いません**（ノートブックは**内容を変更せず**保存）。

---

## 背景・目的
- VAR（Video Assistant Referee）の発想を柔道に適用し、**俯瞰視点で審判を補助**する仕組みを目指しました。  
- 誤審の歴史的事例や、**選手の背中の付き方・速度・強さ**等の定性的基準を定量化する動機があります。  
- 手法は **審判の映り込み除去 → 選手のみ抽出 → 姿勢推定（関節系列） → 行動認識** の流れです。  
  （詳細は `00_docs/スポコン_Judo_2023.pdf` を参照）
  
---

## 全体フロー

```

[01_data_ops] 時間トリミング/向き振り分け/編集
│
▼
[02_inpainting_mask] 審判除去（LangSAM→XMem→ProPainter）
│
▼
[03_pose_estimation] DeepLabCutで関節座標抽出
│
▼
[04_skeleton_dataset] 骨格データセット生成 & 可視化(PySKL)
│
▼
[05_training_eval] MMAction2で学習・評価（2 or 3クラス）

```

- 3秒＝**約73フレーム**を入力系列とし、内股一本 vs 時間切れの2クラス、または内股一本/技あり/時間切れの3クラスを分類。  
- PDFの実験では、2クラスで **Acc ≈ 93.75%**（小規模実験）。今後は3クラス精度の改善が課題。  
  *出典：`00_docs/スポコン_Judo_2023.pdf` 内の結果・考察を参照。*

---

## ディレクトリと各スクリプトの役割・依存関係

- `01_data_ops/`
  - **動画を範囲時間だけカットする.ipynb**：終了時刻から3秒切り出しなど。
  - **動画向きで分ける.ipynb**：画角/向き等で分類し、以降の処理を安定化。
  - **動画データセット編集など.ipynb のコピー**：命名/整理のユーティリティ。
- `02_inpainting_mask/`
  - **マスク切り抜き動画.ipynb**：LangSAMで審判マスク生成 → XMemで追跡 → ProPainterで除去。
- `03_pose_estimation/`
  - **COLAB_maDLC_TrainNetwork_VideoAnalysis.ipynb**：DeepLabCutの学習/推定テンプレート（Colab前提）。
- `04_skeleton_dataset/`
  - **学習データ作成.ipynb**：CSVやフレームから骨格系列用データの準備。
  - **pysklでmmactionの骨格座標を可視化.ipynb**：PySKLで骨格結果の可視化・デバッグ。
- `05_training_eval/`
  - **mmaction_skeleton_based_dataset作成_学習_テストも含む.ipynb**：MMAction2ベースのデータ作成→学習→推論。
  - **柔道_学習_11月23日提出用.ipynb**：最終提出用の実験一式（2/3クラス設定の比較など）。

**依存関係（概略）**  
`01_data_ops` → `02_inpainting_mask` → `03_pose_estimation` → `04_skeleton_dataset` → `05_training_eval`

---

## 実行環境（参考・再現用メモ）

> ※ 本リポジトリは**データ非公開かつ実行不要**です。以下は**参考**としての環境メモです。

- OS: Google Colab / Linux 相当
- Python: 3.9–3.10 目安
- 主要ライブラリ
  - OpenMMLab: `mmcv`, `mmengine`, `mmaction2`, `mmpose`, `mmdet`
  - DeepLabCut 2.2+
  - PyTorch (CUDA対応推奨だがCPUでも可。ただし推論/学習時間増)
  - 画像/動画：`opencv-python`, `ffmpeg`
  - 可視化/解析：`numpy`, `pandas`, `matplotlib`
  - 前処理：LangSAM, XMem, ProPainter（研究用実装のため**セットアップが重い**点に注意）

---

## 再現に関する注意

- コンペ提供データは**非公開**であり、本リポジトリに含めません。
- **ノートブックの中身は一切変更していません**（`/content/drive/...` 等のパスや `!pip install` を含むセルは当時のまま残しています）。
- 実行を試みる場合は、以下に留意してください（推奨はしません）:
  - Google Drive/Colab 固有パスを**自環境に合わせて変更**。
  - `!pip install` は**バージョンピン止め**や**仮想環境**を推奨。
  - CUDAが無い環境では**GPU依存コード**（`.to("cuda")`など）を**CPUへ置換**が必要。

---

## 今後の改善点（ロードマップ）

- [ ] **パス依存の解消**：環境変数/設定ファイル化（例：`config/env.yaml`）
- [ ] **環境構築の自動化**：`requirements.txt` / `environment.yml` / `Dockerfile`
- [ ] **学習スクリプトの分離**：`src/`に共通関数を切り出し、ノートは実行ドキュメントへ
- [ ] **3クラス分類の精度改善**：データ拡張、画角の多様化、骨格以外の特徴融合
- [ ] **推論用スクリプト**：学習済み重みがある場合の**バッチ推論CLI**の整備

---

## 引用
- 研究背景・手法・結果の詳細は `00_docs/スポコン_Judo_2023.pdf` を参照してください。  
```
