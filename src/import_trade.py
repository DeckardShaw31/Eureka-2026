import os
import re
import pandas as pd
import numpy as np
from clean_common import CORE_ASEAN_COASTAL, standardize_iso3, ensure_directories

RAW_ASEAN_DIR = os.path.join('data', 'raw', 'aseanstats')
RAW_COMTRADE_DIR = os.path.join('data', 'raw', 'comtrade')
INTERIM_DIR = os.path.join('data', 'interim')

def extract_hs2_chapter(commodity_str):
    """Trích xuất mã chương HS 2 chữ số từ chuỗi mô tả (ví dụ: '[05] Animal...')"""
    if not isinstance(commodity_str, str):
        return None
    match = re.search(r'\[(\d{2})\]', commodity_str)
    if match:
        return int(match.group(1))
    return None

def process_aseanstats_exports(start_year=2010, end_year=2025):
    """
    Xử lý xuất khẩu từ ASEANstats HS2:
    - Tổng xuất khẩu (TOTAL): tổng giá trị các chương HS 01-97
    - Nông sản thực phẩm (agri_food): HS 01-24
    - Hàng chế tạo chế biến (manufacturing): HS 25-97
    - Lưu ý: Dữ liệu tiền tệ gốc là USD
    """
    hs2_file = os.path.join(RAW_ASEAN_DIR, 'asean_imts_annual_hs2.csv')
    if not os.path.exists(hs2_file):
        raise FileNotFoundError(f"Không tìm thấy tệp {hs2_file}")
        
    print(f"[ASEANstats] Đọc xuất khẩu từ {hs2_file}...")
    df = pd.read_csv(hs2_file)
    
    # Lọc luồng Xuất khẩu (Export)
    df_exp = df[df['Flow'].str.strip().str.lower() == 'export'].copy()
    df_exp['iso3'] = df_exp['Reporter'].apply(standardize_iso3)
    df_exp = df_exp[df_exp['iso3'].isin(CORE_ASEAN_COASTAL)].copy()
    
    df_exp['year'] = pd.to_numeric(df_exp['Year'], errors='coerce')
    df_exp = df_exp[(df_exp['year'] >= start_year) & (df_exp['year'] <= end_year)].copy()
    df_exp['trade_usd'] = pd.to_numeric(df_exp['Trade Value (US$)'], errors='coerce').fillna(0.0)
    
    # Trích xuất chương HS2
    df_exp['hs2'] = df_exp['Commodity'].apply(extract_hs2_chapter)
    
    # Tổng hợp theo phân nhóm sản phẩm
    records = []
    for (iso, yr), group in df_exp.groupby(['iso3', 'year']):
        val_total = group['trade_usd'].sum()
        val_agri = group[group['hs2'].between(1, 24)]['trade_usd'].sum()
        val_mfg = group[group['hs2'].between(25, 97)]['trade_usd'].sum()
        
        records.append({
            'iso3': iso,
            'year': int(yr),
            'export_usd': float(val_total),
            'export_usd_agri': float(val_agri),
            'export_usd_mfg': float(val_mfg),
            'trade_source': 'ASEANstats'
        })
        
    df_res = pd.DataFrame(records).sort_values(['iso3', 'year']).reset_index(drop=True)
    out_file = os.path.join(INTERIM_DIR, 'aseanstats_exports_annual.csv')
    df_res.to_csv(out_file, index=False)
    print(f"[ASEANstats] Đã lưu {len(df_res)} bản ghi xuất khẩu quốc gia vào {out_file}")
    return df_res

def process_comtrade_bilateral(start_year=2010, end_year=2024):
    """
    Xử lý xuất khẩu song phương từ UN Comtrade:
    - 9 nước xuất khẩu ASEAN x 24 đối tác lớn
    - Lưu trữ giá trị xuất khẩu song phương theo từng cặp và năm
    """
    comtrade_file = os.path.join(RAW_COMTRADE_DIR, 'comtrade_bilateral_2010_2024.csv')
    if not os.path.exists(comtrade_file):
        raise FileNotFoundError(f"Không tìm thấy tệp {comtrade_file}")
        
    print(f"[UN Comtrade] Đọc thương mại song phương từ {comtrade_file}...")
    df = pd.read_csv(comtrade_file)
    
    # Đảm bảo các kiểu dữ liệu và lọc thời gian
    df['year'] = df['year'].astype(int)
    df = df[(df['year'] >= start_year) & (df['year'] <= end_year)].copy()
    df['trade_usd'] = pd.to_numeric(df['trade_usd'], errors='coerce').fillna(0.0)
    
    # Gom nhóm chống trùng lặp
    agg_df = df.groupby(['exporter_iso3', 'importer_iso3', 'year'])['trade_usd'].max().reset_index()
    agg_df['source_flag'] = 'UNComtrade'
    
    out_file = os.path.join(INTERIM_DIR, 'comtrade_bilateral_annual.csv')
    agg_df.to_csv(out_file, index=False)
    print(f"[UN Comtrade] Đã lưu {len(agg_df)} bản ghi thương mại song phương vào {out_file}")
    return agg_df

if __name__ == '__main__':
    ensure_directories()
    df_as = process_aseanstats_exports()
    df_ct = process_comtrade_bilateral()
    print("[DONE] Hoàn thành tiền xử lý dữ liệu thương mại.")
