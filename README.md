# 競艇データ分析システム (Boat Race Dataset)

2024年の競艇結果TXTファイルからデータを抽出し、人間が読みやすく機械学習に適した形式で出力するシステムです。

## 機能

### データ抽出機能
- **レース場情報**: 会場コード、会場名
- **選手情報**: 枠番、選手ナンバー、レーサーID、選手名、年齢、体重
- **タイム情報**: 展示タイム、スタートタイミング、レースタイム
- **結果情報**: 最終着順
- **オッズ情報**: 単勝、複勝、2連単、2連複、拡連複、3連複、3連単

### 出力形式

#### 1. 人間が読みやすい形式 (CSV)
- 日本語カラム名
- 適切なデータ型
- 直感的な構造

#### 2. 機械学習用形式 (CSV)
- 数値特徴量の正規化
- カテゴリカル変数のエンコーディング
- 日付から派生した特徴量
- オッズデータの正規化

## 使用方法

### 基本的な使用方法

```python
from src.boat_race_analyzer import BoatRaceAnalyzer

# アナライザーの初期化
analyzer = BoatRaceAnalyzer()

# ファイルの処理
processed_count = analyzer.process_files("path/to/kekkaf/directory", max_files=10)

# 人間が読みやすい形式でデータを取得
human_readable_df = analyzer.get_human_readable_data()

# 機械学習用形式でデータを取得
ml_ready_df = analyzer.get_ml_ready_data()

# 結果の保存
human_df, ml_df = analyzer.save_analysis_results("output_directory")
```

### デモンストレーション

```bash
python demo_analysis.py
```

## ファイル構成

```
boatdataset/
├── src/
│   ├── boat_race_analyzer.py  # メインの分析クラス
│   ├── convert.py             # 既存の変換処理
│   └── utils.py               # ユーティリティ関数
├── demo_analysis.py           # デモンストレーション用スクリプト
├── dataset.py                 # 既存のデータセット処理
└── README.md                  # このファイル
```

## 出力ファイル

### 1. boat_race_human_readable.csv
人間が読みやすい形式のデータ
- 日本語カラム名
- 適切なデータ型
- 直感的な構造

### 2. boat_race_ml_ready.csv
機械学習用のデータ
- 正規化された数値特徴量
- エンコーディングされたカテゴリカル変数
- 派生特徴量

### 3. analysis_stats.json
データの統計情報
- 総レコード数
- ユニークな値の数
- 分布情報
- サンプルデータ

## データ形式の詳細

### 人間が読みやすい形式の特徴
- **日本語カラム名**: 直感的で理解しやすい
- **適切なデータ型**: 日付、数値、文字列が適切に型付け
- **構造化**: 論理的な順序でカラムが配置

### 機械学習用形式の特徴
- **数値特徴量の正規化**: 平均0、標準偏差1に正規化
- **カテゴリカル変数のエンコーディング**: 数値コードに変換
- **派生特徴量**: 日付から年、月、日、曜日を抽出
- **オッズデータの正規化**: オッズ値も正規化

## 分析用途

### 推奨される分析
1. **着順予測モデル**: 機械学習による着順予測
2. **オッズ分析**: オッズの変動パターン分析
3. **レーサー分析**: 個人別パフォーマンス分析
4. **レース場分析**: 会場別の特性分析
5. **時系列分析**: 時間経過による変化の分析

### 機械学習での活用例
```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# 機械学習用データの読み込み
df = pd.read_csv('boat_race_ml_ready.csv')

# 特徴量とターゲットの分離
X = df.drop(['最終着順'], axis=1)
y = df['最終着順']

# 訓練・テストデータの分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# モデルの訓練
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 予測精度の評価
accuracy = model.score(X_test, y_test)
print(f"予測精度: {accuracy:.3f}")
```

## 注意事項

- ファイルパスは実際の環境に合わせて変更してください
- 大量のファイルを処理する場合は、`max_files`パラメータで制限してください
- エンコーディングはShift_JISを想定しています

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
