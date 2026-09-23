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

def estimate_pooled_product_panel(sample_full):
    """
    Ước lượng mô hình PPML gộp đa ngành hàng (Pooled Product-Panel PPML):
    Kiểm định trực tiếp giả thuyết H4 xem hệ số độ co giãn LSCI của ngành chế tạo
    có khác biệt có ý nghĩa thống kê so với nông sản và nhiên liệu hay không
    (tránh lỗi ngụy biện so sánh chéo hệ số theo Gelman & Stern, 2006).
    
    Quy đổi bảng sang dạng dọc: 9 nước x 15 năm x 3 nhóm hàng = 405 quan sát.
    Phương trình:
      E(Export_{ikt}) = exp[ beta_agri * ln_LSCI_{it} 
                            + beta_{diff_mfg} * (ln_LSCI_{it} x Mfg_k)
                            + beta_{diff_fuels} * (ln_LSCI_{it} x Fuels_k)
                            + C(product) + ln_gdp + ln_pop + C(iso3) + C(year) ]
    """
    records = []
    for _, r in sample_full.iterrows():
        # Nhóm 1: Nông - thủy sản (HS 01-24) - làm nhóm cơ sở (reference group)
        records.append({
            'iso3': r['iso3'], 'year': r['year'], 'ln_lsci': r['ln_lsci'],
            'ln_gdp': r['ln_gdp'], 'ln_population': r['ln_population'],
            'product': 'agri', 'export_val': r['export_usd_agri']
        })
        # Nhóm 2: Nhiên liệu & Khoáng sản (HS 25-27)
        records.append({
            'iso3': r['iso3'], 'year': r['year'], 'ln_lsci': r['ln_lsci'],
            'ln_gdp': r['ln_gdp'], 'ln_population': r['ln_population'],
            'product': 'fuels', 'export_val': r['export_usd_fuels']
        })
        # Nhóm 3: Chế biến - Chế tạo (HS 28-96)
        records.append({
            'iso3': r['iso3'], 'year': r['year'], 'ln_lsci': r['ln_lsci'],
            'ln_gdp': r['ln_gdp'], 'ln_population': r['ln_population'],
            'product': 'mfg', 'export_val': r['export_usd_mfg']
        })
    df_long = pd.DataFrame(records)
    df_long['is_mfg'] = (df_long['product'] == 'mfg').astype(int)
    df_long['is_fuels'] = (df_long['product'] == 'fuels').astype(int)
    df_long['lsci_mfg'] = df_long['ln_lsci'] * df_long['is_mfg']
    df_long['lsci_fuels'] = df_long['ln_lsci'] * df_long['is_fuels']
    
    formula = (
        'export_val ~ ln_lsci + lsci_mfg + lsci_fuels + C(product) '
        '+ ln_gdp + ln_population + C(iso3) + C(year)'
    )
    
    print("\n--- Chạy Mô hình gộp đa ngành hàng kiểm định khác biệt hệ số (N = 405, Cụm = 9) ---")
    res = smf.glm(formula, data=df_long, family=sm.families.Poisson()).fit(
        cov_type='cluster', use_t=True, cov_kwds={'groups': df_long['iso3']}
    )
    
    # 1. Hệ số cơ sở của Nông nghiệp
    c_agri = float(res.params['ln_lsci'])
    se_agri = float(res.bse['ln_lsci'])
    p_agri = float(res.pvalues['ln_lsci'])
    
    # 2. Chênh lệch Chế tạo vs Nông nghiệp (beta_diff_mfg)
    c_diff_mfg_agri = float(res.params['lsci_mfg'])
    se_diff_mfg_agri = float(res.bse['lsci_mfg'])
    t_diff_mfg_agri = float(res.tvalues['lsci_mfg'])
    p_diff_mfg_agri = float(res.pvalues['lsci_mfg'])
    stars_diff_mfg_agri = '***' if p_diff_mfg_agri < 0.01 else '**' if p_diff_mfg_agri < 0.05 else '*' if p_diff_mfg_agri < 0.1 else ''
    
    # 3. Chênh lệch Nhiên liệu vs Nông nghiệp (beta_diff_fuels)
    c_diff_fuels_agri = float(res.params['lsci_fuels'])
    se_diff_fuels_agri = float(res.bse['lsci_fuels'])
    p_diff_fuels_agri = float(res.pvalues['lsci_fuels'])
    
    # 4. Kiểm định tổ hợp tuyến tính: Chế tạo vs Nhiên liệu (lsci_mfg - lsci_fuels = 0)
    ttest_mfg_fuels = res.t_test('lsci_mfg - lsci_fuels = 0')
    c_diff_mfg_fuels = float(ttest_mfg_fuels.effect.item() if hasattr(ttest_mfg_fuels.effect, 'item') else ttest_mfg_fuels.effect)
    se_diff_mfg_fuels = float(ttest_mfg_fuels.sd.item() if hasattr(ttest_mfg_fuels.sd, 'item') else ttest_mfg_fuels.sd)
    t_diff_mfg_fuels = float(ttest_mfg_fuels.tvalue.item() if hasattr(ttest_mfg_fuels.tvalue, 'item') else ttest_mfg_fuels.tvalue)
    p_diff_mfg_fuels = float(ttest_mfg_fuels.pvalue.item() if hasattr(ttest_mfg_fuels.pvalue, 'item') else ttest_mfg_fuels.pvalue)
    stars_diff_mfg_fuels = '***' if p_diff_mfg_fuels < 0.01 else '**' if p_diff_mfg_fuels < 0.05 else '*' if p_diff_mfg_fuels < 0.1 else ''
    
    print(f"  -> Hệ số LSCI Nông sản (Cơ sở): {c_agri:.3f} (SE = {se_agri:.3f}, p = {format_pval(p_agri)})")
    print(f"  -> Chênh lệch Chế tạo vs Nông sản: {c_diff_mfg_agri:.3f}{stars_diff_mfg_agri} (SE = {se_diff_mfg_agri:.3f}, p = {format_pval(p_diff_mfg_agri)})")
    print(f"  -> Chênh lệch Chế tạo vs Nhiên liệu: {c_diff_mfg_fuels:.3f}{stars_diff_mfg_fuels} (SE = {se_diff_mfg_fuels:.3f}, p = {format_pval(p_diff_mfg_fuels)})")
    
    pooled_metrics = {
        'id': 'R_pooled_product',
        'name': 'Mô hình gộp ngành hàng PPML (Kiểm định trực tiếp H4)',
        'desc': 'Bảng gộp 3 nhóm ngành hàng (N = 405, 9 cụm quốc gia)',
        'n_obs': int(len(df_long)),
        'n_clusters': int(df_long['iso3'].nunique()),
        'pseudo_ll': float(res.llf),
        'agri_baseline': {
            'coef': c_agri, 'se': se_agri, 'pval': p_agri
        },
        'diff_mfg_minus_agri': {
            'coef': c_diff_mfg_agri, 'se': se_diff_mfg_agri, 'tval': t_diff_mfg_agri, 'pval': p_diff_mfg_agri
        },
        'diff_mfg_minus_fuels': {
            'coef': c_diff_mfg_fuels, 'se': se_diff_mfg_fuels, 'tval': t_diff_mfg_fuels, 'pval': p_diff_mfg_fuels
        },
        'diff_fuels_minus_agri': {
            'coef': c_diff_fuels_agri, 'se': se_diff_fuels_agri, 'pval': p_diff_fuels_agri
        }
    }
    
    # Dòng đưa vào bảng bảng kiểm định độ bền
    row_pooled = {
        'Kiểm định độ bền': '11. Chênh lệch Chế tạo vs Nông sản (Pooled)',
        'Mô tả mẫu': 'Kiểm định trực tiếp khác biệt hệ số: Mfg - Agri (HS 28–96 vs HS 01–24)',
        'Hệ số LSCI': f"{c_diff_mfg_agri:.3f}{stars_diff_mfg_agri}",
        'SE LSCI': f"({se_diff_mfg_agri:.3f})",
        'P-value LSCI': format_pval(p_diff_mfg_agri),
        'Hệ số ln(GDP)': f"{float(res.params.get('ln_gdp', 0)):.3f}",
        'SE GDP': f"({float(res.bse.get('ln_gdp', 0)):.3f})",
        'Số quan sát (N)': len(df_long),
        'Số nước': int(df_long['iso3'].nunique()),
        'Pseudo LL': f"{res.llf:.1f}"
    }
    return pooled_metrics, row_pooled

def run_robustness_checks():
    """
    Thực hiện hệ thống kiểm định độ bền và độ nhạy theo Mục 11.3 của design.md:
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
    11. Kiểm định trực tiếp khác biệt ngành hàng (Pooled Product-Panel PPML)
    12. Kiểm định kỳ vọng/dẫn trước Placebo (LSCI Lead 1)
    
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
            'id': 'R12_placebo',
            'name': '12. Placebo Test (LSCI Lead 1)',
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
        
    # Chạy mô hình gộp ngành hàng kiểm định trực tiếp khác biệt hệ số (H4)
    pooled_metrics, row_pooled = estimate_pooled_product_panel(sample_full)
    structured_robustness['R_pooled_product'] = pooled_metrics
    # Chèn dòng mô hình gộp vào trước Placebo test
    rows.insert(-1, row_pooled)
    
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
