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
    
    print("=== [BƯỚC 2] Ghép dòng xuất khẩu song phương từ UN Comtrade & Kiểm toán trạng thái ===")
    ct_file = os.path.join(INTERIM_DIR, 'comtrade_bilateral_annual.csv')
    df_ct = pd.read_csv(ct_file)
    
    rep_file = os.path.join(INTERIM_DIR, 'comtrade_reporter_coverage.csv')
    df_rep = pd.read_csv(rep_file) if os.path.exists(rep_file) else pd.DataFrame()
    
    panel = panel.merge(
        df_ct[['exporter_iso3', 'importer_iso3', 'year', 'trade_usd', 'source_flag']].rename(columns={'trade_usd': 'trade_usd_raw'}),
        on=['exporter_iso3', 'importer_iso3', 'year'],
        how='left'
    )
    
    if not df_rep.empty:
        panel = panel.merge(
            df_rep[['exporter_iso3', 'year', 'reporter_year_complete']],
            on=['exporter_iso3', 'year'],
            how='left'
        )
    else:
        panel['reporter_year_complete'] = 1
        
    # Phân loại chính xác 3 trạng thái dữ liệu:
    # 1. Có số liệu thương mại dương (trade_observed = 1)
    # 2. Số liệu bằng 0 thực tế đã xác nhận (zero_trade_confirmed = 1) khi quốc gia có báo cáo đầy đủ
    # 3. Bản ghi chưa báo cáo / khuyết (unreported_reporter_year) -> GIỮ NGUYÊN NaN, KHÔNG ĐIỀN 0
    panel['trade_observed'] = np.where(panel['trade_usd_raw'] > 0, 1, 0)
    panel['zero_trade_confirmed'] = np.where((panel['reporter_year_complete'] == 1) & (panel['trade_usd_raw'].isnull()), 1, 0)
    
    # Thiết lập biến trade_usd dùng cho PPML:
    # Chỉ điền 0.0 nếu quốc gia CÓ BÁO CÁO (reporter_year_complete == 1)
    panel['trade_usd'] = np.where(
        panel['trade_observed'] == 1,
        panel['trade_usd_raw'],
        np.where(panel['zero_trade_confirmed'] == 1, 0.0, np.nan)
    )
    
    panel['missing_reason'] = None
    panel.loc[panel['reporter_year_complete'] == 0, 'missing_reason'] = 'unreported_reporter_year_in_comtrade'
    
    panel['source_flag'] = 'UNComtrade'
    panel.loc[panel['zero_trade_confirmed'] == 1, 'source_flag'] = 'UNComtrade (Confirmed Zero)'
    panel.loc[panel['reporter_year_complete'] == 0, 'source_flag'] = 'UNComtrade (Unreported)'

    
    n_pos = (panel['trade_observed'] == 1).sum()
    n_zero = (panel['zero_trade_confirmed'] == 1).sum()
    n_miss = panel['trade_usd'].isnull().sum()
    print(f"Kiểm toán thương mại: {n_pos} cặp dương, {n_zero} cặp bằng 0 xác nhận, {n_miss} cặp chưa báo cáo (được bảo toàn NaN để không làm sai lệch PPML).")

    
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
    
    # Sắp xếp các cột theo đúng chuẩn Mục 6.2 và các trường kiểm toán trạng thái dữ liệu
    ordered_cols = [
        'exporter_iso3', 'importer_iso3', 'year', 'trade_usd', 'trade_usd_raw',
        'trade_observed', 'zero_trade_confirmed', 'reporter_year_complete', 'missing_reason',
        'lsbci', 'product_group', 'pair_id', 'exporter_year', 'importer_year',
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
