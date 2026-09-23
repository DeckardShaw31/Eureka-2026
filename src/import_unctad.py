import os
import pandas as pd
import numpy as np
from clean_common import CORE_ASEAN_COASTAL, standardize_iso3, ensure_directories

RAW_UNCTAD_DIR = os.path.join('data', 'raw', 'unctad')
INTERIM_DIR = os.path.join('data', 'interim')

def process_lsci(start_year=2010, end_year=2025, min_quarters=3):
    """
    Xử lý tệp chỉ số kết nối vận tải biển LSCI từ UNCTADstat:
    - Quy đổi dữ liệu quý sang dữ liệu năm bằng trung bình số học
    - Lọc tối thiểu min_quarters quý có sẵn trong năm
    - Tạo cờ lsci_partial_year nếu năm có ít hơn 4 quý
    """
    raw_file = os.path.join(RAW_UNCTAD_DIR, 'US_LSCI.csv')
    if not os.path.exists(raw_file):
        raise FileNotFoundError(f"Không tìm thấy tệp {raw_file}")
    
    print(f"[UNCTAD LSCI] Đọc dữ liệu từ {raw_file}...")
    df = pd.read_csv(raw_file, usecols=[
        'Quarter', 'Economy', 'Economy Label', 'Index (Average Q1 2023 = 100)'
    ])
    
    # Chuẩn hóa mã quốc gia
    df['iso3'] = df['Economy Label'].apply(standardize_iso3)
    df_core = df[df['iso3'].isin(CORE_ASEAN_COASTAL)].copy()
    
    # Tách năm và quý
    df_core['year'] = df_core['Quarter'].str[:4].astype(int)
    df_core['quarter_num'] = df_core['Quarter'].str[-2:].astype(int)
    df_core['lsci_val'] = pd.to_numeric(df_core['Index (Average Q1 2023 = 100)'], errors='coerce')
    
    # Lọc giai đoạn nghiên cứu
    df_period = df_core[(df_core['year'] >= start_year) & (df_core['year'] <= end_year)]
    
    # Tổng hợp theo nước và năm
    agg_df = df_period.groupby(['iso3', 'year'])['lsci_val'].agg(
        lsci='mean',
        lsci_quarters='count'
    ).reset_index()
    
    # Kiểm tra điều kiện tối thiểu 3 quý
    agg_df['lsci_valid'] = agg_df['lsci_quarters'] >= min_quarters
    agg_df['lsci_partial_year'] = (agg_df['lsci_quarters'] < 4).astype(int)
    
    # Bỏ các năm không đạt số quý tối thiểu (nếu có)
    agg_df = agg_df[agg_df['lsci_valid']].drop(columns=['lsci_valid'])
    
    out_file = os.path.join(INTERIM_DIR, 'unctad_lsci_annual.csv')
    agg_df.to_csv(out_file, index=False)
    print(f"[UNCTAD LSCI] Đã lưu {len(agg_df)} quan sát LSCI năm vào {out_file}")
    return agg_df

def process_lsbci(start_year=2010, end_year=2025):
    """
    Xử lý tệp chỉ số kết nối song phương LSBCI từ UNCTADstat:
    - Lọc 9 nước xuất khẩu ASEAN ven biển và 24 đối tác lớn
    - Lưu ý phương pháp luận: LSBCI được UNCTAD công bố định kỳ Q1 hàng năm
    - Giữ giá trị Q1 của mỗi năm và tính log tự nhiên
    """
    raw_file = os.path.join(RAW_UNCTAD_DIR, 'US_LSBCI.csv')
    if not os.path.exists(raw_file):
        raise FileNotFoundError(f"Không tìm thấy tệp {raw_file}")
        
    print(f"[UNCTAD LSBCI] Đọc dữ liệu từ {raw_file}...")
    df = pd.read_csv(raw_file, usecols=[
        'Quarter', 'Economy Label', 'Partner Label', 'Index'
    ])
    
    # Chuẩn hóa mã ISO3 cho cả nước xuất khẩu và nước nhập khẩu
    df['exporter_iso3'] = df['Economy Label'].apply(standardize_iso3)
    df['importer_iso3'] = df['Partner Label'].apply(standardize_iso3)
    df['year'] = df['Quarter'].str[:4].astype(int)
    df['lsbci'] = pd.to_numeric(df['Index'], errors='coerce')
    
    # Lọc các cặp hợp lệ trong mẫu nghiên cứu
    df_core = df[
        (df['exporter_iso3'].isin(CORE_ASEAN_COASTAL)) &
        (df['importer_iso3'].notnull()) &
        (df['exporter_iso3'] != df['importer_iso3']) &
        (df['year'] >= start_year) &
        (df['year'] <= end_year)
    ].copy()
    
    # Tổng hợp theo cặp nước - năm
    agg_lsbci = df_core.groupby(['exporter_iso3', 'importer_iso3', 'year'])['lsbci'].mean().reset_index()
    agg_lsbci['ln_lsbci'] = np.where(agg_lsbci['lsbci'] > 0, np.log(agg_lsbci['lsbci']), np.nan)
    
    out_file = os.path.join(INTERIM_DIR, 'unctad_lsbci_annual.csv')
    agg_lsbci.to_csv(out_file, index=False)
    print(f"[UNCTAD LSBCI] Đã lưu {len(agg_lsbci)} cặp quan sát LSBCI năm vào {out_file}")
    return agg_lsbci

if __name__ == '__main__':
    ensure_directories()
    df_lsci = process_lsci()
    df_lsbci = process_lsbci()
    print("[DONE] Hoàn thành tiền xử lý dữ liệu UNCTADstat.")
