import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from clean_common import ensure_directories

PROCESSED_DIR = os.path.join('data', 'processed')
TABLES_DIR = os.path.join('outputs', 'tables')

def run_robustness_checks():
    """
    Thực hiện 7 kiểm định độ bền nghiêm ngặt theo Mục 11.3 của design.md:
    1. Baseline M2 PPML (Mẫu đầy đủ 2010-2024)
    2. Loại bỏ Singapore (loại ngoại lai trung tâm trung chuyển hàng hải)
    3. Mẫu tiền COVID-19 (2010-2019)
    4. Loại bỏ 2 năm biến động bất thường COVID-19 (2020-2021)
    5. Mẫu nhóm ASEAN-6
    6. Mẫu nhóm CLMV ven biển (KHM, MMR, VNM)
    7. Phân tích theo nhóm hàng: Nông-Thủy sản (HS 01-24)
    8. Phân tích theo nhóm hàng: Chế biến - Chế tạo (HS 25-97)
    9. Placebo test: Kiểm tra ngoại sinh bằng LSCI tương lai (Lead 1)
    """
    ensure_directories()
    country_file = os.path.join(PROCESSED_DIR, 'panel_country_year.csv')
    df = pd.read_csv(country_file)
    sample_full = df[df['year'] <= 2024].copy()
    
    # Tạo biến lead 1 cho placebo test
    sample_full['ln_lsci_lead1'] = sample_full.groupby('iso3')['ln_lsci'].shift(-1)
    
    robustness_specs = [
        {
            'name': '1. Mẫu cơ sở (2010–2024)',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full,
            'key_var': 'ln_lsci',
            'desc': 'Toàn bộ 9 nước ASEAN ven biển'
        },
        {
            'name': '2. Loại Singapore (Không ngoại lai)',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['iso3'] != 'SGP'],
            'key_var': 'ln_lsci',
            'desc': 'Loại trừ cảng trung chuyển lớn nhất'
        },
        {
            'name': '3. Tiền COVID (2010–2019)',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['year'] <= 2019],
            'key_var': 'ln_lsci',
            'desc': 'Tránh cú sốc đại dịch toàn cầu'
        },
        {
            'name': '4. Loại năm 2020–2021',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[~sample_full['year'].isin([2020, 2021])],
            'key_var': 'ln_lsci',
            'desc': 'Loại trừ đứt gãy chuỗi cung ứng'
        },
        {
            'name': '5. Phân nhóm ASEAN-6',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['asean6'] == 1],
            'key_var': 'ln_lsci',
            'desc': 'Các nền kinh tế phát triển hơn'
        },
        {
            'name': '6. Phân nhóm CLMV có biển',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['clmv'] == 1],
            'key_var': 'ln_lsci',
            'desc': 'Campuchia, Myanmar, Việt Nam'
        },
        {
            'name': '7. Nông – Thủy sản (HS 01–24)',
            'formula': 'export_usd_agri ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['export_usd_agri'] > 0],
            'key_var': 'ln_lsci',
            'desc': 'Kiểm định giả thuyết H4'
        },
        {
            'name': '8. Chế biến – Chế tạo (HS 25–97)',
            'formula': 'export_usd_mfg ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['export_usd_mfg'] > 0],
            'key_var': 'ln_lsci',
            'desc': 'Kiểm định giả thuyết H4'
        },
        {
            'name': '9. Placebo Test (LSCI Lead 1)',
            'formula': 'export_usd ~ ln_lsci_lead1 + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full.dropna(subset=['ln_lsci_lead1']),
            'key_var': 'ln_lsci_lead1',
            'desc': 'LSCI tương lai giải thích hiện tại'
        }
    ]
    
    rows = []
    print("=== [ROBUSTNESS] Bắt đầu thực hiện các kiểm định độ bền ===")
    for spec in robustness_specs:
        s_data = spec['data']
        f = spec['formula']
        var = spec['key_var']
        print(f"\n--- Chạy {spec['name']} (N = {len(s_data)}) ---")
        
        # PPML với Clustered SE theo quốc gia
        res = smf.glm(f, data=s_data, family=sm.families.Poisson()).fit(
            cov_type='cluster', cov_kwds={'groups': s_data['iso3']}
        )
        
        coef = res.params.get(var, np.nan)
        se = res.bse.get(var, np.nan)
        pval = res.pvalues.get(var, np.nan)
        stars = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.1 else ''
        
        # Lấy thêm hệ số GDP
        c_gdp = res.params.get('ln_gdp', np.nan)
        se_gdp = res.bse.get('ln_gdp', np.nan)
        p_gdp = res.pvalues.get('ln_gdp', np.nan)
        stars_gdp = '***' if p_gdp < 0.01 else '**' if p_gdp < 0.05 else '*' if p_gdp < 0.1 else ''
        
        rows.append({
            'Kiểm định độ bền': spec['name'],
            'Mô tả mẫu': spec['desc'],
            'Hệ số LSCI': f"{coef:.3f}{stars}",
            'SE LSCI': f"({se:.3f})",
            'P-value LSCI': f"{pval:.4f}",
            'Hệ số ln(GDP)': f"{c_gdp:.3f}{stars_gdp}",
            'SE GDP': f"({se_gdp:.3f})",
            'Số quan sát (N)': len(s_data),
            'Số nước': s_data['iso3'].nunique(),
            'Pseudo LL': f"{res.llf:.1f}"
        })
        
    df_robust = pd.DataFrame(rows)
    out_csv = os.path.join(TABLES_DIR, 'table_robustness.csv')
    out_tex = os.path.join(TABLES_DIR, 'table_robustness.tex')
    df_robust.to_csv(out_csv, index=False)
    df_robust.to_latex(out_tex, index=False, caption='Tổng hợp các kiểm định độ bền và độ nhạy (PPML)', label='tab:robustness')
    print(f"\n[THÀNH CÔNG] Đã lưu bảng kiểm định độ bền vào:\n  {out_csv}\n  {out_tex}")
    return df_robust

if __name__ == '__main__':
    run_robustness_checks()
