import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from clean_common import ensure_directories

PROCESSED_DIR = os.path.join('data', 'processed')
TABLES_DIR = os.path.join('outputs', 'tables')
LOGS_DIR = os.path.join('outputs', 'logs')

def estimate_gravity_models():
    """
    Ước lượng các mô hình trọng lực PPML song phương (Tầng B) theo Mục 4.2 của design.md:
    G1: ln_lsbci + Cặp nước FE + Năm FE (Cluster by pair_id)
    G2: ln_lsbci + Nước xuất khẩu FE + Nước nhập khẩu FE + Năm FE
    G3: ln_lsbci + Nước xuất khẩu-Năm FE + Nước nhập khẩu FE
    G4: ln_lsbci + Nước xuất khẩu FE + Nước nhập khẩu-Năm FE
    G5: Mô hình rút gọn: ln_lsbci + ln_exporter_lsci + Cặp nước FE + Năm FE
    """
    ensure_directories()
    bilateral_file = os.path.join(PROCESSED_DIR, 'panel_bilateral_year.csv')
    df = pd.read_csv(bilateral_file)
    
    # Mẫu ước lượng chuẩn 2010-2024
    sample = df[df['year'] <= 2024].dropna(subset=['ln_lsbci']).copy()
    # Chuyển đổi đơn vị thành triệu USD để tránh overflow số thực trong thuật toán IRLS
    # (Đặc tính bất biến của Poisson: hệ số góc ln(LSBCI) không bị thay đổi)
    sample['trade_million'] = sample['trade_usd'] / 1e6
    
    specs = [
        {
            'id': 'G1',
            'name': 'G1: Trọng lực cơ sở\n[Cặp FE + Năm FE]',
            'formula': 'trade_million ~ ln_lsbci + C(pair_id) + C(year)',
            'cluster': 'pair_id',
            'pair_fe': 'Có',
            'year_fe': 'Có',
            'exp_year_fe': 'Không',
            'imp_year_fe': 'Không',
            'exp_fe': 'Hấp thụ',
            'imp_fe': 'Hấp thụ'
        },
        {
            'id': 'G2',
            'name': 'G2: Trọng lực cổ điển\n[Nước FE + Năm FE]',
            'formula': 'trade_million ~ ln_lsbci + C(exporter_iso3) + C(importer_iso3) + C(year)',
            'cluster': 'pair_id',
            'pair_fe': 'Không',
            'year_fe': 'Có',
            'exp_year_fe': 'Không',
            'imp_year_fe': 'Không',
            'exp_fe': 'Có',
            'imp_fe': 'Có'
        },
        {
            'id': 'G3',
            'name': 'G3: Sức cản xuất khẩu\n[Xuất khẩu-Năm FE]',
            'formula': 'trade_million ~ ln_lsbci + C(exporter_year) + C(importer_iso3)',
            'cluster': 'pair_id',
            'pair_fe': 'Không',
            'year_fe': 'Hấp thụ',
            'exp_year_fe': 'Có',
            'imp_year_fe': 'Không',
            'exp_fe': 'Hấp thụ',
            'imp_fe': 'Có'
        },
        {
            'id': 'G4',
            'name': 'G4: Sức cản nhập khẩu\n[Nhập khẩu-Năm FE]',
            'formula': 'trade_million ~ ln_lsbci + C(exporter_iso3) + C(importer_year)',
            'cluster': 'pair_id',
            'pair_fe': 'Không',
            'year_fe': 'Hấp thụ',
            'exp_year_fe': 'Không',
            'imp_year_fe': 'Có',
            'exp_fe': 'Có',
            'imp_fe': 'Hấp thụ'
        },
        {
            'id': 'G5',
            'name': 'G5: Mô hình rút gọn\n[LSBCI + LSCI]',
            'formula': 'trade_million ~ ln_lsbci + ln_exporter_lsci + C(pair_id) + C(year)',
            'cluster': 'pair_id',
            'pair_fe': 'Có',
            'year_fe': 'Có',
            'exp_year_fe': 'Không',
            'imp_year_fe': 'Không',
            'exp_fe': 'Hấp thụ',
            'imp_fe': 'Hấp thụ'
        }
    ]
    
    results = {}
    cols_header = []
    
    print("=== [ESTIMATION] Bắt đầu ước lượng các mô hình Trọng lực PPML (Tầng B) ===")
    
    for s in specs:
        model_name = s['name']
        cols_header.append(model_name)
        print(f"\n--- Đang ước lượng mô hình {s['id']} (N = {len(sample)}) ---")
        
        res = smf.glm(
            s['formula'],
            data=sample,
            family=sm.families.Poisson()
        ).fit(cov_type='cluster', cov_kwds={'groups': sample[s['cluster']]}, maxiter=100)
        
        print(f"  ✓ Hội tụ: {res.converged} | Pseudo LL: {res.llf:.1f}")
        
        # Lấy hệ số ln_lsbci
        c_lsbci = res.params.get('ln_lsbci', np.nan)
        se_lsbci = res.bse.get('ln_lsbci', np.nan)
        p_lsbci = res.pvalues.get('ln_lsbci', np.nan)
        stars_lsbci = '***' if p_lsbci < 0.01 else '**' if p_lsbci < 0.05 else '*' if p_lsbci < 0.1 else ''
        
        # Lấy hệ số ln_exporter_lsci (nếu có trong G5)
        if 'ln_exporter_lsci' in res.params:
            c_lsci = res.params['ln_exporter_lsci']
            se_lsci = res.bse['ln_exporter_lsci']
            p_lsci = res.pvalues['ln_exporter_lsci']
            stars_lsci = '***' if p_lsci < 0.01 else '**' if p_lsci < 0.05 else '*' if p_lsci < 0.1 else ''
            val_lsci_str = f"{c_lsci:.3f}{stars_lsci}"
            se_lsci_str = f"({se_lsci:.3f})"
        else:
            val_lsci_str = ""
            se_lsci_str = ""
            
        results[model_name] = {
            'ln_lsbci': f"{c_lsbci:.3f}{stars_lsbci}",
            'ln_lsbci_se': f"({se_lsbci:.3f})",
            'ln_exporter_lsci': val_lsci_str,
            'ln_exporter_lsci_se': se_lsci_str,
            'pair_fe': s['pair_fe'],
            'year_fe': s['year_fe'],
            'exp_year_fe': s['exp_year_fe'],
            'imp_year_fe': s['imp_year_fe'],
            'n_obs': len(sample),
            'n_pairs': sample['pair_id'].nunique(),
            'zero_obs': (sample['trade_usd'] == 0).sum(),
            'pseudo_ll': f"{res.llf:.1f}"
        }
        
    # Tạo bảng hiển thị
    row_labels = [
        'ln(LSBCI song phương)',
        'ln(LSBCI song phương) (SE)',
        'ln(LSCI nước xuất khẩu)',
        'ln(LSCI nước xuất khẩu) (SE)',
        'Hiệu ứng cố định Cặp quốc gia',
        'Hiệu ứng cố định Năm',
        'Hiệu ứng Xuất khẩu - Năm',
        'Hiệu ứng Nhập khẩu - Năm',
        'Số quan sát (N)',
        'Số cặp quốc gia',
        'Số quan sát thương mại bằng 0',
        'Sai số chuẩn phân cụm'
    ]
    
    table_data = []
    for lbl in row_labels:
        row_vals = []
        for col in cols_header:
            d = results[col]
            if lbl == 'ln(LSBCI song phương)':
                row_vals.append(d['ln_lsbci'])
            elif lbl == 'ln(LSBCI song phương) (SE)':
                row_vals.append(d['ln_lsbci_se'])
            elif lbl == 'ln(LSCI nước xuất khẩu)':
                row_vals.append(d['ln_exporter_lsci'])
            elif lbl == 'ln(LSCI nước xuất khẩu) (SE)':
                row_vals.append(d['ln_exporter_lsci_se'])
            elif lbl == 'Hiệu ứng cố định Cặp quốc gia':
                row_vals.append(d['pair_fe'])
            elif lbl == 'Hiệu ứng cố định Năm':
                row_vals.append(d['year_fe'])
            elif lbl == 'Hiệu ứng Xuất khẩu - Năm':
                row_vals.append(d['exp_year_fe'])
            elif lbl == 'Hiệu ứng Nhập khẩu - Năm':
                row_vals.append(d['imp_year_fe'])
            elif lbl == 'Số quan sát (N)':
                row_vals.append(d['n_obs'])
            elif lbl == 'Số cặp quốc gia':
                row_vals.append(d['n_pairs'])
            elif lbl == 'Số quan sát thương mại bằng 0':
                row_vals.append(d['zero_obs'])
            elif lbl == 'Sai số chuẩn phân cụm':
                row_vals.append('Cluster (Pair ID)')
        table_data.append(row_vals)
        
    df_gravity_table = pd.DataFrame(table_data, index=row_labels, columns=cols_header)
    
    out_csv = os.path.join(TABLES_DIR, 'table_gravity_ppml_models.csv')
    out_tex = os.path.join(TABLES_DIR, 'table_gravity_ppml_models.tex')
    df_gravity_table.to_csv(out_csv)
    df_gravity_table.to_latex(out_tex, caption='Kết quả ước lượng mô hình trọng lực PPML song phương (2010--2024)', label='tab:gravity_ppml')
    print(f"\n[THÀNH CÔNG] Đã lưu bảng kết quả hồi quy Trọng lực PPML Tầng B vào:\n  {out_csv}\n  {out_tex}")
    
    return df_gravity_table

if __name__ == '__main__':
    estimate_gravity_models()
