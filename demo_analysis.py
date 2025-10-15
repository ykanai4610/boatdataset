#!/usr/bin/env python3
"""
競艇データ分析デモンストレーション
2024年の結果TXTファイルからデータを抽出し、分析用の形式で出力する例
"""

import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.boat_race_analyzer import BoatRaceAnalyzer
import pandas as pd
import numpy as np

def demonstrate_data_extraction():
    """データ抽出のデモンストレーション"""
    print("=" * 60)
    print("競艇データ抽出・分析システム デモンストレーション")
    print("=" * 60)
    
    # アナライザーの初期化
    analyzer = BoatRaceAnalyzer()
    
    # サンプルファイルの処理
    print("\n1. データファイルの処理")
    print("-" * 30)
    
    # 実際のファイルパスに変更してください
    kekkaf_dir = r"G:\マイドライブ\BR_python\kekkaf"
    
    # ファイルが存在しない場合のサンプルデータ作成
    if not Path(kekkaf_dir).exists():
        print(f"指定されたディレクトリが存在しません: {kekkaf_dir}")
        print("サンプルデータでデモンストレーションを実行します...")
        create_sample_data(analyzer)
    else:
        # 実際のファイルを処理
        processed_count = analyzer.process_files(kekkaf_dir, max_files=3)
        if processed_count == 0:
            print("ファイル処理に失敗しました。サンプルデータでデモンストレーションを実行します...")
            create_sample_data(analyzer)
    
    # データ形式の表示
    print("\n2. 抽出されたデータ形式")
    print("-" * 30)
    
    if analyzer.race_data:
        # 人間が読みやすい形式
        human_df = analyzer.get_human_readable_data()
        print("【人間が読みやすい形式】")
        print(f"カラム数: {len(human_df.columns)}")
        print("カラム一覧:")
        for i, col in enumerate(human_df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\nサンプルデータ (最初の3行):")
        print(human_df.head(3).to_string())
        
        # 機械学習用形式
        ml_df = analyzer.get_ml_ready_data()
        print(f"\n【機械学習用形式】")
        print(f"カラム数: {len(ml_df.columns)}")
        print("追加された特徴量:")
        ml_only_cols = [col for col in ml_df.columns if col not in human_df.columns]
        for i, col in enumerate(ml_only_cols, 1):
            print(f"  {i:2d}. {col}")
    
    # 分析結果の保存
    print("\n3. 分析結果の保存")
    print("-" * 30)
    
    if analyzer.race_data:
        human_df, ml_df = analyzer.save_analysis_results("demo_output")
        
        # 統計情報の表示
        print("\n4. データ統計情報")
        print("-" * 30)
        print(f"総レコード数: {len(human_df)}")
        print(f"レース場数: {human_df['レース場名'].nunique()}")
        print(f"日付範囲: {human_df['日付'].min()} ～ {human_df['日付'].max()}")
        print(f"ユニークなレーサー数: {human_df['レーサーID'].nunique()}")
        
        # レース場別の分布
        print("\nレース場別レコード数:")
        venue_counts = human_df['レース場名'].value_counts()
        for venue, count in venue_counts.items():
            print(f"  {venue}: {count} レコード")
        
        # 着順の分布
        print("\n着順の分布:")
        finish_counts = human_df['最終着順'].value_counts().sort_index()
        for position, count in finish_counts.items():
            print(f"  {position}着: {count} レコード")
    
    print("\n" + "=" * 60)
    print("デモンストレーション完了")
    print("=" * 60)

def create_sample_data(analyzer):
    """サンプルデータを作成してデモンストレーション"""
    print("サンプルデータを作成中...")
    
    # サンプルデータの作成
    sample_data = [
        {
            '日付': '2024-01-15',
            'レース場コード': '05',
            'レース場名': '多摩川',
            'レース番号': 1,
            '選手枠番': 1,
            '選手ナンバー': 1,
            'レーサーID': 3501,
            'レーサー名': '佐々木康幸',
            '年齢': 28,
            '体重': 52,
            '展示タイム': 6.89,
            'スタートタイミング': 0.08,
            'レースタイム': '1.49.7',
            '最終着順': 1,
            'オッズ_single_1': 2.5,
            'オッズ_place_1': 1.8
        },
        {
            '日付': '2024-01-15',
            'レース場コード': '05',
            'レース場名': '多摩川',
            'レース番号': 1,
            '選手枠番': 2,
            '選手ナンバー': 2,
            'レーサーID': 3502,
            'レーサー名': '田中太郎',
            '年齢': 30,
            '体重': 55,
            '展示タイム': 6.95,
            'スタートタイミング': 0.12,
            'レースタイム': '1.50.1',
            '最終着順': 2,
            'オッズ_single_2': 3.2,
            'オッズ_place_2': 2.1
        },
        {
            '日付': '2024-01-15',
            'レース場コード': '05',
            'レース場名': '多摩川',
            'レース番号': 1,
            '選手枠番': 3,
            '選手ナンバー': 3,
            'レーサーID': 3503,
            'レーサー名': '山田花子',
            '年齢': 26,
            '体重': 50,
            '展示タイム': 6.92,
            'スタートタイミング': 0.05,
            'レースタイム': '1.50.3',
            '最終着順': 3,
            'オッズ_single_3': 4.1,
            'オッズ_place_3': 2.8
        },
        {
            '日付': '2024-01-15',
            'レース場コード': '05',
            'レース場名': '多摩川',
            'レース番号': 2,
            '選手枠番': 1,
            '選手ナンバー': 1,
            'レーサーID': 3504,
            'レーサー名': '鈴木一郎',
            '年齢': 32,
            '体重': 58,
            '展示タイム': 6.88,
            'スタートタイミング': 0.15,
            'レースタイム': '1.49.5',
            '最終着順': 1,
            'オッズ_single_1': 1.9,
            'オッズ_place_1': 1.5
        },
        {
            '日付': '2024-01-15',
            'レース場コード': '05',
            'レース場名': '多摩川',
            'レース番号': 2,
            '選手枠番': 2,
            '選手ナンバー': 2,
            'レーサーID': 3505,
            'レーサー名': '高橋次郎',
            '年齢': 29,
            '体重': 53,
            '展示タイム': 6.91,
            'スタートタイミング': 0.08,
            'レースタイム': '1.50.0',
            '最終着順': 2,
            'オッズ_single_2': 2.8,
            'オッズ_place_2': 1.9
        }
    ]
    
    analyzer.race_data = sample_data
    print(f"サンプルデータ {len(sample_data)} レコードを作成しました")

def show_usage_examples():
    """使用例の表示"""
    print("\n" + "=" * 60)
    print("使用例")
    print("=" * 60)
    
    print("""
# 基本的な使用方法

from src.boat_race_analyzer import BoatRaceAnalyzer

# 1. アナライザーの初期化
analyzer = BoatRaceAnalyzer()

# 2. ファイルの処理
processed_count = analyzer.process_files("path/to/kekkaf/directory", max_files=10)

# 3. 人間が読みやすい形式でデータを取得
human_readable_df = analyzer.get_human_readable_data()

# 4. 機械学習用形式でデータを取得
ml_ready_df = analyzer.get_ml_ready_data()

# 5. 結果の保存
human_df, ml_df = analyzer.save_analysis_results("output_directory")

# 6. データの確認
print(human_readable_df.head())
print(ml_ready_df.describe())
""")

def show_data_formats():
    """データ形式の説明"""
    print("\n" + "=" * 60)
    print("データ形式の説明")
    print("=" * 60)
    
    print("""
【人間が読みやすい形式の特徴】
- 日本語のカラム名で直感的
- 日付は YYYY-MM-DD 形式
- 数値データは適切な型に変換
- カテゴリカルデータは文字列として保持

【機械学習用形式の特徴】
- 数値特徴量の正規化
- カテゴリカル変数のエンコーディング
- 日付から派生した特徴量（年、月、日、曜日）
- オッズデータの正規化
- 欠損値の適切な処理

【抽出される主要データ項目】
1. レース場情報（コード、名前）
2. 選手情報（枠番、ナンバー、レーサーID、名前、年齢、体重）
3. タイム情報（展示タイム、スタートタイミング、レースタイム）
4. 結果情報（最終着順）
5. オッズ情報（単勝、複勝、2連単、2連複、拡連複、3連複、3連単）

【推奨される分析用途】
- 着順予測モデルの構築
- オッズ分析
- レーサー別パフォーマンス分析
- レース場別特性分析
- 時系列分析
""")

if __name__ == "__main__":
    # デモンストレーションの実行
    demonstrate_data_extraction()
    
    # 使用例の表示
    show_usage_examples()
    
    # データ形式の説明
    show_data_formats()
