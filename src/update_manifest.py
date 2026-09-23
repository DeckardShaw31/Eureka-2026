import os
import hashlib
import pandas as pd
from datetime import datetime

MANIFEST_PATH = os.path.join('data', 'raw', 'manifest.csv')

RAW_FILES = [
    {
        'source': 'UNCTADstat',
        'dataset': 'LSCI',
        'filepath': os.path.join('data', 'raw', 'unctad', 'US_LSCI.csv'),
        'url': 'https://unctadstat-api.unctad.org/bulkdownload/US.LSCI/10012/US_LSCI',
        'frequency': 'Quarterly (2006Q1 - 2026Q2)',
        'description': 'Liner Shipping Connectivity Index (Average Q1 2023 = 100)'
    },
    {
        'source': 'UNCTADstat',
        'dataset': 'LSBCI',
        'filepath': os.path.join('data', 'raw', 'unctad', 'US_LSBCI.csv'),
        'url': 'https://unctadstat-api.unctad.org/bulkdownload/US.LSBCI/10004/US_LSBCI',
        'frequency': 'Quarterly (2006Q1 - 2026Q1)',
        'description': 'Bilateral Liner Shipping Connectivity Index'
    },
    {
        'source': 'World Bank API',
        'dataset': 'WDI Indicators',
        'filepath': os.path.join('data', 'raw', 'world_bank', 'world_bank_indicators_2010_2025.csv'),
        'url': 'http://api.worldbank.org/v2/country/.../indicator/...',
        'frequency': 'Annual (2010 - 2025)',
        'description': 'GDP, Population, Net FDI (% GDP), Official FX, REER, Merchandise Exports'
    },
    {
        'source': 'ASEANstats Data Portal',
        'dataset': 'IMTS Trade in Goods (HS2)',
        'filepath': os.path.join('data', 'raw', 'aseanstats', 'asean_imts_annual_hs2.csv'),
        'url': 'https://data.aseanstats.org/trade-annually',
        'frequency': 'Annual (2003 - 2025)',
        'description': 'ASEAN International Merchandise Trade Statistics, Annually, HS 2-Digit Chapters 01-97, World Partner'
    },
    {
        'source': 'ASEANstats Data Portal',
        'dataset': 'IMTS Trade in Goods (HS4)',
        'filepath': os.path.join('data', 'raw', 'aseanstats', 'asean_imts_annual_hs4.csv'),
        'url': 'https://data.aseanstats.org/trade-annually',
        'frequency': 'Annual (2003 - 2025)',
        'description': 'ASEAN International Merchandise Trade Statistics, Annually, HS 4-Digit, World Partner'
    },
    {
        'source': 'ASEANstats Data Portal',
        'dataset': 'IMTS Trade in Goods (HS6)',
        'filepath': os.path.join('data', 'raw', 'aseanstats', 'asean_imts_annual_hs6.csv'),
        'url': 'https://data.aseanstats.org/trade-annually',
        'frequency': 'Annual (2003 - 2025)',
        'description': 'ASEAN International Merchandise Trade Statistics, Annually, HS 6-Digit, World Partner'
    },
    {
        'source': 'ASEANstats Data Portal',
        'dataset': 'IMTS Trade in Goods (HS8 AHTN)',
        'filepath': os.path.join('data', 'raw', 'aseanstats', 'asean_imts_annual_hs8.csv'),
        'url': 'https://data.aseanstats.org/trade-annually',
        'frequency': 'Annual (2003 - 2025)',
        'description': 'ASEAN International Merchandise Trade Statistics, Annually, HS 8-Digit (AHTN), World Partner'
    },
    {
        'source': 'UN Comtrade API',
        'dataset': 'Bilateral Merchandise Exports',
        'filepath': os.path.join('data', 'raw', 'comtrade', 'comtrade_bilateral_2010_2024.csv'),
        'url': 'https://comtradeapi.un.org/public/v1/preview/C/A/HS',
        'frequency': 'Annual (2010 - 2024)',
        'description': 'Bilateral Merchandise Exports from 9 ASEAN economies to 24 major partners'
    }
]

def compute_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def update_manifest():
    records = []
    for item in RAW_FILES:
        fp = item['filepath']
        if os.path.exists(fp):
            stat = os.stat(fp)
            records.append({
                'source': item['source'],
                'dataset': item['dataset'],
                'file_name': os.path.basename(fp),
                'relative_path': fp.replace('\\', '/'),
                'size_bytes': stat.st_size,
                'sha256': compute_sha256(fp),
                'download_url': item['url'],
                'frequency': item['frequency'],
                'description': item['description'],
                'last_updated': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    df = pd.DataFrame(records)
    df.to_csv(MANIFEST_PATH, index=False)
    print(f"Manifest written to {MANIFEST_PATH} with {len(df)} datasets.")
    print(df[['dataset', 'file_name', 'size_bytes', 'sha256']])

if __name__ == '__main__':
    update_manifest()
