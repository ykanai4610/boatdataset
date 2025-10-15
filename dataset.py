from src import wkwk, QuickKekkaf2024Processor
import yaml
import os
config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

def main():
    """メイン実行"""
    print("=== 2024年競艇データ特化処理（クイック版） ===")
    print("要求データ: レース場、着順、艇番、レーサーNo、展示タイム、スタートタイミング、タイム")
    
   # kekkaf_dir = config['file_path']['kekkaf_dir']
    kekkaf_dir = r"G:\マイドライブ\BR_python\kekkaf"
    processor = QuickKekkaf2024Processor()
    
    # サンプルファイルを処理
    if processor.process_sample_files(kekkaf_dir, max_files=12):
        processor.save_sample_dataset()
    else:
        print("ファイル処理に失敗しました")

if __name__ == "__main__":
    main()

