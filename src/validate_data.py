import os
import pandas as pd
import numpy as np
from clean_common import ensure_directories

PROCESSED_DIR = os.path.join('data', 'processed')
DIAGNOSTICS_DIR = os.path.join('outputs', 'diagnostics')

def validate_datasets():
    """
    Thực hiện kiểm tra các assertion hợp đồng dữ liệu theo Mục 7 & 10 của design.md:
    - Tính duy nhất của các khóa chính (primary keys)
    - Miền giá trị hợp lệ (non-negative trade, positive indices)
    - So sánh tổng kim ngạch xuất khẩu giữa 2 nguồn ASEANstats và UN Comtrade
    - Xuất các báo cáo chẩn đoán vào outputs/diagnostics/
    """
    ensure_directories()
    country_file = os.path.join(PROCESSED_DIR, 'panel_country_year.csv')
    bilateral_file = os.path.join(PROCESSED_DIR, 'panel_bilateral_year.csv')
    
    if not os.path.exists(country_file) or not os.path.exists(bilateral_file):
        raise FileNotFoundError("Không tìm thấy tệp processed. Hãy chạy build_country_panel.py và build_bilateral_panel.py trước.")
        
    print("=== [VALIDATION 1] Kiểm tra bảng quốc gia - năm (panel_country_year.csv) ===")
    df_country = pd.read_csv(country_file)
    
    # 1. Khóa chính không trùng lặp
    dup_country = df_country[df_country.duplicated(subset=['iso3', 'year'], keep=False)]
    assert len(dup_country) == 0, f"Phát hiện {len(dup_country)} dòng trùng khóa (iso3, year)!"
    print("  ✓ Khóa (iso3, year) duy nhất tuyệt đối 100%.")
    
    # 2. Miền giá trị hợp lệ
    assert (df_country['export_usd'] >= 0).all(), "Giá trị export_usd có số âm!"
    assert (df_country['lsci'] > 0).all(), "Chỉ số LSCI có giá trị <= 0 hoặc khuyết!"
    assert (df_country['gdp_usd'] > 0).all(), "GDP có giá trị <= 0 hoặc khuyết!"
    assert (df_country['population'] > 0).all(), "Dân số có giá trị <= 0 hoặc khuyết!"
    assert df_country['year'].between(2010, 2025).all(), "Năm nằm ngoài phạm vi 2010-2025!"
    print("  ✓ Các biến cốt lõi (export_usd, lsci, gdp, population) đều không âm và nằm trong miền giá trị chuẩn.")
    
    print("\n=== [VALIDATION 2] Kiểm tra bảng song phương (panel_bilateral_year.csv) ===")
    df_bilateral = pd.read_csv(bilateral_file)
    
    # 1. Khóa chính không trùng lặp
    dup_bilateral = df_bilateral[df_bilateral.duplicated(subset=['exporter_iso3', 'importer_iso3', 'year', 'product_group'], keep=False)]
    assert len(dup_bilateral) == 0, f"Phát hiện {len(dup_bilateral)} dòng trùng khóa song phương!"
    print("  ✓ Khóa (exporter_iso3, importer_iso3, year, product_group) duy nhất tuyệt đối 100%.")
    
    # 2. Miền giá trị
    assert (df_bilateral['trade_usd'] >= 0).all(), "Giá trị trade_usd có số âm!"
    valid_lsbci = df_bilateral['lsbci'].dropna()
    assert (valid_lsbci >= 0).all(), "LSBCI có giá trị âm!"
    assert df_bilateral['year'].between(2010, 2024).all(), "Năm song phương ngoài khoảng 2010-2024!"
    print("  ✓ Miền giá trị song phương hợp lệ (trade_usd >= 0, lsbci >= 0).")
    
    print("\n=== [VALIDATION 3] Xuất các báo cáo chẩn đoán dữ liệu ===")
    # A. Báo cáo tỷ lệ khuyết (Missingness report)
    missing_records = []
    for col in df_country.columns:
        n_miss = df_country[col].isnull().sum()
        missing_records.append({
            'dataset': 'panel_country_year',
            'variable': col,
            'total_obs': len(df_country),
            'missing_obs': n_miss,
            'missing_rate_pct': round(n_miss / len(df_country) * 100, 2)
        })
    for col in df_bilateral.columns:
        n_miss = df_bilateral[col].isnull().sum()
        missing_records.append({
            'dataset': 'panel_bilateral_year',
            'variable': col,
            'total_obs': len(df_bilateral),
            'missing_obs': n_miss,
            'missing_rate_pct': round(n_miss / len(df_bilateral) * 100, 2)
        })
    df_missing = pd.DataFrame(missing_records)
    missing_file = os.path.join(DIAGNOSTICS_DIR, 'missingness.csv')
    df_missing.to_csv(missing_file, index=False)
    print(f"  ✓ Đã lưu báo cáo tỷ lệ khuyết: {missing_file}")
    
    # B. Báo cáo kiểm tra trùng khóa (Duplicate keys report)
    dup_file = os.path.join(DIAGNOSTICS_DIR, 'duplicate_keys.csv')
    df_dup = pd.DataFrame([
        {'dataset': 'panel_country_year', 'keys': 'iso3, year', 'duplicates': len(dup_country)},
        {'dataset': 'panel_bilateral_year', 'keys': 'exporter, importer, year, product', 'duplicates': len(dup_bilateral)}
    ])
    df_dup.to_csv(dup_file, index=False)
    print(f"  ✓ Đã lưu báo cáo trùng lặp khóa: {dup_file}")
    
    # C. So sánh tổng kim ngạch xuất khẩu giữa ASEANstats và UN Comtrade
    # (So sánh tổng xuất khẩu sang 24 đối tác của Comtrade với tổng xuất khẩu Thế giới của ASEANstats)
    comp_records = []
    agg_comtrade = df_bilateral.groupby(['exporter_iso3', 'year'])['trade_usd'].sum().reset_index()
    for _, row in agg_comtrade.iterrows():
        exp = row['exporter_iso3']
        yr = int(row['year'])
        val_ct = float(row['trade_usd'])
        
        as_match = df_country[(df_country['iso3'] == exp) & (df_country['year'] == yr)]
        if not as_match.empty:
            val_as = float(as_match['export_usd'].values[0])
            ratio = round(val_ct / val_as * 100, 2) if val_as > 0 else 0
            comp_records.append({
                'exporter_iso3': exp,
                'year': yr,
                'comtrade_24_partners_usd': val_ct,
                'aseanstats_world_usd': val_as,
                'coverage_ratio_pct': ratio,
                'notes': 'OK - 24 đối tác lớn chiếm đa số thị phần' if ratio >= 60 else 'Thị phần đối tác nhỏ hoặc thiếu báo cáo'
            })
    df_comp = pd.DataFrame(comp_records)
    comp_file = os.path.join(DIAGNOSTICS_DIR, 'source_comparison.csv')
    df_comp.to_csv(comp_file, index=False)
    print(f"  ✓ Đã lưu báo cáo đối chiếu nguồn thương mại: {comp_file}")
    
    # D. Báo cáo độ phủ dữ liệu năm 2025
    y25 = df_country[df_country['year'] == 2025]
    y25_summary = pd.DataFrame({
        'variable': ['export_usd', 'lsci', 'gdp_usd', 'population', 'fdi_gdp', 'reer', 'official_fx'],
        'non_null_count': [y25[c].notnull().sum() for c in ['export_usd', 'lsci', 'gdp_usd', 'population', 'fdi_gdp', 'reer', 'official_fx']],
        'total_countries': len(y25),
        'coverage_pct': [(y25[c].notnull().sum() / len(y25) * 100).round(1) for c in ['export_usd', 'lsci', 'gdp_usd', 'population', 'fdi_gdp', 'reer', 'official_fx']],
        'status_rule_80pct': ['ĐẠT' if (y25[c].notnull().sum() / len(y25)) >= 0.8 else 'KHÔNG ĐẠT' for c in ['export_usd', 'lsci', 'gdp_usd', 'population', 'fdi_gdp', 'reer', 'official_fx']]
    })
    cov_file = os.path.join(DIAGNOSTICS_DIR, '2025_coverage.csv')
    y25_summary.to_csv(cov_file, index=False)
    print(f"  ✓ Đã lưu báo cáo đánh giá năm 2025: {cov_file}")
    
    print("\n[THÀNH CÔNG] Tất cả các kiểm tra hợp đồng dữ liệu đã vượt qua (PASS).")

if __name__ == '__main__':
    validate_datasets()
