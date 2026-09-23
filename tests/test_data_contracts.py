import os
import pytest
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join('data', 'processed')
COUNTRY_FILE = os.path.join(PROCESSED_DIR, 'panel_country_year.csv')
BILATERAL_FILE = os.path.join(PROCESSED_DIR, 'panel_bilateral_year.csv')

@pytest.fixture(scope="module")
def country_df():
    assert os.path.exists(COUNTRY_FILE), f"Tệp {COUNTRY_FILE} không tồn tại!"
    return pd.read_csv(COUNTRY_FILE)

@pytest.fixture(scope="module")
def bilateral_df():
    assert os.path.exists(BILATERAL_FILE), f"Tệp {BILATERAL_FILE} không tồn tại!"
    return pd.read_csv(BILATERAL_FILE)

def test_country_panel_dimensions_and_keys(country_df):
    """Kiểm tra kích thước và tính duy nhất của khóa (iso3, year)"""
    assert len(country_df) == 144, f"Mong đợi 144 quan sát (9 nước x 16 năm), thực tế: {len(country_df)}"
    assert country_df['iso3'].nunique() == 9, "Mẫu phải chứa chính xác 9 nước ASEAN ven biển"
    assert country_df.duplicated(subset=['iso3', 'year']).sum() == 0, "Trùng khóa (iso3, year)"

def test_country_panel_core_variables_completeness(country_df):
    """Kiểm tra tính không khuyết của các biến cơ sở (M1, M2) cho 2010-2024"""
    sample_10_24 = country_df[country_df['year'] <= 2024]
    core_cols = ['export_usd', 'lsci', 'gdp_usd', 'population', 'ln_export', 'ln_lsci', 'ln_gdp', 'ln_population']
    for col in core_cols:
        assert sample_10_24[col].notnull().all(), f"Biến {col} bị khuyết trong mẫu 2010-2024!"

def test_country_panel_values_validity(country_df):
    """Kiểm tra miền giá trị biến quốc gia không âm"""
    assert (country_df['export_usd'] > 0).all()
    assert (country_df['lsci'] > 0).all()
    assert (country_df['gdp_usd'] > 0).all()
    assert (country_df['population'] > 0).all()

def test_bilateral_panel_dimensions_and_keys(bilateral_df):
    """Kiểm tra kích thước và tính duy nhất của khóa song phương"""
    assert len(bilateral_df) == 3240, f"Mong đợi 3240 dòng (9 x 24 x 15), thực tế: {len(bilateral_df)}"
    assert bilateral_df.duplicated(subset=['exporter_iso3', 'importer_iso3', 'year', 'product_group']).sum() == 0

def test_bilateral_trade_zero_preservation(bilateral_df):
    """Kiểm tra nguyên tắc PPML: Bảo toàn các quan sát thương mại bằng 0 được xác nhận (zero_trade_confirmed)"""
    reported_df = bilateral_df[bilateral_df['reporter_year_complete'] == 1]
    assert (reported_df['trade_usd'] >= 0).all()
    zero_trades = (reported_df['trade_usd'] == 0).sum()
    assert zero_trades > 0, "Bảng song phương phải bảo toàn các quan sát thương mại bằng 0 cho các năm có báo cáo!"
    assert (bilateral_df['zero_trade_confirmed'] == 1).sum() == zero_trades

def test_vietnam_2024_unreported_not_zero(bilateral_df):
    """Kiểm tra Việt Nam 2024: chưa báo cáo Comtrade thì để NaN, không được điền số 0 giả"""
    vnm_2024 = bilateral_df[(bilateral_df['exporter_iso3'] == 'VNM') & (bilateral_df['year'] == 2024)]
    assert len(vnm_2024) == 24
    assert vnm_2024['trade_usd'].isnull().all(), "Việt Nam 2024 không được điền số 0 giả!"
    assert (vnm_2024['reporter_year_complete'] == 0).all()

def test_bilateral_lsbci_validity(bilateral_df):
    """Kiểm tra chỉ số LSBCI không âm khi được quan sát"""
    valid_lsbci = bilateral_df['lsbci'].dropna()
    assert len(valid_lsbci) >= 3000, "LSBCI bị thiếu quá nhiều quan sát!"
    assert (valid_lsbci >= 0).all()

