import os
import json
import time
import requests
import pandas as pd
import hashlib

# 9 ASEAN coastal countries + Lao PDR + Timor-Leste
ASEAN_ISO3_LIST = ['BRN', 'KHM', 'IDN', 'MYS', 'MMR', 'PHL', 'SGP', 'THA', 'VNM', 'LAO', 'TLS']
COUNTRY_PARAM = ';'.join(ASEAN_ISO3_LIST)

INDICATORS = {
    'gdp_usd': {
        'code': 'NY.GDP.MKTP.CD',
        'desc': 'GDP (current US$)'
    },
    'population': {
        'code': 'SP.POP.TOTL',
        'desc': 'Population, total'
    },
    'fdi_gdp': {
        'code': 'BX.KLT.DINV.WD.GD.ZS',
        'desc': 'Foreign direct investment, net inflows (% of GDP)'
    },
    'official_fx': {
        'code': 'PA.NUS.FCRF',
        'desc': 'Official exchange rate (LCU per US$, period average)'
    },
    'reer': {
        'code': 'PX.REX.REER',
        'desc': 'Real effective exchange rate index (2010 = 100)'
    },
    'merch_export_wb': {
        'code': 'TX.VAL.MRCH.CD.WT',
        'desc': 'Merchandise exports (current US$)'
    }
}

RAW_WB_DIR = os.path.join('data', 'raw', 'world_bank')
os.makedirs(RAW_WB_DIR, exist_ok=True)

def compute_sha256(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def fetch_indicator(var_name, info, start_year=2010, end_year=2025, retries=3):
    ind_code = info['code']
    url = f"http://api.worldbank.org/v2/country/{COUNTRY_PARAM}/indicator/{ind_code}?date={start_year}:{end_year}&format=json&per_page=500"
    print(f"Fetching {var_name} ({ind_code})...", flush=True)
    
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 1 and data[1]:
                    records = data[1]
                    raw_file = os.path.join(RAW_WB_DIR, f"{var_name}_{ind_code}.json")
                    with open(raw_file, 'w', encoding='utf-8') as f:
                        json.dump(records, f, ensure_ascii=False, indent=2)
                    print(f"  -> Saved {len(records)} records to {raw_file}", flush=True)
                    return records
                else:
                    print(f"  -> No records found for {ind_code}", flush=True)
                    return []
            else:
                print(f"  -> Attempt {attempt}: HTTP {resp.status_code}", flush=True)
        except Exception as e:
            print(f"  -> Attempt {attempt} failed: {e}", flush=True)
        time.sleep(1)
        
    raise RuntimeError(f"Failed to fetch {var_name} ({ind_code}) after {retries} retries.")

def main():
    all_rows = []
    
    for var_name, info in INDICATORS.items():
        records = fetch_indicator(var_name, info)
        for rec in records:
            all_rows.append({
                'iso3': rec['countryiso3code'],
                'country': rec['country']['value'],
                'year': int(rec['date']),
                'indicator': var_name,
                'indicator_code': info['code'],
                'value': rec['value']
            })
            
    df = pd.DataFrame(all_rows)
    if not df.empty:
        pivot = df.pivot_table(index=['iso3', 'country', 'year'], columns='indicator', values='value').reset_index()
        csv_path = os.path.join(RAW_WB_DIR, 'world_bank_indicators_2010_2025.csv')
        pivot.to_csv(csv_path, index=False)
        sha256 = compute_sha256(csv_path)
        print(f"\n[DONE] Saved consolidated World Bank indicators to {csv_path}")
        print(f"SHA-256: {sha256}")
        
        core_sample = pivot[(pivot['year'] <= 2024) & (pivot['iso3'].isin(['BRN', 'KHM', 'IDN', 'MYS', 'MMR', 'PHL', 'SGP', 'THA', 'VNM']))]
        print(f"\n--- Coverage for Core Sample (9 ASEAN countries, 2010-2024, max 135) ---")
        print(core_sample[list(INDICATORS.keys())].notnull().sum())
        
        y2025 = pivot[(pivot['year'] == 2025) & (pivot['iso3'].isin(['BRN', 'KHM', 'IDN', 'MYS', 'MMR', 'PHL', 'SGP', 'THA', 'VNM']))]
        print(f"\n--- Coverage for Year 2025 (9 ASEAN countries, max 9) ---")
        print(y2025[list(INDICATORS.keys())].notnull().sum())

if __name__ == '__main__':
    main()
