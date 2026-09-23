import os
import json
import pandas as pd
import numpy as np
import scipy.linalg
import patsy
import statsmodels.api as sm
import statsmodels.formula.api as smf
from clean_common import ensure_directories, format_coef_se, format_pval

PROCESSED_DIR = os.path.join('data', 'processed')
TABLES_DIR = os.path.join('outputs', 'tables')
LOGS_DIR = os.path.join('outputs', 'logs')

def fit_structural_gravity(sample):
    """
    Ước lượng mô hình Trọng lực cấu trúc đầy đủ (Full Structural Gravity):
    X_ijt = exp(beta * ln_lsbci_ijt + mu_ij + pi_it + chi_jt) * eps_ijt
    với Cặp FE (mu_ij), Nước xuất khẩu-Năm FE (pi_it), Nước nhập khẩu-Năm FE (chi_jt).
    
    Xử lý đa cộng tuyến hoàn hảo giữa các biến giả thông qua phân rã QR với pivoting
    (QR decomposition with column pivoting), đảm bảo ma trận thiết kế đạt hạng đầy đủ.
    """
    print("  [QR-Pivoting] Khởi tạo ma trận thiết kế cho mô hình cấu trúc đầy đủ...")
    formula = 'trade_million ~ ln_lsbci + C(pair_id) + C(exporter_year) + C(importer_year)'
    y, X = patsy.dmatrices(formula, data=sample, return_type='dataframe')
    
    # Phân rã QR để phát hiện và loại bỏ các cột đa cộng tuyến
    Q, R, P = scipy.linalg.qr(X.values, mode='economic', pivoting=True)
    diag_R = np.abs(np.diag(R))
    tol = diag_R[0] * np.finfo(float).eps * max(X.shape)
    rank = int(np.sum(diag_R > tol))
    
    keep_idx = np.sort(P[:rank])
    X_sub = X.iloc[:, keep_idx]
    
    # Đảm bảo biến giải thích chính không bị loại trừ
    if 'ln_lsbci' not in X_sub.columns:
        raise ValueError("Lỗi: Biến ln_lsbci bị loại trong quá trình khử cộng tuyến QR!")
        
    print(f"  [QR-Pivoting] Số biến ban đầu: {X.shape[1]} -> Hạng ma trận (Rank): {rank} (Đã khử {X.shape[1] - rank} biến giả cộng tuyến)")
    
    # Ước lượng GLM Poisson với Clustered SE theo pair_id và hiệu chỉnh mẫu nhỏ t
    res = sm.GLM(y, X_sub, family=sm.families.Poisson()).fit(
        cov_type='cluster', use_t=True, cov_kwds={'groups': sample['pair_id']}, maxiter=100
    )
    return res

def estimate_gravity_models():
    """
    Ước lượng các mô hình trọng lực PPML song phương (Tầng B) theo Mục 4.2 của design.md:
    G1: Trọng lực cấu trúc đầy đủ (Pair FE + Exp-Year FE + Imp-Year FE)
    G2: Trọng lực chuẩn với Cặp FE (Pair FE + Year FE)
    G3: Sức cản Xuất khẩu-Thời gian (Exp-Year FE + Imp FE)
    G4: Sức cản Nhập khẩu-Thời gian (Exp FE + Imp-Year FE)
    G5: Trọng lực Cổ điển (Exp FE + Imp FE + Year FE)
    G6: Mô hình rút gọn (Pair FE + Year FE + ln_exporter_lsci)
    """
    ensure_directories()
    bilateral_file = os.path.join(PROCESSED_DIR, 'panel_bilateral_year.csv')
    df = pd.read_csv(bilateral_file)
    
    # Mẫu ước lượng chuẩn 2010-2024 (chỉ lấy các quan sát hợp lệ, loại trừ VNM 2024 chưa báo cáo)
    sample = df[(df['year'] <= 2024) & (df['trade_usd'].notnull()) & (df['ln_lsbci'].notnull())].copy()
    
    # Chuyển đổi đơn vị thành triệu USD để tối ưu độ ổn định số học trong thuật toán IRLS
    # (Đặc tính bất biến của Poisson: hệ số góc độ co giãn ln(LSBCI) không bị thay đổi)
    sample['trade_million'] = sample['trade_usd'] / 1e6
    
    specs = [
        {
            'id': 'G1',
            'name': 'G1: Cấu trúc đầy đủ\n[Cặp, XK-Năm, NK-Năm]',
            'is_structural': True,
            'pair_fe': 'Có',
            'year_fe': 'Hấp thụ',
            'exp_year_fe': 'Có',
            'imp_year_fe': 'Có',
            'exp_fe': 'Hấp thụ',
            'imp_fe': 'Hấp thụ'
        },
        {
            'id': 'G2',
            'name': 'G2: Trọng lực chuẩn\n[Cặp FE + Năm FE]',
            'is_structural': False,
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
            'id': 'G3',
            'name': 'G3: Sức cản xuất khẩu\n[XK-Năm FE + NK FE]',
            'is_structural': False,
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
            'name': 'G4: Sức cản nhập khẩu\n[XK FE + NK-Năm FE]',
            'is_structural': False,
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
            'name': 'G5: Trọng lực cổ điển\n[Nước FE + Năm FE]',
            'is_structural': False,
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
            'id': 'G6',
            'name': 'G6: Mô hình rút gọn\n[LSBCI + LSCI]',
            'is_structural': False,
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
    structured_results = {}
    cols_header = []
    
    print("=== [ESTIMATION] Bắt đầu ước lượng các mô hình Trọng lực PPML (Tầng B) ===")
    print(f"Tổng số quan sát hợp lệ: {len(sample)} | Số cặp: {sample['pair_id'].nunique()} | Số quan sát 0: {(sample['trade_usd'] == 0).sum()}")
    
    for s in specs:
        model_name = s['name']
        m_id = s['id']
        cols_header.append(model_name)
        print(f"\n--- Đang ước lượng mô hình {m_id}: {model_name.replace(chr(10), ' ')} ---")
        
        if s.get('is_structural', False):
            res = fit_structural_gravity(sample)
        else:
            res = smf.glm(
                s['formula'],
                data=sample,
                family=sm.families.Poisson()
            ).fit(cov_type='cluster', use_t=True, cov_kwds={'groups': sample[s['cluster']]}, maxiter=100)
            
        print(f"  ✓ Hội tụ: {res.converged} | Pseudo LL: {res.llf:.1f}")
        
        # Trích xuất hệ số ln_lsbci
        c_lsbci = float(res.params.get('ln_lsbci', np.nan))
        se_lsbci = float(res.bse.get('ln_lsbci', np.nan))
        p_lsbci = float(res.pvalues.get('ln_lsbci', np.nan))
        t_lsbci = float(res.tvalues.get('ln_lsbci', np.nan))
        stars_lsbci = '***' if p_lsbci < 0.01 else '**' if p_lsbci < 0.05 else '*' if p_lsbci < 0.1 else ''
        print(f"  -> ln_lsbci: {c_lsbci:.3f}{stars_lsbci} (SE = {se_lsbci:.3f}, p = {format_pval(p_lsbci)})")
        
        # Trích xuất hệ số ln_exporter_lsci (nếu có trong G6)
        c_lsci = np.nan
        se_lsci = np.nan
        p_lsci = np.nan
        t_lsci = np.nan
        val_lsci_str = ""
        se_lsci_str = ""
        if 'ln_exporter_lsci' in res.params:
            c_lsci = float(res.params['ln_exporter_lsci'])
            se_lsci = float(res.bse['ln_exporter_lsci'])
            p_lsci = float(res.pvalues['ln_exporter_lsci'])
            t_lsci = float(res.tvalues['ln_exporter_lsci'])
            stars_lsci = '***' if p_lsci < 0.01 else '**' if p_lsci < 0.05 else '*' if p_lsci < 0.1 else ''
            val_lsci_str = f"{c_lsci:.3f}{stars_lsci}"
            se_lsci_str = f"({se_lsci:.3f})"
            print(f"  -> ln_exporter_lsci: {c_lsci:.3f}{stars_lsci} (SE = {se_lsci:.3f}, p = {format_pval(p_lsci)})")
            
        results[model_name] = {
            'ln_lsbci': f"{c_lsbci:.3f}{stars_lsbci}",
            'ln_lsbci_se': f"({se_lsbci:.3f})",
            'ln_exporter_lsci': val_lsci_str,
            'ln_exporter_lsci_se': se_lsci_str,
            'pair_fe': s['pair_fe'],
            'year_fe': s['year_fe'],
            'exp_year_fe': s['exp_year_fe'],
            'imp_year_fe': s['imp_year_fe'],
            'exp_fe': s['exp_fe'],
            'imp_fe': s['imp_fe'],
            'n_obs': len(sample),
            'n_pairs': sample['pair_id'].nunique(),
            'zero_obs': int((sample['trade_usd'] == 0).sum()),
            'pseudo_ll': f"{res.llf:.1f}"
        }
        
        structured_results[m_id] = {
            'model_id': m_id,
            'name': model_name.replace('\n', ' '),
            'n_obs': int(len(sample)),
            'n_pairs': int(sample['pair_id'].nunique()),
            'zero_obs': int((sample['trade_usd'] == 0).sum()),
            'converged': bool(res.converged),
            'pseudo_ll': float(res.llf),
            'ln_lsbci': {
                'coef': c_lsbci,
                'se': se_lsbci,
                'tval': t_lsbci,
                'pval': p_lsbci
            },
            'ln_exporter_lsci': {
                'coef': c_lsci,
                'se': se_lsci,
                'tval': t_lsci,
                'pval': p_lsci
            } if not np.isnan(c_lsci) else None
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
        'Hiệu ứng Nước xuất khẩu',
        'Hiệu ứng Nước nhập khẩu',
        'Số quan sát (N)',
        'Số cặp quốc gia',
        'Số quan sát thương mại bằng 0',
        'Sai số chuẩn phân cụm',
        'Pseudo Log-likelihood'
    ]
    
    table_dict = {row: [] for row in row_labels}
    for col in cols_header:
        r = results[col]
        table_dict['ln(LSBCI song phương)'].append(r['ln_lsbci'])
        table_dict['ln(LSBCI song phương) (SE)'].append(r['ln_lsbci_se'])
        table_dict['ln(LSCI nước xuất khẩu)'].append(r['ln_exporter_lsci'])
        table_dict['ln(LSCI nước xuất khẩu) (SE)'].append(r['ln_exporter_lsci_se'])
        table_dict['Hiệu ứng cố định Cặp quốc gia'].append(r['pair_fe'])
        table_dict['Hiệu ứng cố định Năm'].append(r['year_fe'])
        table_dict['Hiệu ứng Xuất khẩu - Năm'].append(r['exp_year_fe'])
        table_dict['Hiệu ứng Nhập khẩu - Năm'].append(r['imp_year_fe'])
        table_dict['Hiệu ứng Nước xuất khẩu'].append(r['exp_fe'])
        table_dict['Hiệu ứng Nước nhập khẩu'].append(r['imp_fe'])
        table_dict['Số quan sát (N)'].append(r['n_obs'])
        table_dict['Số cặp quốc gia'].append(r['n_pairs'])
        table_dict['Số quan sát thương mại bằng 0'].append(r['zero_obs'])
        table_dict['Sai số chuẩn phân cụm'].append('Cluster (pair_id, t-dist)')
        table_dict['Pseudo Log-likelihood'].append(r['pseudo_ll'])
        
    df_table = pd.DataFrame(table_dict, index=cols_header).T
    
    out_csv = os.path.join(TABLES_DIR, 'table_gravity_ppml_models.csv')
    out_tex = os.path.join(TABLES_DIR, 'table_gravity_ppml_models.tex')
    df_table.to_csv(out_csv)
    df_table.to_latex(out_tex, caption='Kết quả ước lượng mô hình Trọng lực PPML song phương (2010--2024)', label='tab:gravity_ppml')
    
    out_json = os.path.join(TABLES_DIR, 'model_gravity_results.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(structured_results, f, ensure_ascii=False, indent=2)
        
    print(f"\n[THÀNH CÔNG] Đã lưu bảng kết quả hồi quy Trọng lực Tầng B vào:\n  {out_csv}\n  {out_tex}\n  {out_json}")
    return df_table

if __name__ == '__main__':
    estimate_gravity_models()
