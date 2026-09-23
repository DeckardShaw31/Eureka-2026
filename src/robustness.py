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

def run_robustness_checks():
    """
    Thực hiện 11 kiểm định độ bền và độ nhạy theo Mục 11.3 của design.md:
    1. Mẫu cơ sở PPML (Toàn bộ 9 nước ASEAN ven biển, 2010-2024)
    2. Kiểm soát xu hướng thời gian riêng của từng quốc gia (Country-specific linear trends)
    3. Loại bỏ Singapore (loại ngoại lai trung tâm trung chuyển hàng hải)
    4. Mẫu tiền COVID-19 (2010-2019)
    5. Loại bỏ 2 năm biến động bất thường COVID-19 (2020-2021)
    6. Mẫu phân nhóm ASEAN-6 (phát triển hơn)
    7. Mẫu phân nhóm CLMV ven biển (KHM, MMR, VNM - thu nhập thấp hơn)
    8. Phân tích theo nhóm hàng: Chế biến - Chế tạo chuẩn (HS 28-96, tách biệt nhiên liệu)
    9. Phân tích theo nhóm hàng: Nhiên liệu & Khoáng sản (HS 25-27, cô lập dầu khí Brunei)
    10. Phân tích theo nhóm hàng: Nông - Thủy sản (HS 01-24)
    11. Kiểm định kỳ vọng/dẫn trước Placebo (LSCI Lead 1)
    
    Tất cả các mô hình đều áp dụng Clustered SE theo quốc gia và hiệu chỉnh mẫu nhỏ Student-t.
    """
    ensure_directories()
    country_file = os.path.join(PROCESSED_DIR, 'panel_country_year.csv')
    df = pd.read_csv(country_file)
    sample_full = df[df['year'] <= 2024].copy()
    
    # Tạo biến xu hướng thời gian tuyến tính
    sample_full['trend'] = sample_full['year'] - 2010
    
    # Tạo biến lead 1 cho kiểm định placebo
    sample_full['ln_lsci_lead1'] = sample_full.groupby('iso3')['ln_lsci'].shift(-1)
    
    robustness_specs = [
        {
            'id': 'R1_baseline',
            'name': '1. Mẫu cơ sở (2010–2024)',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full,
            'key_var': 'ln_lsci',
            'desc': 'Toàn bộ 9 nước ASEAN ven biển'
        },
        {
            'id': 'R2_country_trends',
            'name': '2. Xu hướng thời gian từng nước',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year) + C(iso3):trend',
            'data': sample_full,
            'key_var': 'ln_lsci',
            'desc': 'Kiểm soát xu hướng tuyến tính riêng của từng nước'
        },
        {
            'id': 'R3_no_sgp',
            'name': '3. Loại Singapore (Không ngoại lai)',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['iso3'] != 'SGP'],
            'key_var': 'ln_lsci',
            'desc': 'Loại trừ cảng trung chuyển lớn nhất'
        },
        {
            'id': 'R4_pre_covid',
            'name': '4. Tiền COVID (2010–2019)',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['year'] <= 2019],
            'key_var': 'ln_lsci',
            'desc': 'Tránh cú sốc đại dịch toàn cầu'
        },
        {
            'id': 'R5_no_covid_years',
            'name': '5. Loại năm 2020–2021',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[~sample_full['year'].isin([2020, 2021])],
            'key_var': 'ln_lsci',
            'desc': 'Loại trừ đứt gãy chuỗi cung ứng'
        },
        {
            'id': 'R6_asean6',
            'name': '6. Phân nhóm ASEAN-6',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['asean6'] == 1],
            'key_var': 'ln_lsci',
            'desc': 'Các nền kinh tế phát triển hơn'
        },
        {
            'id': 'R7_clmv',
            'name': '7. Phân nhóm CLMV có biển',
            'formula': 'export_usd ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['clmv'] == 1],
            'key_var': 'ln_lsci',
            'desc': 'Campuchia, Myanmar, Việt Nam (3 nước)'
        },
        {
            'id': 'R8_manufacturing',
            'name': '8. Chế biến – Chế tạo (HS 28–96)',
            'formula': 'export_usd_mfg ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['export_usd_mfg'] > 0],
            'key_var': 'ln_lsci',
            'desc': 'Kiểm định H4 (Đã bóc tách nhiên liệu khoáng sản)'
        },
        {
            'id': 'R9_fuels',
            'name': '9. Nhiên liệu & Khoáng sản (HS 25–27)',
            'formula': 'export_usd_fuels ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['export_usd_fuels'] > 0],
            'key_var': 'ln_lsci',
            'desc': 'Kiểm định H4 (Hàng rời/dầu mỏ, kiểm chứng Brunei)'
        },
        {
            'id': 'R10_agriculture',
            'name': '10. Nông – Thủy sản (HS 01–24)',
            'formula': 'export_usd_agri ~ ln_lsci + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full[sample_full['export_usd_agri'] > 0],
            'key_var': 'ln_lsci',
            'desc': 'Kiểm định H4 (Hàng nông nghiệp truyền thống)'
        },
        {
            'id': 'R11_placebo',
            'name': '11. Placebo Test (LSCI Lead 1)',
            'formula': 'export_usd ~ ln_lsci_lead1 + ln_gdp + ln_population + C(iso3) + C(year)',
            'data': sample_full.dropna(subset=['ln_lsci_lead1']),
            'key_var': 'ln_lsci_lead1',
            'desc': 'LSCI năm t+1 (Kiểm tra kỳ vọng & tự tương quan)'
        }
    ]
    
    rows = []
    structured_robustness = {}
    print("=== [ROBUSTNESS] Bắt đầu thực hiện các kiểm định độ bền ===")
    
    for spec in robustness_specs:
        s_data = spec['data']
        f = spec['formula']
        var = spec['key_var']
        s_id = spec['id']
        n_clusters = s_data['iso3'].nunique()
        print(f"\n--- Chạy {spec['name']} (N = {len(s_data)}, Cụm = {n_clusters}) ---")
        
        # PPML với Clustered SE theo quốc gia và phân phối Student-t (mẫu nhỏ)
        res = smf.glm(f, data=s_data, family=sm.families.Poisson()).fit(
            cov_type='cluster', use_t=True, cov_kwds={'groups': s_data['iso3']}
        )
        
        coef = float(res.params.get(var, np.nan))
        se = float(res.bse.get(var, np.nan))
        pval = float(res.pvalues.get(var, np.nan))
        tval = float(res.tvalues.get(var, np.nan))
        stars = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.1 else ''
        
        # Hệ số GDP
        c_gdp = float(res.params.get('ln_gdp', np.nan)) if 'ln_gdp' in res.params else np.nan
        se_gdp = float(res.bse.get('ln_gdp', np.nan)) if 'ln_gdp' in res.bse else np.nan
        p_gdp = float(res.pvalues.get('ln_gdp', np.nan)) if 'ln_gdp' in res.pvalues else np.nan
        stars_gdp = '***' if p_gdp < 0.01 else '**' if p_gdp < 0.05 else '*' if p_gdp < 0.1 else ''
        
        formatted_pval = format_pval(pval)
        print(f"  -> {var}: {coef:.3f}{stars} (SE = {se:.3f}, p = {formatted_pval})")
        
        rows.append({
            'Kiểm định độ bền': spec['name'],
            'Mô tả mẫu': spec['desc'],
            'Hệ số LSCI': f"{coef:.3f}{stars}",
            'SE LSCI': f"({se:.3f})",
            'P-value LSCI': formatted_pval,
            'Hệ số ln(GDP)': f"{c_gdp:.3f}{stars_gdp}" if not np.isnan(c_gdp) else "-",
            'SE GDP': f"({se_gdp:.3f})" if not np.isnan(se_gdp) else "-",
            'Số quan sát (N)': len(s_data),
            'Số nước': n_clusters,
            'Pseudo LL': f"{res.llf:.1f}"
        })
        
        structured_robustness[s_id] = {
            'id': s_id,
            'name': spec['name'],
            'desc': spec['desc'],
            'key_var': var,
            'n_obs': int(len(s_data)),
            'n_clusters': int(n_clusters),
            'pseudo_ll': float(res.llf),
            'estimates': {
                'coef': coef,
                'se': se,
                'tval': tval,
                'pval': pval
            },
            'gdp_estimates': {
                'coef': c_gdp,
                'se': se_gdp,
                'pval': p_gdp
            } if not np.isnan(c_gdp) else None
        }
        
    df_robust = pd.DataFrame(rows)
    out_csv = os.path.join(TABLES_DIR, 'table_robustness.csv')
    out_tex = os.path.join(TABLES_DIR, 'table_robustness.tex')
    df_robust.to_csv(out_csv, index=False)
    df_robust.to_latex(out_tex, index=False, caption='Tổng hợp các kiểm định độ bền và độ nhạy (PPML, 2010--2024)', label='tab:robustness')
    
    out_json = os.path.join(TABLES_DIR, 'model_robustness_results.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(structured_robustness, f, ensure_ascii=False, indent=2)
        
    print(f"\n[THÀNH CÔNG] Đã lưu bảng kiểm định độ bền vào:\n  {out_csv}\n  {out_tex}\n  {out_json}")
    return df_robust

if __name__ == '__main__':
    run_robustness_checks()
