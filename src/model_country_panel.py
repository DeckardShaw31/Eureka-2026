import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from clean_common import ensure_directories

PROCESSED_DIR = os.path.join('data', 'processed')
TABLES_DIR = os.path.join('outputs', 'tables')
LOGS_DIR = os.path.join('outputs', 'logs')

def format_coef_se(coef, se, pval):
    """Định dạng hệ số kèm dấu sao ý nghĩa thống kê và sai số chuẩn"""
    stars = ''
    if pval < 0.01:
        stars = '***'
    elif pval < 0.05:
        stars = '**'
    elif pval < 0.1:
        stars = '*'
    return f"{coef:.3f}{stars}\n({se:.3f})"

def estimate_country_models():
    """
    Ước lượng các mô hình kinh tế lượng Tầng A theo Mục 4.1 của design.md:
    M1: ln_lsci + Country FE + Year FE
    M2: M1 + ln_gdp + ln_population
    M3: M2 + fdi_gdp + fx_growth
    M4: M2 với ln_lsci_lag1 (biến trễ 1 năm để giảm thiểu nội sinh)
    M5: M2 + tương tác ln_lsci * clmv (kiểm định giả thuyết H3)
    """
    ensure_directories()
    country_file = os.path.join(PROCESSED_DIR, 'panel_country_year.csv')
    df = pd.read_csv(country_file)
    
    # Mẫu ước lượng chuẩn 2010-2024
    sample = df[df['year'] <= 2024].copy()
    sample['lsci_clmv'] = sample['ln_lsci'] * sample['clmv']
    
    model_configs = [
        {
            'name': 'M1: Cơ sở (LSCI)',
            'ols_formula': 'ln_export ~ ln_lsci + C(iso3) + C(year)',
            'ppml_formula': 'export_usd ~ ln_lsci + C(iso3) + C(year)',
            'vars': ['ln_lsci'],
            'data': sample
        },
        {
            'name': 'M2: Mở rộng (GDP & Dân số)',
            'ols_formula': 'ln_export ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'ppml_formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'vars': ['ln_lsci', 'ln_gdp', 'ln_population'],
            'data': sample
        },
        {
            'name': 'M3: Thêm FDI & Tỷ giá',
            'ols_formula': 'ln_export ~ ln_lsci + ln_gdp + ln_population + fdi_gdp + fx_growth + C(iso3) + C(year)',
            'ppml_formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + fdi_gdp + fx_growth + C(iso3) + C(year)',
            'vars': ['ln_lsci', 'ln_gdp', 'ln_population', 'fdi_gdp', 'fx_growth'],
            'data': sample.dropna(subset=['fdi_gdp', 'fx_growth'])
        },
        {
            'name': 'M4: Biến trễ (LSCI Lag 1)',
            'ols_formula': 'ln_export ~ ln_lsci_lag1 + ln_gdp + ln_population + C(iso3) + C(year)',
            'ppml_formula': 'export_usd ~ ln_lsci_lag1 + ln_gdp + ln_population + C(iso3) + C(year)',
            'vars': ['ln_lsci_lag1', 'ln_gdp', 'ln_population'],
            'data': sample.dropna(subset=['ln_lsci_lag1'])
        },
        {
            'name': 'M5: Dị biệt ASEAN-6 vs CLMV',
            'ols_formula': 'ln_export ~ ln_lsci + lsci_clmv + ln_gdp + ln_population + C(iso3) + C(year)',
            'ppml_formula': 'export_usd ~ ln_lsci + lsci_clmv + ln_gdp + ln_population + C(iso3) + C(year)',
            'vars': ['ln_lsci', 'lsci_clmv', 'ln_gdp', 'ln_population'],
            'data': sample
        }
    ]
    
    table_rows = {}
    summary_metrics = []
    
    # Danh sách các biến hiển thị trong bảng
    display_vars = ['ln_lsci', 'ln_lsci_lag1', 'lsci_clmv', 'ln_gdp', 'ln_population', 'fdi_gdp', 'fx_growth']
    var_labels = {
        'ln_lsci': 'ln(LSCI)',
        'ln_lsci_lag1': 'ln(LSCI trễ 1 năm)',
        'lsci_clmv': 'ln(LSCI) × CLMV',
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
        print(f"\n--- Ước lượng {model_name} (N = {len(sub_df)}) ---")
        
        # 1. Ước lượng OLS TWFE (Clustered SE by iso3)
        res_ols = smf.ols(cfg['ols_formula'], data=sub_df).fit(
            cov_type='cluster', cov_kwds={'groups': sub_df['iso3']}
        )
        col_ols = f"{cfg['name']}\n[OLS TWFE]"
        cols_header.append(col_ols)
        
        # 2. Ước lượng PPML (Poisson GLM with log-link, Clustered SE by iso3)
        res_ppml = smf.glm(
            cfg['ppml_formula'], data=sub_df, family=sm.families.Poisson()
        ).fit(cov_type='cluster', cov_kwds={'groups': sub_df['iso3']})
        col_ppml = f"{cfg['name']}\n[PPML]"
        cols_header.append(col_ppml)
        
        # Điền số liệu cho từng biến
        for v in display_vars:
            # OLS
            if v in res_ols.params:
                c = res_ols.params[v]
                se = res_ols.bse[v]
                p = res_ols.pvalues[v]
                table_rows[f"{var_labels[v]}"].append(f"{c:.3f}{'***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''}")
                table_rows[f"{var_labels[v]} (SE)"].append(f"({se:.3f})")
            else:
                table_rows[f"{var_labels[v]}"].append("")
                table_rows[f"{var_labels[v]} (SE)"].append("")
                
            # PPML
            if v in res_ppml.params:
                c = res_ppml.params[v]
                se = res_ppml.bse[v]
                p = res_ppml.pvalues[v]
                table_rows[f"{var_labels[v]}"].append(f"{c:.3f}{'***' if p<0.01 else '**' if p<0.05 else '*' if p<0.1 else ''}")
                table_rows[f"{var_labels[v]} (SE)"].append(f"({se:.3f})")
            else:
                table_rows[f"{var_labels[v]}"].append("")
                table_rows[f"{var_labels[v]} (SE)"].append("")
                
        # Thống kê mẫu
        summary_metrics.append({
            'col_ols': col_ols,
            'col_ppml': col_ppml,
            'n_obs': len(sub_df),
            'n_countries': sub_df['iso3'].nunique(),
            'ols_r2': round(res_ols.rsquared, 3),
            'ppml_ll': round(res_ppml.llf, 1)
        })
        
    df_table = pd.DataFrame(table_rows, index=cols_header).T
    
    # Thêm các hàng thống kê phía dưới
    extra_rows = pd.DataFrame([
        ['Có'] * len(cols_header),
        ['Có'] * len(cols_header),
        [len(cfg['data']) for cfg in model_configs for _ in range(2)],
        [9] * len(cols_header),
        ['Cluster (iso3)'] * len(cols_header)
    ], index=['Hiệu ứng cố định Quốc gia', 'Hiệu ứng cố định Năm', 'Số quan sát (N)', 'Số quốc gia', 'Sai số chuẩn'], columns=cols_header)
    
    final_table = pd.concat([df_table, extra_rows])
    
    out_csv = os.path.join(TABLES_DIR, 'table_country_panel_models.csv')
    out_tex = os.path.join(TABLES_DIR, 'table_country_panel_models.tex')
    final_table.to_csv(out_csv)
    final_table.to_latex(out_tex, caption='Kết quả ước lượng mô hình Quốc gia--Năm (OLS TWFE và PPML, 2010--2024)', label='tab:country_panel')
    print(f"\n[THÀNH CÔNG] Đã lưu bảng kết quả hồi quy Tầng A vào:\n  {out_csv}\n  {out_tex}")
    
    return final_table

if __name__ == '__main__':
    estimate_country_models()
