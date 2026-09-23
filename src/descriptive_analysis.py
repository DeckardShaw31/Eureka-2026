import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.outliers_influence import variance_inflation_factor
from clean_common import ensure_directories

# Thiết lập phong cách đồ thị học thuật chuẩn
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#E0E0E0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

PROCESSED_DIR = os.path.join('data', 'processed')
TABLES_DIR = os.path.join('outputs', 'tables')
FIGURES_DIR = os.path.join('outputs', 'figures')

def compute_descriptive_stats(df_country, df_bilateral):
    """Tính bảng thống kê mô tả cho dữ liệu quốc gia và dữ liệu song phương (2010-2024)"""
    print("[DESCRIPTIVE] Tính toán bảng thống kê mô tả...")
    c_sample = df_country[df_country['year'] <= 2024].copy()
    b_sample = df_bilateral[df_bilateral['year'] <= 2024].copy()
    
    # Biến đổi đơn vị để bảng số liệu dễ đọc trong bài báo
    stats_data = [
        {'Variable': 'Tổng xuất khẩu (tỷ USD)', 'Series': c_sample['export_usd'] / 1e9},
        {'Variable': 'Xuất khẩu Nông-Thủy sản (tỷ USD)', 'Series': c_sample['export_usd_agri'] / 1e9},
        {'Variable': 'Xuất khẩu Chế biến-Chế tạo (tỷ USD)', 'Series': c_sample['export_usd_mfg'] / 1e9},
        {'Variable': 'Chỉ số LSCI', 'Series': c_sample['lsci']},
        {'Variable': 'GDP hiện hành (tỷ USD)', 'Series': c_sample['gdp_usd'] / 1e9},
        {'Variable': 'Dân số (triệu người)', 'Series': c_sample['population'] / 1e6},
        {'Variable': 'FDI ròng (% GDP)', 'Series': c_sample['fdi_gdp']},
        {'Variable': 'ln(Tổng xuất khẩu)', 'Series': c_sample['ln_export']},
        {'Variable': 'ln(LSCI)', 'Series': c_sample['ln_lsci']},
        {'Variable': 'ln(GDP)', 'Series': c_sample['ln_gdp']},
        {'Variable': 'ln(Dân số)', 'Series': c_sample['ln_population']},
        {'Variable': 'Xuất khẩu song phương (triệu USD)', 'Series': b_sample['trade_usd'] / 1e6},
        {'Variable': 'Chỉ số LSBCI song phương', 'Series': b_sample['lsbci'].dropna()},
        {'Variable': 'ln(LSBCI)', 'Series': b_sample['ln_lsbci'].dropna()}
    ]
    
    records = []
    for item in stats_data:
        s = item['Series'].dropna()
        records.append({
            'Biến số': item['Variable'],
            'N': len(s),
            'Mean': round(s.mean(), 3),
            'Std. Dev.': round(s.std(), 3),
            'Min': round(s.min(), 3),
            'P25': round(s.quantile(0.25), 3),
            'Median': round(s.median(), 3),
            'P75': round(s.quantile(0.75), 3),
            'Max': round(s.max(), 3)
        })
        
    df_desc = pd.DataFrame(records)
    csv_file = os.path.join(TABLES_DIR, 'table_descriptive_stats.csv')
    tex_file = os.path.join(TABLES_DIR, 'table_descriptive_stats.tex')
    df_desc.to_csv(csv_file, index=False)
    
    # Xuất LaTeX
    df_desc.to_latex(tex_file, index=False, caption='Thống kê mô tả các biến trong mô hình (2010--2024)', label='tab:desc_stats')
    print(f"  ✓ Đã lưu bảng thống kê mô tả: {csv_file} và {tex_file}")
    return df_desc

def compute_correlation_and_vif(df_country):
    """Tính ma trận tương quan và kiểm tra hệ số phóng đại phương sai (VIF)"""
    print("[DESCRIPTIVE] Tính ma trận tương quan và kiểm định đa cộng tuyến (VIF)...")
    c_sample = df_country[df_country['year'] <= 2024].dropna(subset=['ln_lsci', 'ln_gdp', 'ln_population', 'fdi_gdp']).copy()
    
    vars_list = ['ln_lsci', 'ln_gdp', 'ln_population', 'fdi_gdp']
    corr_matrix = c_sample[vars_list].corr().round(3)
    
    # Tính VIF
    X = c_sample[vars_list]
    vif_data = []
    for i, col in enumerate(vars_list):
        v = variance_inflation_factor(X.values, i)
        vif_data.append(round(v, 2))
    
    corr_matrix['VIF'] = vif_data
    csv_file = os.path.join(TABLES_DIR, 'table_correlation_vif.csv')
    tex_file = os.path.join(TABLES_DIR, 'table_correlation_vif.tex')
    corr_matrix.to_csv(csv_file)
    corr_matrix.to_latex(tex_file, caption='Ma trận tương quan và hệ số phóng đại phương sai (VIF)', label='tab:corr_vif')
    print(f"  ✓ Đã lưu ma trận tương quan và VIF: {csv_file}")
    return corr_matrix

def generate_visualizations(df_country, df_bilateral):
    """Tạo bộ 5 hình trực quan hóa chất lượng cao theo Mục 12 của design.md"""
    print("[VISUALIZATION] Đang xuất 5 biểu đồ chất lượng cao...")
    c_sample = df_country[df_country['year'] <= 2024].copy()
    
    # Hình 1: LSCI trung bình theo quốc gia
    plt.figure(figsize=(9, 5), dpi=300)
    avg_lsci = c_sample.groupby('country')['lsci'].agg(['mean', 'std']).sort_values('mean', ascending=False)
    colors = ['#1f77b4' if c in ['Singapore', 'Malaysia', 'Viet Nam', 'Thailand', 'Indonesia', 'Philippines'] else '#2ca02c' for c in avg_lsci.index]
    bars = plt.bar(avg_lsci.index, avg_lsci['mean'], yerr=avg_lsci['std'], capsize=4, color=colors, alpha=0.85, edgecolor='#333333')
    plt.title('Chỉ số kết nối vận tải biển (LSCI) trung bình của các nước ASEAN (2010–2024)', fontsize=12, pad=12, fontweight='bold')
    plt.ylabel('Điểm LSCI trung bình', fontsize=11)
    plt.xticks(rotation=25, ha='right', fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    for bar in bars:
        h = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., h + 15, f'{h:.1f}', ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    f1_path = os.path.join(FIGURES_DIR, 'fig1_lsci_ranking.png')
    plt.savefig(f1_path)
    plt.close()
    print(f"  ✓ Hình 1: {f1_path}")
    
    # Hình 2: Xu hướng LSCI và Xuất khẩu theo thời gian
    plt.figure(figsize=(10, 5.5), dpi=300)
    # Lấy top 4 nước tiêu biểu: SGP, MYS, VNM, IDN
    sample_countries = ['Singapore', 'Viet Nam', 'Malaysia', 'Indonesia']
    palette = {'Singapore': '#d62728', 'Viet Nam': '#1f77b4', 'Malaysia': '#2ca02c', 'Indonesia': '#ff7f0e'}
    for c in sample_countries:
        sub = c_sample[c_sample['country'] == c].sort_values('year')
        plt.plot(sub['year'], sub['lsci'], marker='o', label=c, color=palette[c], linewidth=2.2)
    plt.title('Xu hướng phát triển chỉ số kết nối vận tải biển LSCI (2010–2024)', fontsize=12, pad=12, fontweight='bold')
    plt.xlabel('Năm', fontsize=11)
    plt.ylabel('Chỉ số LSCI (Q1 2023 = 100)', fontsize=11)
    plt.legend(title='Quốc gia', frameon=True)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    f2_path = os.path.join(FIGURES_DIR, 'fig2_lsci_export_trends.png')
    plt.savefig(f2_path)
    plt.close()
    print(f"  ✓ Hình 2: {f2_path}")
    
    # Hình 3: Scatter plot ln(LSCI) và ln(Export) theo nhóm ASEAN-6 và CLMV
    plt.figure(figsize=(9, 6), dpi=300)
    sns.scatterplot(
        data=c_sample, x='ln_lsci', y='ln_export', hue='country', style='clmv',
        s=85, alpha=0.85, palette='tab10'
    )
    # Thêm đường hồi quy tổng quát
    sns.regplot(
        data=c_sample, x='ln_lsci', y='ln_export', scatter=False,
        color='#444444', line_kws={'linestyle': '--', 'linewidth': 1.8, 'label': 'Đường xu thế chung'}
    )
    plt.title('Tương quan giữa Kết nối vận tải biển ln(LSCI) và Tổng xuất khẩu ln(Export)', fontsize=12, pad=12, fontweight='bold')
    plt.xlabel('ln(LSCI)', fontsize=11)
    plt.ylabel('ln(Tổng xuất khẩu, USD)', fontsize=11)
    plt.legend(bbox_to_anchor=(1.04, 1), loc="upper left", fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    f3_path = os.path.join(FIGURES_DIR, 'fig3_scatter_lsci_export.png')
    plt.savefig(f3_path)
    plt.close()
    print(f"  ✓ Hình 3: {f3_path}")
    
    # Hình 4: So sánh giai đoạn trước, trong và sau COVID-19
    c_sample['period'] = '2010–2019 (Tiền COVID)'
    c_sample.loc[c_sample['year'].isin([2020, 2021]), 'period'] = '2020–2021 (COVID-19)'
    c_sample.loc[c_sample['year'] >= 2022, 'period'] = '2022–2024 (Hậu COVID)'
    
    plt.figure(figsize=(9, 5), dpi=300)
    order_periods = ['2010–2019 (Tiền COVID)', '2020–2021 (COVID-19)', '2022–2024 (Hậu COVID)']
    sns.boxplot(data=c_sample, x='period', y='export_usd_billions', order=order_periods,
                palette=['#a1c9f4', '#ffb3ba', '#baffc9'], showmeans=True,
                meanprops={"marker":"o", "markerfacecolor":"red", "markeredgecolor":"red"})
    plt.title('Kim ngạch xuất khẩu trung bình qua các giai đoạn COVID-19', fontsize=12, pad=12, fontweight='bold')
    plt.xlabel('Giai đoạn', fontsize=11)
    plt.ylabel('Tổng xuất khẩu (tỷ USD)', fontsize=11)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    f4_path = os.path.join(FIGURES_DIR, 'fig4_covid_impact.png')
    plt.savefig(f4_path)
    plt.close()
    print(f"  ✓ Hình 4: {f4_path}")
    
    # Hình 5: Heatmap kết nối hàng hải song phương LSBCI giữa các nước ASEAN và đối tác chính
    plt.figure(figsize=(11, 7), dpi=300)
    b_sample = df_bilateral[df_bilateral['year'] <= 2024]
    pivot_lsbci = b_sample.groupby(['exporter_iso3', 'importer_iso3'])['lsbci'].mean().unstack()
    # Chọn top đối tác chính để hiển thị rõ
    key_partners = ['USA', 'CHN', 'JPN', 'KOR', 'DEU', 'SGP', 'MYS', 'VNM', 'THA', 'IDN', 'GBR', 'AUS', 'IND']
    pivot_sub = pivot_lsbci[[c for c in key_partners if c in pivot_lsbci.columns]]
    
    sns.heatmap(pivot_sub, annot=True, fmt=".2f", cmap='YlGnBu', cbar_kws={'label': 'Chỉ số LSBCI trung bình'})
    plt.title('Ma trận kết nối vận tải biển song phương LSBCI giữa ASEAN và các đối tác chính', fontsize=12, pad=12, fontweight='bold')
    plt.xlabel('Đối tác nhập khẩu', fontsize=11)
    plt.ylabel('Nước xuất khẩu ASEAN', fontsize=11)
    plt.tight_layout()
    f5_path = os.path.join(FIGURES_DIR, 'fig5_lsbci_connectivity_heatmap.png')
    plt.savefig(f5_path)
    plt.close()
    print(f"  ✓ Hình 5: {f5_path}")

def main():
    ensure_directories()
    df_country = pd.read_csv(os.path.join(PROCESSED_DIR, 'panel_country_year.csv'))
    df_bilateral = pd.read_csv(os.path.join(PROCESSED_DIR, 'panel_bilateral_year.csv'))
    
    df_country['export_usd_billions'] = df_country['export_usd'] / 1e9
    
    compute_descriptive_stats(df_country, df_bilateral)
    compute_correlation_and_vif(df_country)
    generate_visualizations(df_country, df_bilateral)
    print("\n[THÀNH CÔNG] Hoàn thành toàn bộ phân tích mô tả và xuất biểu đồ.")

if __name__ == '__main__':
    main()
