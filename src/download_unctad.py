import os
import urllib.request
import subprocess
import hashlib
from datetime import datetime

UNCTAD_DATASETS = {
    'lsci': {
        'url': 'https://unctadstat-api.unctad.org/bulkdownload/US.LSCI/10012/US_LSCI',
        'archive_name': 'US_LSCI.csv.7z',
        'csv_name': 'US_LSCI.csv',
        'description': 'Liner Shipping Connectivity Index (Quarterly, 2006Q1 - 2026Q2)'
    },
    'lsbci': {
        'url': 'https://unctadstat-api.unctad.org/bulkdownload/US.LSBCI/10004/US_LSBCI',
        'archive_name': 'US_LSBCI.csv.7z',
        'csv_name': 'US_LSBCI.csv',
        'description': 'Bilateral Liner Shipping Connectivity Index (Quarterly, 2006Q1 - 2026Q1)'
    }
}

RAW_UNCTAD_DIR = os.path.join('data', 'raw', 'unctad')
os.makedirs(RAW_UNCTAD_DIR, exist_ok=True)

def compute_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def download_and_extract(dataset_key):
    info = UNCTAD_DATASETS[dataset_key]
    archive_path = os.path.join(RAW_UNCTAD_DIR, info['archive_name'])
    csv_path = os.path.join(RAW_UNCTAD_DIR, info['csv_name'])
    
    print(f"[{dataset_key.upper()}] Downloading from {info['url']}...")
    req = urllib.request.Request(info['url'], headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req) as resp, open(archive_path, 'wb') as f:
        f.write(resp.read())
    
    archive_size = os.path.getsize(archive_path)
    print(f"[{dataset_key.upper()}] Downloaded {archive_size:,} bytes. Extracting...")
    
    # Extract using system tar
    subprocess.run(['tar', '-xf', archive_path, '-C', RAW_UNCTAD_DIR], check=True)
    
    if os.path.exists(csv_path):
        csv_size = os.path.getsize(csv_path)
        sha256 = compute_sha256(csv_path)
        print(f"[{dataset_key.upper()}] Extracted {info['csv_name']} ({csv_size:,} bytes, SHA-256: {sha256[:16]}...)")
        return {
            'file_name': info['csv_name'],
            'url': info['url'],
            'download_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'size_bytes': csv_size,
            'sha256': sha256,
            'description': info['description']
        }
    else:
        raise FileNotFoundError(f"Failed to find {csv_path} after extraction.")

if __name__ == '__main__':
    for key in UNCTAD_DATASETS:
        download_and_extract(key)
