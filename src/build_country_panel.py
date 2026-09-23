import os
import pandas as pd
import numpy as np
from clean_common import CORE_ASEAN_COASTAL, load_countries_config, ensure_directories

INTERIM_DIR = os.path.join('data', 'interim')
PROCESSED_DIR = os.path.join('data', 'processed')
RAW_WB_FILE = os.path.join('data', 'raw', 'world_bank', 'world_bank_indicators_2010_2025.csv')
DIAGNOSTICS_DIR = os.path.join('outputs', 'diagnostics')

def build_country_panel(start_year=2010, end_year=2025):
    """
    Xây dựng bảng dữ liệu quốc gia - năm (panel_country_year.csv)
    tuân thủ đúng Từ điển dữ liệu Mục 6.1 của design.md
    """
    print("=== [BƯỚC 1] Khởi tạo lưới dữ liệu 9 nước x 16 năm ===")
    df_countries = load_countries_config()
    core_countries = df_countries[df_countries['iso3'].isin(CORE_ASEAN_COASTAL)].copy()
    
    # Tạo lưới cân bằng
    grid_rows = []
    for _, c_row in core_countries.iterrows():
        iso = c_row['iso3']
        country_name = c_row['country']
        grp = c_row['group']
        for yr in range(start_year, end_year + 1):
            grid_rows.append({
                'iso3': iso,
                'country': country_name,
                'year': yr,
                'clmv': 1 if grp == 'clmv' else 0,
                'asean6': 1 if grp == 'asean6' else 0,
                'covid': 1 if yr in [2020, 2021] else 0
            })
    panel = pd.DataFrame(grid_rows)
    print(f"Khung lưới ban đầu: {len(panel)} quan sát.")
    
    print("=== [BƯỚC 2] Ghép dữ liệu xuất khẩu từ ASEANstats ===")
    as_file = os.path.join(INTERIM_DIR, 'aseanstats_exports_annual.csv')
    df_as = pd.read_csv(as_file)
    panel = panel.merge(
        df_as[['iso3', 'year', 'export_usd', 'export_usd_agri', 'export_usd_mfg']],
        on=['iso3', 'year'],
        how='left'
    )
    
    print("=== [BƯỚC 3] Ghép chỉ số LSCI từ UNCTADstat ===")
    lsci_file = os.path.join(INTERIM_DIR, 'unctad_lsci_annual.csv')
    df_lsci = pd.read_csv(lsci_file)
    panel = panel.merge(
        df_lsci[['iso3', 'year', 'lsci', 'lsci_quarters', 'lsci_partial_year']],
        on=['iso3', 'year'],
        how='left'
    )
    
    print("=== [BƯỚC 4] Ghép các biến kiểm soát World Bank ===")
    df_wb = pd.read_csv(RAW_WB_FILE)
    wb_cols = ['iso3', 'year', 'gdp_usd', 'population', 'fdi_gdp', 'reer', 'official_fx']
    panel = panel.merge(
        df_wb[wb_cols],
        on=['iso3', 'year'],
        how='left'
    )
    
    print("=== [BƯỚC 5] Tính toán biến Log và Biến trễ ===")
    panel = panel.sort_values(['iso3', 'year']).reset_index(drop=True)
    
    # Tính log cho các biến dương
    panel['ln_export'] = np.where(panel['export_usd'] > 0, np.log(panel['export_usd']), np.nan)
    panel['ln_export_agri'] = np.where(panel['export_usd_agri'] > 0, np.log(panel['export_usd_agri']), np.nan)
    panel['ln_export_mfg'] = np.where(panel['export_usd_mfg'] > 0, np.log(panel['export_usd_mfg']), np.nan)
    panel['ln_lsci'] = np.where(panel['lsci'] > 0, np.log(panel['lsci']), np.nan)
    panel['ln_gdp'] = np.where(panel['gdp_usd'] > 0, np.log(panel['gdp_usd']), np.nan)
    panel['ln_population'] = np.where(panel['population'] > 0, np.log(panel['population']), np.nan)
    
    # Biến trễ 1 năm theo từng quốc gia
    panel['ln_lsci_lag1'] = panel.groupby('iso3')['ln_lsci'].shift(1)
    panel['lsci_lag1'] = panel.groupby('iso3')['lsci'].shift(1)
    
    # Biến tốc độ thay đổi tỷ giá chính thức (% change)
    panel['fx_growth'] = panel.groupby('iso3')['official_fx'].pct_change(fill_method=None)

    
    # Xác định cờ data_complete (đầy đủ các biến bắt buộc cho mô hình cơ sở M1 & M2)
    core_complete = (
        panel['export_usd'].notnull() &
        panel['lsci'].notnull() &
        panel['gdp_usd'].notnull() &
        panel['population'].notnull()
    )
    panel['data_complete'] = core_complete.astype(int)
    
    # Sắp xếp đúng thứ tự cột quy định tại Mục 6.1
    ordered_cols = [
        'iso3', 'country', 'year', 'export_usd', 'lsci', 'gdp_usd', 'population',
        'fdi_gdp', 'reer', 'official_fx', 'clmv', 'asean6', 'covid',
        'ln_export', 'ln_lsci', 'ln_gdp', 'ln_population', 'ln_lsci_lag1',
        'data_complete', 'export_usd_agri', 'export_usd_mfg', 'ln_export_agri',
        'ln_export_mfg', 'lsci_lag1', 'fx_growth', 'lsci_quarters', 'lsci_partial_year'
    ]
    panel = panel[ordered_cols]
    
    out_file = os.path.join(PROCESSED_DIR, 'panel_country_year.csv')
    panel.to_csv(out_file, index=False)
    print(f"\n[THÀNH CÔNG] Đã tạo bảng dữ liệu quốc gia: {out_file} ({len(panel)} dòng, {len(panel.columns)} cột)")
    
    # Báo cáo kiểm toán ghép dữ liệu
    audit_file = os.path.join(DIAGNOSTICS_DIR, 'merge_audit_country.csv')
    audit_df = pd.DataFrame({
        'variable': panel.columns,
        'non_null_count': panel.notnull().sum().values,
        'missing_count': panel.isnull().sum().values,
        'completeness_pct': (panel.notnull().sum().values / len(panel) * 100).round(2)
    })
    audit_df.to_csv(audit_file, index=False)
    print(f"[AUDIT] Đã lưu báo cáo kiểm toán ghép dữ liệu vào {audit_file}")
    
    return panel

if __name__ == '__main__':
    ensure_directories()
    df_panel = build_country_panel()
