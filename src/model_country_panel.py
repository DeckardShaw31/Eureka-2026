import os
import json
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from clean_common import ensure_directories, format_coef_se, format_pval

PROCESSED_DIR = os.path.join('data', 'processed')
TABLES_DIR = os.path.join('outputs', 'tables')
LOGS_DIR = os.path.join('outputs', 'logs')

def estimate_country_models():
    """
    Ước lượng các mô hình kinh tế lượng Tầng A theo Mục 4.1 của design.md:
    M1: ln_lsci + Country FE + Year FE
    M2: M1 + ln_gdp + ln_population
    M3: M2 + fdi_gdp + fx_growth
    M4: M2 với ln_lsci_lag1 (biến trễ 1 năm để giảm thiểu nội sinh)
    M5: M2 + tương tác ln_lsci * clmv (kiểm định giả thuyết H3 về hiệu ứng phân hóa)
    
    Phương pháp suy diễn thống kê:
    - Clustered Standard Errors theo cấp Quốc gia (iso3)
    - Sử dụng hiệu chỉnh mẫu nhỏ với phân phối Student-t (use_t=True, Cameron & Miller 2015)
    - Kiểm định tổ hợp tuyến tính (linear restriction test) cho tổng tác động CLMV: beta_LSCI + beta_Interact
    """
    ensure_directories()
    country_file = os.path.join(PROCESSED_DIR, 'panel_country_year.csv')
    df = pd.read_csv(country_file)
    
    # Mẫu ước lượng chuẩn 2010-2024 (loại trừ năm 2025 chỉ dùng phân tích mô tả)
    sample = df[df['year'] <= 2024].copy()
    sample['lsci_clmv'] = sample['ln_lsci'] * sample['clmv']
    
    model_configs = [
        {
            'id': 'M1',
            'name': 'M1: Cơ sở (LSCI)',
            'ols_formula': 'ln_export ~ ln_lsci + C(iso3) + C(year)',
            'ppml_formula': 'export_usd ~ ln_lsci + C(iso3) + C(year)',
            'vars': ['ln_lsci'],
            'data': sample
        },
        {
            'id': 'M2',
            'name': 'M2: Mở rộng (GDP & Dân số)',
            'ols_formula': 'ln_export ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'ppml_formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'vars': ['ln_lsci', 'ln_gdp', 'ln_population'],
            'data': sample
        },
        {
            'id': 'M3',
            'name': 'M3: Thêm FDI & Tỷ giá',
            'ols_formula': 'ln_export ~ ln_lsci + ln_gdp + ln_population + fdi_gdp + fx_growth + C(iso3) + C(year)',
            'ppml_formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + fdi_gdp + fx_growth + C(iso3) + C(year)',
            'vars': ['ln_lsci', 'ln_gdp', 'ln_population', 'fdi_gdp', 'fx_growth'],
            'data': sample.dropna(subset=['fdi_gdp', 'fx_growth'])
        },
        {
            'id': 'M4',
            'name': 'M4: Biến trễ (LSCI Lag 1)',
            'ols_formula': 'ln_export ~ ln_lsci_lag1 + ln_gdp + ln_population + C(iso3) + C(year)',
            'ppml_formula': 'export_usd ~ ln_lsci_lag1 + ln_gdp + ln_population + C(iso3) + C(year)',
            'vars': ['ln_lsci_lag1', 'ln_gdp', 'ln_population'],
            'data': sample.dropna(subset=['ln_lsci_lag1'])
        },
        {
            'id': 'M5',
            'name': 'M5: Dị biệt ASEAN-6 vs CLMV',
            'ols_formula': 'ln_export ~ ln_lsci + lsci_clmv + ln_gdp + ln_population + C(iso3) + C(year)',
            'ppml_formula': 'export_usd ~ ln_lsci + lsci_clmv + ln_gdp + ln_population + C(iso3) + C(year)',
            'vars': ['ln_lsci', 'lsci_clmv', 'ln_gdp', 'ln_population'],
            'data': sample
        }
    ]
    
    table_rows = {}
    structured_results = {}
    
    # Danh sách các biến hiển thị trong bảng
    display_vars = [
        'ln_lsci', 
        'ln_lsci_lag1', 
        'lsci_clmv', 
        'total_clmv_effect',
        'ln_gdp', 
        'ln_population', 
        'fdi_gdp', 
        'fx_growth'
    ]
    var_labels = {
        'ln_lsci': 'ln(LSCI)',
        'ln_lsci_lag1': 'ln(LSCI trễ 1 năm)',
        'lsci_clmv': 'ln(LSCI) × CLMV (chênh lệch)',
        'total_clmv_effect': 'Tổng tác động LSCI đối với CLMV (LSCI + Tương tác)',
        'ln_gdp': 'ln(GDP)',
        'ln_population': 'ln(Dân số)',
        'fdi_gdp': 'FDI ròng (% GDP)',
        'fx_growth': 'Tăng trưởng tỷ giá'
    }
    
    for v in display_vars:
        table_rows[f"{var_labels[v]}"] = []
        table_rows[f"{var_labels[v]} (SE)"] = []
        
    cols_header = []
    
    print("=== [ESTIMATION] Bắt đầu ước lượng các mô hình Quốc gia - Năm (Tầng A) ===")
    for cfg in model_configs:
        sub_df = cfg['data'].copy()
        model_name = cfg['name']
        m_id = cfg['id']
        n_clusters = sub_df['iso3'].nunique()
        print(f"\n--- Ước lượng {model_name} (N = {len(sub_df)}, Số cụm = {n_clusters}) ---")
        
        # 1. Ước lượng OLS TWFE (Clustered SE by iso3, small sample t-distribution)
        res_ols = smf.ols(cfg['ols_formula'], data=sub_df).fit(
            cov_type='cluster', use_t=True, cov_kwds={'groups': sub_df['iso3']}
        )
        col_ols = f"{cfg['name']}\n[OLS TWFE]"
        cols_header.append(col_ols)
        
        # 2. Ước lượng PPML (Poisson GLM with log-link, Clustered SE by iso3, small sample t-distribution)
        res_ppml = smf.glm(
            cfg['ppml_formula'], data=sub_df, family=sm.families.Poisson()
        ).fit(cov_type='cluster', use_t=True, cov_kwds={'groups': sub_df['iso3']})
        col_ppml = f"{cfg['name']}\n[PPML]"
        cols_header.append(col_ppml)
        
        # Lưu kết quả có cấu trúc cho OLS và PPML
        structured_results[f"{m_id}_OLS"] = {
            'model_id': m_id,
            'estimator': 'OLS TWFE',
            'n_obs': int(len(sub_df)),
            'n_clusters': int(n_clusters),
            'r2': float(res_ols.rsquared),
            'params': {k: float(v) for k, v in res_ols.params.items()},
            'bse': {k: float(v) for k, v in res_ols.bse.items()},
            'pvalues': {k: float(v) for k, v in res_ols.pvalues.items()},
            'tvalues': {k: float(v) for k, v in res_ols.tvalues.items()}
        }
        structured_results[f"{m_id}_PPML"] = {
            'model_id': m_id,
            'estimator': 'PPML',
            'n_obs': int(len(sub_df)),
            'n_clusters': int(n_clusters),
            'llf': float(res_ppml.llf),
            'params': {k: float(v) for k, v in res_ppml.params.items()},
            'bse': {k: float(v) for k, v in res_ppml.bse.items()},
            'pvalues': {k: float(v) for k, v in res_ppml.pvalues.items()},
            'tvalues': {k: float(v) for k, v in res_ppml.tvalues.items()}
        }
        
        # Tính toán tổ hợp tuyến tính cho M5 (Tổng tác động LSCI lên CLMV)
        ols_clmv_total = None
        ppml_clmv_total = None
        if m_id == 'M5':
            # Wald / t-test: beta_ln_lsci + beta_lsci_clmv = 0
            ttest_ols = res_ols.t_test('ln_lsci + lsci_clmv = 0')
            ols_clmv_total = {
                'coef': float(ttest_ols.effect.item() if hasattr(ttest_ols.effect, 'item') else ttest_ols.effect),
                'se': float(ttest_ols.sd.item() if hasattr(ttest_ols.sd, 'item') else ttest_ols.sd),
                'tval': float(ttest_ols.tvalue.item() if hasattr(ttest_ols.tvalue, 'item') else ttest_ols.tvalue),
                'pval': float(ttest_ols.pvalue.item() if hasattr(ttest_ols.pvalue, 'item') else ttest_ols.pvalue)
            }
            structured_results[f"{m_id}_OLS"]['total_clmv_effect'] = ols_clmv_total
            print(f"  [M5 OLS] Tổng tác động CLMV = {ols_clmv_total['coef']:.3f} (SE = {ols_clmv_total['se']:.3f}, p = {format_pval(ols_clmv_total['pval'])})")
            
            ttest_ppml = res_ppml.t_test('ln_lsci + lsci_clmv = 0')
            ppml_clmv_total = {
                'coef': float(ttest_ppml.effect.item() if hasattr(ttest_ppml.effect, 'item') else ttest_ppml.effect),
                'se': float(ttest_ppml.sd.item() if hasattr(ttest_ppml.sd, 'item') else ttest_ppml.sd),
                'tval': float(ttest_ppml.tvalue.item() if hasattr(ttest_ppml.tvalue, 'item') else ttest_ppml.tvalue),
                'pval': float(ttest_ppml.pvalue.item() if hasattr(ttest_ppml.pvalue, 'item') else ttest_ppml.pvalue)
            }
            structured_results[f"{m_id}_PPML"]['total_clmv_effect'] = ppml_clmv_total
            print(f"  [M5 PPML] Tổng tác động CLMV = {ppml_clmv_total['coef']:.3f} (SE = {ppml_clmv_total['se']:.3f}, p = {format_pval(ppml_clmv_total['pval'])})")

        # Điền dữ liệu vào bảng kết quả
        for v in display_vars:
            if v == 'total_clmv_effect':
                if m_id == 'M5' and ols_clmv_total is not None and ppml_clmv_total is not None:
                    # OLS
                    c, se, p = ols_clmv_total['coef'], ols_clmv_total['se'], ols_clmv_total['pval']
                    stars = '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.1 else ''
                    table_rows[f"{var_labels[v]}"].append(f"{c:.3f}{stars}")
                    table_rows[f"{var_labels[v]} (SE)"].append(f"({se:.3f})")
                    # PPML
                    c, se, p = ppml_clmv_total['coef'], ppml_clmv_total['se'], ppml_clmv_total['pval']
                    stars = '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.1 else ''
                    table_rows[f"{var_labels[v]}"].append(f"{c:.3f}{stars}")
                    table_rows[f"{var_labels[v]} (SE)"].append(f"({se:.3f})")
                else:
                    table_rows[f"{var_labels[v]}"].extend(["", ""])
                    table_rows[f"{var_labels[v]} (SE)"].extend(["", ""])
                continue

            # OLS
            if v in res_ols.params:
                c = res_ols.params[v]
                se = res_ols.bse[v]
                p = res_ols.pvalues[v]
                stars = '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.1 else ''
                table_rows[f"{var_labels[v]}"].append(f"{c:.3f}{stars}")
                table_rows[f"{var_labels[v]} (SE)"].append(f"({se:.3f})")
            else:
                table_rows[f"{var_labels[v]}"].append("")
                table_rows[f"{var_labels[v]} (SE)"].append("")
                
            # PPML
            if v in res_ppml.params:
                c = res_ppml.params[v]
                se = res_ppml.bse[v]
                p = res_ppml.pvalues[v]
                stars = '***' if p < 0.01 else '**' if p < 0.05 else '*' if p < 0.1 else ''
                table_rows[f"{var_labels[v]}"].append(f"{c:.3f}{stars}")
                table_rows[f"{var_labels[v]} (SE)"].append(f"({se:.3f})")
            else:
                table_rows[f"{var_labels[v]}"].append("")
                table_rows[f"{var_labels[v]} (SE)"].append("")
                
    df_table = pd.DataFrame(table_rows, index=cols_header).T
    
    # Thêm các hàng thống kê và chẩn đoán
    r2_row = []
    for cfg in model_configs:
        m_id = cfg['id']
        r2_row.append(f"{structured_results[f'{m_id}_OLS']['r2']:.3f}")
        r2_row.append("-")
        
    extra_rows = pd.DataFrame([
        ['Có'] * len(cols_header),
        ['Có'] * len(cols_header),
        [len(cfg['data']) for cfg in model_configs for _ in range(2)],
        [sub_df['iso3'].nunique() for _ in range(len(cols_header))],
        ['Cluster (iso3, t-dist)'] * len(cols_header),
        r2_row
    ], index=[
        'Hiệu ứng cố định Quốc gia (FE)', 
        'Hiệu ứng cố định Năm (FE)', 
        'Số quan sát (N)', 
        'Số cụm quốc gia (Clusters)', 
        'Phương pháp sai số chuẩn',
        'R-squared'
    ], columns=cols_header)
    
    final_table = pd.concat([df_table, extra_rows])
    
    # Xuất file CSV và LaTeX
    out_csv = os.path.join(TABLES_DIR, 'table_country_panel_models.csv')
    out_tex = os.path.join(TABLES_DIR, 'table_country_panel_models.tex')
    final_table.to_csv(out_csv)
    final_table.to_latex(out_tex, caption='Kết quả ước lượng mô hình Quốc gia--Năm (OLS TWFE và PPML, 2010--2024)', label='tab:country_panel')
    
    # Xuất file JSON có cấu trúc để các script khác tiêu thụ động
    out_json = os.path.join(TABLES_DIR, 'model_country_results.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(structured_results, f, ensure_ascii=False, indent=2)
        
    print(f"\n[THÀNH CÔNG] Đã lưu bảng kết quả hồi quy Tầng A vào:\n  {out_csv}\n  {out_tex}\n  {out_json}")
    return final_table

if __name__ == '__main__':
    estimate_country_models()
