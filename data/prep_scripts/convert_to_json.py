import pandas as pd
import os

csv_file = r"C:\Data Collection\dataset_labels.csv"
json_file = r"C:\Data Collection\dataset_labels.json"
def main():
    if not os.path.exists(csv_file):
        print(f"[ERROR] ไม่พบไฟล์ {csv_file}")
        return

    try:
       
        df = pd.read_csv(csv_file)

        df.to_json(json_file, orient='records', indent=4)

        print(f"SUCCESS {json_file} ")
        print(f"รวมข้อมูลทั้งหมด {len(df)} รายการ")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()