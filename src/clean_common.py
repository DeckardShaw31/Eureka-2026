import os
import sys
import hashlib
import pandas as pd
import numpy as np

# Thiết lập UTF-8 cho môi trường console Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


# Đường dẫn cấu hình
CONFIG_DIR = 'config'
COUNTRIES_FILE = os.path.join(CONFIG_DIR, 'countries.csv')
PARTNERS_FILE = os.path.join(CONFIG_DIR, 'partners.csv')

# Danh sách 9 nước ASEAN ven biển làm mẫu chính
CORE_ASEAN_COASTAL = ['BRN', 'KHM', 'IDN', 'MYS', 'MMR', 'PHL', 'SGP', 'THA', 'VNM']

# Ánh xạ chuẩn hóa tên gọi sang ISO3
NAME_TO_ISO3 = {
    # 9 nước ASEAN ven biển
    'brunei darussalam': 'BRN',
    'brunei': 'BRN',
    'cambodia': 'KHM',
    'indonesia': 'IDN',
    'malaysia': 'MYS',
    'myanmar': 'MMR',
    'burma': 'MMR',
    'philippines': 'PHL',
    'singapore': 'SGP',
    'thailand': 'THA',
    'viet nam': 'VNM',
    'vietnam': 'VNM',
    # Các thành viên ASEAN khác
    'lao pdr': 'LAO',
    'laos': 'LAO',
    'timor-leste': 'TLS',
    'east timor': 'TLS',
    # 15 đối tác thương mại lớn
    'united states': 'USA',
    'united states of america': 'USA',
    'china': 'CHN',
    'japan': 'JPN',
    'republic of korea': 'KOR',
    'korea, rep.': 'KOR',
    'south korea': 'KOR',
    'hong kong': 'HKG',
    'china, hong kong sar': 'HKG',
    'germany': 'DEU',
    'netherlands': 'NLD',
    'netherlands (kingdom of the)': 'NLD',
    'united kingdom': 'GBR',
    'australia': 'AUS',
    'india': 'IND',
    'taiwan': 'TWN',
    'other asia nes (taiwan)': 'TWN',
    'china, taiwan province of': 'TWN',
    'france': 'FRA',
    'italy': 'ITA',
    'canada': 'CAN',
    'united arab emirates': 'ARE'
}

def load_countries_config():
    """Tải danh mục quốc gia nghiên cứu từ config/countries.csv"""
    if os.path.exists(COUNTRIES_FILE):
        return pd.read_csv(COUNTRIES_FILE)
    return pd.DataFrame()

def load_partners_config():
    """Tải danh mục đối tác thương mại từ config/partners.csv"""
    if os.path.exists(PARTNERS_FILE):
        return pd.read_csv(PARTNERS_FILE)
    return pd.DataFrame()

def standardize_iso3(country_name):
    """Chuẩn hóa tên quốc gia bất kỳ về mã chuẩn ISO3 (3 ký tự in hoa)"""
    if not isinstance(country_name, str):
        return None
    cleaned = country_name.strip().lower()
    return NAME_TO_ISO3.get(cleaned, None)

def compute_file_sha256(filepath):
    """Tính mã băm SHA-256 của tệp để kiểm tra tính toàn vẹn"""
    if not os.path.exists(filepath):
        return None
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_project_config():
    """Tải cấu hình dự án từ config/project_config.json làm nguồn chuẩn duy nhất"""
    cfg_path = os.path.join(CONFIG_DIR, 'project_config.json')
    if os.path.exists(cfg_path):
        import json
        with open(cfg_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'start_year': 2010,
        'end_year': 2025,
        'estimation_end_year': 2024,
        'descriptive_end_year': 2025,
        'min_quarters_per_year': 3,
        'min_2025_coverage': 0.8
    }

def format_pval(pval):
    """Định dạng p-value chuẩn học thuật (không bao giờ in p = 0.0000)"""
    if pd.isnull(pval):
        return ""
    if pval < 0.001:
        return "< 0.001"
    return f"{pval:.3f}"

def format_coef_se(coef, se, pval):
    """Định dạng hệ số kèm dấu sao ý nghĩa thống kê và sai số chuẩn"""
    if pd.isnull(coef):
        return ""
    stars = ''
    if pval < 0.01:
        stars = '***'
    elif pval < 0.05:
        stars = '**'
    elif pval < 0.1:
        stars = '*'
    se_str = f"({se:.3f})" if not pd.isnull(se) else ""
    return f"{coef:.3f}{stars}\n{se_str}".strip()

def ensure_directories():
    """Đảm bảo các thư mục cần thiết trong dự án tồn tại"""
    dirs = [
        os.path.join('data', 'raw'),
        os.path.join('data', 'interim'),
        os.path.join('data', 'processed'),
        os.path.join('outputs', 'tables'),
        os.path.join('outputs', 'figures'),
        os.path.join('outputs', 'diagnostics'),
        os.path.join('outputs', 'logs')
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

