import pandas as pd
import numpy as np
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class BoatRaceAnalyzer:
    """
    競艇データ分析用クラス
    2024年の結果TXTファイルからデータを抽出し、人間が読みやすく機械学習に適した形式で出力
    """
    
    def __init__(self):
        # 会場マッピング
        self.venue_mapping = {
            '01': '桐生', '02': '戸田', '03': '江戸川', '04': '平和島', 
            '05': '多摩川', '06': '浜名湖', '07': '蒲郡', '08': '常滑',
            '09': '津', '10': '三国', '11': 'びわこ', '12': '住之江',
            '13': '尼崎', '14': '鳴門', '15': '丸亀', '16': '児島',
            '17': '宮島', '18': '徳山', '19': '下関', '20': '若松',
            '21': '芦屋', '22': '福岡', '23': '唐津', '24': '大村'
        }
        
        # データ格納用
        self.race_data = []
        self.odds_data = []
        
        # 正規表現パターン
        self.patterns = {
            'race_result': re.compile(r'(\d+)R\s+([1-6]-[1-6]-[1-6])\s+(\d+)'),
            'racer_info': re.compile(r'\s*(\d{2})\s+(\d)\s+(\d{4})\s+(.{8,12})\s+(\d{2})\s+(\d{1,3})\s+(\d\.\d{2})\s+(\d)\s+([\d\.+-]+)\s+([\d\.:]*)'),
            'odds_single': re.compile(r'単勝\s*(\d+)\s*(\d+\.\d+)'),
            'odds_place': re.compile(r'複勝\s*(\d+)\s*(\d+\.\d+)'),
            'odds_exacta': re.compile(r'2連単\s*(\d+)-(\d+)\s*(\d+\.\d+)'),
            'odds_quinella': re.compile(r'2連複\s*(\d+)-(\d+)\s*(\d+\.\d+)'),
            'odds_wide': re.compile(r'拡連複\s*(\d+)-(\d+)\s*(\d+\.\d+)'),
            'odds_trifecta': re.compile(r'3連複\s*(\d+)-(\d+)-(\d+)\s*(\d+\.\d+)'),
            'odds_trio': re.compile(r'3連単\s*(\d+)-(\d+)-(\d+)\s*(\d+\.\d+)')
        }
    
    def extract_date_from_filename(self, filename: str) -> str:
        """ファイル名から日付を抽出"""
        if len(filename) >= 7 and filename.upper().startswith('K'):
            year_code = filename[1:3]
            month_code = filename[3:5]
            day_code = filename[5:7]
            year = 2000 + int(year_code)
            month = int(month_code)
            day = int(day_code)
            return f"{year:04d}-{month:02d}-{day:02d}"
        return "unknown"
    
    def extract_venue_from_content(self, lines: List[str]) -> Tuple[str, str]:
        """ファイル内容から会場情報を抽出"""
        venue_patterns = list(self.venue_mapping.values())
        
        for line in lines[:30]:
            for venue in venue_patterns:
                if venue in line:
                    for code, name in self.venue_mapping.items():
                        if name == venue:
                            return code, venue
        return '', ''
    
    def extract_race_results(self, lines: List[str]) -> Dict[int, Dict]:
        """レース結果（着順）を抽出"""
        race_results = {}
        for line in lines:
            line = line.strip()
            match = self.patterns['race_result'].search(line)
            if match:
                race_number = int(match.group(1))
                finish_combination = match.group(2)
                positions = finish_combination.split('-')
                if len(positions) == 3:
                    race_results[race_number] = {
                        'first': int(positions[0]),
                        'second': int(positions[1]), 
                        'third': int(positions[2])
                    }
        return race_results
    
    def extract_odds_data(self, lines: List[str]) -> Dict[int, Dict]:
        """オッズデータを抽出"""
        odds_data = {}
        current_race = None
        
        for line in lines:
            line = line.strip()
            
            # レース番号の検出
            race_match = re.search(r'(\d+)R', line)
            if race_match:
                current_race = int(race_match.group(1))
                odds_data[current_race] = {}
                continue
            
            if current_race is None:
                continue
            
            # 各種オッズの抽出
            odds_types = [
                ('single', self.patterns['odds_single']),
                ('place', self.patterns['odds_place']),
                ('exacta', self.patterns['odds_exacta']),
                ('quinella', self.patterns['odds_quinella']),
                ('wide', self.patterns['odds_wide']),
                ('trifecta', self.patterns['odds_trifecta']),
                ('trio', self.patterns['odds_trio'])
            ]
            
            for odds_type, pattern in odds_types:
                match = pattern.search(line)
                if match:
                    if odds_type in ['single', 'place']:
                        boat_num = int(match.group(1))
                        odds_value = float(match.group(2))
                        odds_data[current_race][f'{odds_type}_{boat_num}'] = odds_value
                    elif odds_type in ['exacta', 'quinella', 'wide']:
                        boat1 = int(match.group(1))
                        boat2 = int(match.group(2))
                        odds_value = float(match.group(3))
                        odds_data[current_race][f'{odds_type}_{boat1}_{boat2}'] = odds_value
                    elif odds_type in ['trifecta', 'trio']:
                        boat1 = int(match.group(1))
                        boat2 = int(match.group(2))
                        boat3 = int(match.group(3))
                        odds_value = float(match.group(4))
                        odds_data[current_race][f'{odds_type}_{boat1}_{boat2}_{boat3}'] = odds_value
        
        return odds_data
    
    def process_single_file(self, file_path: Path) -> bool:
        """単一ファイルを処理"""
        print(f"処理中: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='shift_jis', errors='ignore') as f:
                lines = f.readlines()
            
            # 基本情報の抽出
            date_str = self.extract_date_from_filename(file_path.stem)
            venue_code, venue_name = self.extract_venue_from_content(lines)
            
            # レース結果とオッズデータの抽出
            race_results = self.extract_race_results(lines)
            odds_data = self.extract_odds_data(lines)
            
            # 選手データの抽出
            current_race = None
            for line_num, line in enumerate(lines):
                line_original = line
                line = line.strip()
                
                # レース番号の検出
                race_match = re.search(r'(\d+)R', line)
                if race_match:
                    current_race = int(race_match.group(1))
                
                # 選手情報の抽出
                if current_race and len(line_original) >= 40:
                    try:
                        match = self.patterns['racer_info'].match(line_original)
                        if match:
                            frame_number = int(match.group(1))
                            boat_number = int(match.group(2))
                            racer_id = int(match.group(3))
                            racer_name = match.group(4).strip()
                            age = int(match.group(5))
                            weight = int(match.group(6))
                            exhibition_time = float(match.group(7))
                            position = int(match.group(8))
                            start_timing = float(match.group(9)) if match.group(9) and match.group(9) != '.' else 0.0
                            race_time = match.group(10) if match.group(10) and match.group(10) != '.' else ""
                            
                            # 着順の計算
                            finish_position = 0
                            if current_race in race_results:
                                result = race_results[current_race]
                                if boat_number == result['first']:
                                    finish_position = 1
                                elif boat_number == result['second']:
                                    finish_position = 2
                                elif boat_number == result['third']:
                                    finish_position = 3
                                else:
                                    finish_position = 4  # 4着以下
                            
                            # オッズ情報の取得
                            race_odds = odds_data.get(current_race, {})
                            
                            # 基本データの保存
                            race_record = {
                                '日付': date_str,
                                'レース場コード': venue_code,
                                'レース場名': venue_name,
                                'レース番号': current_race,
                                '選手枠番': frame_number,
                                '選手ナンバー': boat_number,
                                'レーサーID': racer_id,
                                'レーサー名': racer_name,
                                '年齢': age,
                                '体重': weight,
                                '展示タイム': exhibition_time,
                                'スタートタイミング': start_timing,
                                'レースタイム': race_time,
                                '最終着順': finish_position
                            }
                            
                            # オッズ情報の追加
                            for odds_key, odds_value in race_odds.items():
                                race_record[f'オッズ_{odds_key}'] = odds_value
                            
                            self.race_data.append(race_record)
                            
                    except Exception as e:
                        continue
            
            return True
            
        except Exception as e:
            print(f"エラー: {file_path} - {e}")
            return False
    
    def process_files(self, directory_path: str, max_files: Optional[int] = None) -> int:
        """複数ファイルを処理"""
        directory = Path(directory_path)
        processed_count = 0
        
        # 2024年のファイルを検索
        for month in range(1, 13):
            if max_files and processed_count >= max_files:
                break
                
            month_dir = f"2024{month:02d}"
            month_path = directory / month_dir
            
            if month_path.exists():
                txt_files = list(month_path.glob("*.TXT"))
                if txt_files:
                    # 各月の最初のファイルを処理
                    first_file = sorted(txt_files)[0]
                    if self.process_single_file(first_file):
                        processed_count += 1
                        print(f"  -> 処理完了: {len(self.race_data)} レコード")
        
        print(f"\n処理完了: {processed_count} ファイル, {len(self.race_data)} レコード")
        return processed_count
    
    def get_human_readable_data(self) -> pd.DataFrame:
        """人間が読みやすい形式でデータを取得"""
        if not self.race_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.race_data)
        
        # データ型の最適化
        df['日付'] = pd.to_datetime(df['日付'])
        df['レース場コード'] = df['レース場コード'].astype('category')
        df['レース場名'] = df['レース場名'].astype('category')
        df['レーサー名'] = df['レーサー名'].astype('string')
        
        # 数値列の処理
        numeric_columns = ['レース番号', '選手枠番', '選手ナンバー', 'レーサーID', '年齢', '体重', 
                          '展示タイム', 'スタートタイミング', '最終着順']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_ml_ready_data(self) -> pd.DataFrame:
        """機械学習に適した形式でデータを取得"""
        df = self.get_human_readable_data()
        
        if df.empty:
            return df
        
        # 特徴量エンジニアリング
        df_ml = df.copy()
        
        # 日付特徴量の作成
        df_ml['年'] = df_ml['日付'].dt.year
        df_ml['月'] = df_ml['日付'].dt.month
        df_ml['日'] = df_ml['日付'].dt.day
        df_ml['曜日'] = df_ml['日付'].dt.dayofweek
        
        # カテゴリカル変数のエンコーディング
        df_ml['レース場コード_encoded'] = pd.Categorical(df_ml['レース場コード']).codes
        df_ml['レース場名_encoded'] = pd.Categorical(df_ml['レース場名']).codes
        
        # 数値特徴量の正規化
        numeric_features = ['年齢', '体重', '展示タイム', 'スタートタイミング']
        for feature in numeric_features:
            if feature in df_ml.columns:
                df_ml[f'{feature}_normalized'] = (df_ml[feature] - df_ml[feature].mean()) / df_ml[feature].std()
        
        # オッズ関連の特徴量
        odds_columns = [col for col in df_ml.columns if col.startswith('オッズ_')]
        for col in odds_columns:
            df_ml[f'{col}_normalized'] = (df_ml[col] - df_ml[col].mean()) / df_ml[col].std()
        
        return df_ml
    
    def save_analysis_results(self, output_dir: str = "boat_race_analysis"):
        """分析結果を保存"""
        if not self.race_data:
            print("保存するデータがありません")
            return
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 人間が読みやすい形式
        human_df = self.get_human_readable_data()
        human_file = output_path / "boat_race_human_readable.csv"
        human_df.to_csv(human_file, index=False, encoding='utf-8-sig')
        print(f"人間読みやすい形式保存: {human_file}")
        
        # 機械学習用形式
        ml_df = self.get_ml_ready_data()
        ml_file = output_path / "boat_race_ml_ready.csv"
        ml_df.to_csv(ml_file, index=False, encoding='utf-8-sig')
        print(f"機械学習用形式保存: {ml_file}")
        
        # 統計情報（JSONシリアライゼーション対応）
        stats = {
            'total_records': int(len(human_df)),
            'unique_venues': int(human_df['レース場名'].nunique()),
            'unique_dates': int(human_df['日付'].nunique()),
            'unique_racers': int(human_df['レーサーID'].nunique()),
            'venue_distribution': {str(k): int(v) for k, v in human_df['レース場名'].value_counts().items()},
            'date_range': {
                'start': str(human_df['日付'].min()),
                'end': str(human_df['日付'].max())
            },
            'columns': [str(col) for col in human_df.columns],
            'sample_data': []
        }
        
        # サンプルデータをJSON対応形式で準備
        sample_df = human_df.head(3)
        for _, row in sample_df.iterrows():
            sample_record = {}
            for col in sample_df.columns:
                value = row[col]
                if pd.isna(value):
                    sample_record[str(col)] = None
                elif hasattr(value, 'strftime'):  # datetime型の場合
                    sample_record[str(col)] = str(value)
                elif hasattr(value, 'item'):  # numpy型の場合
                    sample_record[str(col)] = value.item()
                else:
                    sample_record[str(col)] = str(value)
            stats['sample_data'].append(sample_record)
        
        stats_file = output_path / "analysis_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"統計情報保存: {stats_file}")
        
        # データ概要の表示
        print("\n=== データ概要 ===")
        print(f"総レコード数: {len(human_df)}")
        print(f"レース場数: {human_df['レース場名'].nunique()}")
        print(f"日付範囲: {human_df['日付'].min()} ～ {human_df['日付'].max()}")
        print(f"カラム数: {len(human_df.columns)}")
        
        print("\n=== サンプルデータ ===")
        print(human_df.head())
        
        return human_df, ml_df

def main():
    """デモンストレーション"""
    print("=== 競艇データ分析システム ===")
    
    analyzer = BoatRaceAnalyzer()
    
    # サンプルファイルの処理（実際のパスに変更してください）
    kekkaf_dir = r"G:\マイドライブ\BR_python\kekkaf"
    
    # ファイル処理
    processed_count = analyzer.process_files(kekkaf_dir, max_files=5)
    
    if processed_count > 0:
        # 結果の保存
        human_df, ml_df = analyzer.save_analysis_results()
        
        print("\n=== 分析完了 ===")
        print("以下のファイルが生成されました:")
        print("- boat_race_human_readable.csv (人間が読みやすい形式)")
        print("- boat_race_ml_ready.csv (機械学習用形式)")
        print("- analysis_stats.json (統計情報)")
    else:
        print("ファイル処理に失敗しました")

if __name__ == "__main__":
    main()
