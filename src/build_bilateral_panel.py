import os
import pandas as pd
import numpy as np
from clean_common import CORE_ASEAN_COASTAL, load_partners_config, ensure_directories

INTERIM_DIR = os.path.join('data', 'interim')
PROCESSED_DIR = os.path.join('data', 'processed')
DIAGNOSTICS_DIR = os.path.join('outputs', 'diagnostics')

def build_bilateral_panel(start_year=2010, end_year=2024):
    """
    Xây dựng bảng dữ liệu song phương (panel_bilateral_year.csv)
    tuân thủ đúng Từ điển dữ liệu Mục 6.2 của design.md
    """
    print("=== [BƯỚC 1] Khởi tạo khung lưới vuông 9 nước xuất khẩu x 24 đối tác x 15 năm ===")
    df_partners = load_partners_config()
    partner_iso_list = df_partners['iso3'].unique().tolist()
    
    grid_rows = []
    for exp_iso in CORE_ASEAN_COASTAL:
        for imp_iso in partner_iso_list:
            if exp_iso == imp_iso:
                continue
            for yr in range(start_year, end_year + 1):
                grid_rows.append({
                    'exporter_iso3': exp_iso,
                    'importer_iso3': imp_iso,
                    'year': yr,
                    'product_group': 'total',
                    'pair_id': f"{exp_iso}-{imp_iso}",
                    'exporter_year': f"{exp_iso}_{yr}",
                    'importer_year': f"{imp_iso}_{yr}"
                })
                
    panel = pd.DataFrame(grid_rows)
    print(f"Tổng số quan sát cặp nước - năm trong lưới vuông lý thuyết: {len(panel)} dòng.")
    
    print("=== [BƯỚC 2] Ghép dòng xuất khẩu song phương từ UN Comtrade ===")
    ct_file = os.path.join(INTERIM_DIR, 'comtrade_bilateral_annual.csv')
    df_ct = pd.read_csv(ct_file)
    
    panel = panel.merge(
        df_ct[['exporter_iso3', 'importer_iso3', 'year', 'trade_usd', 'source_flag']],
        on=['exporter_iso3', 'importer_iso3', 'year'],
        how='left'
    )
    
    # Quy tắc bắt buộc của PPML: Giữ nguyên quan sát thương mại bằng 0 (không xóa, không chuyển thành NaN)
    zero_trade_count = panel['trade_usd'].isnull().sum()
    panel['trade_usd'] = panel['trade_usd'].fillna(0.0)
    panel['source_flag'] = panel['source_flag'].fillna('UNComtrade (Zero Trade)')
    print(f"Số cặp có giao dịch dương: {len(panel) - zero_trade_count}, số cặp không có thương mại (Trade = 0): {zero_trade_count}")
    
    print("=== [BƯỚC 3] Ghép chỉ số kết nối vận tải biển song phương LSBCI ===")
    lsbci_file = os.path.join(INTERIM_DIR, 'unctad_lsbci_annual.csv')
    df_lsbci = pd.read_csv(lsbci_file)
    
    panel = panel.merge(
        df_lsbci[['exporter_iso3', 'importer_iso3', 'year', 'lsbci', 'ln_lsbci']],
        on=['exporter_iso3', 'importer_iso3', 'year'],
        how='left'
    )
    
    print("=== [BƯỚC 4] Ghép LSCI nước xuất khẩu để phục vụ kiểm định mở rộng ===")
    lsci_file = os.path.join(INTERIM_DIR, 'unctad_lsci_annual.csv')
    df_lsci = pd.read_csv(lsci_file)
    panel = panel.merge(
        df_lsci[['iso3', 'year', 'lsci']].rename(columns={'iso3': 'exporter_iso3', 'lsci': 'exporter_lsci'}),
        on=['exporter_iso3', 'year'],
        how='left'
    )
    panel['ln_exporter_lsci'] = np.where(panel['exporter_lsci'] > 0, np.log(panel['exporter_lsci']), np.nan)
    
    # Sắp xếp các cột theo đúng chuẩn Mục 6.2
    ordered_cols = [
        'exporter_iso3', 'importer_iso3', 'year', 'trade_usd', 'lsbci',
        'product_group', 'pair_id', 'exporter_year', 'importer_year',
        'ln_lsbci', 'source_flag', 'exporter_lsci', 'ln_exporter_lsci'
    ]
    panel = panel[ordered_cols].sort_values(['exporter_iso3', 'importer_iso3', 'year']).reset_index(drop=True)
    
    out_file = os.path.join(PROCESSED_DIR, 'panel_bilateral_year.csv')
    panel.to_csv(out_file, index=False)
    print(f"\n[THÀNH CÔNG] Đã tạo bảng dữ liệu song phương: {out_file} ({len(panel)} dòng, {len(panel.columns)} cột)")
    
    # Báo cáo kiểm toán ghép dữ liệu song phương
    audit_file = os.path.join(DIAGNOSTICS_DIR, 'merge_audit_bilateral.csv')
    audit_df = pd.DataFrame({
        'variable': panel.columns,
        'non_null_count': panel.notnull().sum().values,
        'missing_count': panel.isnull().sum().values,
        'zero_count': (panel == 0).sum().values,
        'completeness_pct': (panel.notnull().sum().values / len(panel) * 100).round(2)
    })
    audit_df.to_csv(audit_file, index=False)
    print(f"[AUDIT] Đã lưu báo cáo kiểm toán song phương vào {audit_file}")
    
    return panel

if __name__ == '__main__':
    ensure_directories()
    df_bilateral = build_bilateral_panel()
