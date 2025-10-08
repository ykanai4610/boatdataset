import pandas as pd 
import re
import json
from pathlib import Path

class QuickKekkaf2024Processor:
    def __init__(self):
        self.venue_mapping = {
            '01': '桐生', '02': '戸田', '03': '江戸川', '04': '平和島', 
            '05': '多摩川', '06': '浜名湖', '07': '蒲郡', '08': '常滑',
            '09': '津', '10': '三国', '11': 'びわこ', '12': '住之江',
            '13': '尼崎', '14': '鳴門', '15': '丸亀', '16': '児島',
            '17': '宮島', '18': '徳山', '19': '下関', '20': '若松',
            '21': '芦屋', '22': '福岡', '23': '唐津', '24': '大村'
        }
        self.race_data = []
    
    def extract_venue_from_line(self, lines):
        """会場情報を抽出"""
        venue_patterns = ['多摩川', '浜名湖', '蒲郡', '常滑', '津', '三国',
                         'びわこ', '住之江', '尼崎', '鳴門', '丸亀', '児島',
                         '宮島', '徳山', '下関', '若松', '芦屋', '福岡',
                         '唐津', '大村', '桐生', '戸田', '江戸川', '平和島']
        
        for line in lines[:30]:
            for venue in venue_patterns:
                if venue in line:
                    # 逆引きで会場コードを取得
                    for code, name in self.venue_mapping.items():
                        if name == venue:
                            return code, venue
        return '', ''
    
    def process_file(self, file_path):
        """単一ファイルを処理"""
        print(f"処理中: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='shift_jis', errors='ignore') as f:
                lines = f.readlines()
            
            # 日付抽出
            filename = file_path.stem
            if len(filename) >= 7 and filename.upper().startswith('K'):
                year_code = filename[1:3]  # 24
                month_code = filename[3:5]  # 01-12
                day_code = filename[5:7]   # 01-31
                year = 2000 + int(year_code)
                month = int(month_code)
                day = int(day_code)
                date_str = f"{year:04d}-{month:02d}-{day:02d}"
            else:
                date_str = "unknown"
            
            # 会場情報
            venue_code, venue_name = self.extract_venue_from_line(lines)
            
            # レース結果（着順）を解析
            race_results = {}
            for line in lines:
                line = line.strip()
                race_result_match = re.search(r'(\d+)R\s+([1-6]-[1-6]-[1-6])\s+(\d+)', line)
                if race_result_match:
                    race_number = int(race_result_match.group(1))
                    finish_combination = race_result_match.group(2)
                    positions = finish_combination.split('-')
                    if len(positions) == 3:
                        race_results[race_number] = {
                            'first': int(positions[0]),
                            'second': int(positions[1]), 
                            'third': int(positions[2])
                        }
            
            # 選手データを解析
            current_race = None
            for line_num, line in enumerate(lines):
                line_original = line
                line = line.strip()
                
                # レース番号の検出
                race_match = re.search(r'(\d+)R', line)
                if race_match:
                    current_race = int(race_match.group(1))
                
                # 選手情報の行を検出（日本語文字エンコード対応）
                if current_race and len(line_original) >= 40:
                    try:
                        # 正規表現で選手データを抽出
                        # 例: "  01  1 3501 佐々木  康幸 50   12  6.89   1    0.08     1.49.7"
                        match = re.match(r'\s*(\d{2})\s+(\d)\s+(\d{4})\s+(.{8,12})\s+(\d{2})\s+(\d{1,3})\s+(\d\.\d{2})\s+(\d)\s+([\d\.+-]+)\s+([\d\.:]*)', line_original)
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
                            
                            # 着順を計算
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
                            
                            # データを統合
                            self.race_data.append({
                                'date': date_str,
                                'venue_code': venue_code,
                                'venue_name': venue_name,
                                'race_number': current_race,
                                'boat_number': boat_number,     # 艇番
                                'racer_id': racer_id,          # レーサーNo
                                'racer_name': racer_name,
                                'age': age,
                                'weight': weight,
                                'exhibition_time': exhibition_time,  # 展示タイム
                                'start_timing': start_timing,        # スタートタイミング
                                'race_time': race_time,              # レースタイム
                                'finish_position': finish_position,  # 着順
                                'frame_number': frame_number
                            })
                    except Exception as e:
                        continue
                        
            return True
            
        except Exception as e:
            print(f"エラー: {file_path} - {e}")
            return False
    
    def process_sample_files(self, kekkaf_dir, max_files=10):
        """サンプルファイルを処理"""
        kekkaf_path = Path(kekkaf_dir)
        processed_count = 0
        
        # 2024年の各月から少しずつファイルを処理
        for month in range(1, 13):
            if processed_count >= max_files:
                break
                
            month_dir = f"2024{month:02d}"
            month_path = kekkaf_path / month_dir
            
            if month_path.exists():
                txt_files = list(month_path.glob("*.TXT"))
                if txt_files:
                    # 各月の最初のファイルを処理
                    first_file = sorted(txt_files)[0]
                    if self.process_file(first_file):
                        processed_count += 1
                        print(f"  -> 処理完了: {len(self.race_data)} レコード")
        
        print(f"\n処理完了: {processed_count} ファイル, {len(self.race_data)} レコード")
        return processed_count > 0
    
    def save_sample_dataset(self, output_dir="kekkaf_2024_sample"):
        """サンプルデータセットを保存"""
        if not self.race_data:
            print("保存するデータがありません")
            return
            
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # DataFrame作成
        df = pd.DataFrame(self.race_data)
        
        # メインデータセット（要求された項目のみ）
        main_columns = [
            'date', 'venue_code', 'venue_name',    # レース場
            'race_number', 'finish_position',      # 着順
            'boat_number',                         # 艇番
            'racer_id',                           # レーサーNo
            'racer_name',                         # 選手名（参考）
            'exhibition_time',                    # 展示タイム
            'start_timing',                       # スタートタイミング
            'race_time'                          # レースタイム
        ]
        
        main_dataset = df[main_columns].copy()
        main_file = output_path / "kekkaf_2024_main_dataset.csv"
        main_dataset.to_csv(main_file, index=False, encoding='utf-8-sig')
        print(f"メインデータセット保存: {main_file}")
        print(f"レコード数: {len(main_dataset)}")
        
        # データサンプル表示
        print("\n=== データサンプル ===")
        print(main_dataset.head())
        
        # 統計情報
        stats = {
            'total_records': len(df),
            'unique_venues': df['venue_name'].nunique(),
            'unique_dates': df['date'].nunique(),
            'unique_racers': df['racer_id'].nunique(),
            'venue_distribution': df['venue_name'].value_counts().to_dict(),
            'sample_data': main_dataset.head(5).to_dict('records')
        }
        
        stats_file = output_path / "dataset_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"統計情報保存: {stats_file}")

