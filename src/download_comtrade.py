import os
import json
import time
import requests
import pandas as pd
import hashlib

CONFIG_PARTNERS = os.path.join('config', 'partners.csv')
CONFIG_COUNTRIES = os.path.join('config', 'countries.csv')
RAW_COMTRADE_DIR = os.path.join('data', 'raw', 'comtrade')
CACHE_DIR = os.path.join(RAW_COMTRADE_DIR, 'cache')

os.makedirs(CACHE_DIR, exist_ok=True)

REPORTER_CODES = {
    'BRN': 96,
    'KHM': 116,
    'IDN': 360,
    'MYS': 458,
    'MMR': 104,
    'PHL': 608,
    'SGP': 702,
    'THA': 764,
    'VNM': 704
}

def load_partners():
    df_p = pd.read_csv(CONFIG_PARTNERS)
    # Map UN code to ISO3
    code_to_iso3 = dict(zip(df_p['un_code'].astype(str), df_p['iso3']))
    partner_codes_str = ','.join(df_p['un_code'].astype(str).tolist())
    return code_to_iso3, partner_codes_str

def fetch_comtrade_year(reporter_iso3, reporter_code, partner_codes_str, year, retries=3):
    cache_file = os.path.join(CACHE_DIR, f"{reporter_iso3}_{year}.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass

    url = 'https://comtradeapi.un.org/public/v1/preview/C/A/HS'
    params = {
        'reporterCode': reporter_code,
        'partnerCode': partner_codes_str,
        'period': str(year),
        'flowCode': 'X',
        'cmdCode': 'TOTAL',
        'partner2Code': '0',
        'customsCode': 'C00'
    }

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, timeout=25, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                data = r.json()
                items = data.get('data', [])
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(items, f, ensure_ascii=False)
                return items
            elif r.status_code == 429:
                print(f"  Rate limit hit for {reporter_iso3} {year}, backing off...", flush=True)
                time.sleep(5 * attempt)
            else:
                print(f"  Status {r.status_code} for {reporter_iso3} {year}", flush=True)
        except Exception as e:
            print(f"  Attempt {attempt} failed for {reporter_iso3} {year}: {e}", flush=True)
        time.sleep(2)
        
    return []

def main(start_year=2010, end_year=2024):
    code_to_iso3, partner_codes_str = load_partners()
    print(f"Loaded {len(code_to_iso3)} partner countries.")
    
    all_records = []
    total_queries = len(REPORTER_CODES) * (end_year - start_year + 1)
    q_count = 0

    print(f"Fetching bilateral trade data from UN Comtrade API ({start_year} - {end_year})...")
    for reporter_iso3, rep_code in REPORTER_CODES.items():
        print(f"\n[{reporter_iso3}] Fetching years {start_year}-{end_year}...", flush=True)
        for year in range(start_year, end_year + 1):
            q_count += 1
            items = fetch_comtrade_year(reporter_iso3, rep_code, partner_codes_str, year)
            if items:
                df_temp = pd.DataFrame(items)
                if not df_temp.empty and 'primaryValue' in df_temp.columns:
                    # Filter for max value per partner to get grand total (avoid sub-customs splits)
                    df_agg = df_temp.groupby('partnerCode')['primaryValue'].max().reset_index()
                    for _, row in df_agg.iterrows():
                        p_code = str(int(row['partnerCode']))
                        p_iso3 = code_to_iso3.get(p_code)
                        if p_iso3 and p_iso3 != reporter_iso3:
                            all_records.append({
                                'exporter_iso3': reporter_iso3,
                                'importer_iso3': p_iso3,
                                'year': year,
                                'trade_usd': float(row['primaryValue']),
                                'source_flag': 'UNComtrade'
                            })
            time.sleep(0.5)

    df_out = pd.DataFrame(all_records)
    out_csv = os.path.join(RAW_COMTRADE_DIR, f'comtrade_bilateral_{start_year}_{end_year}.csv')
    df_out.to_csv(out_csv, index=False)
    
    print(f"\n[SUCCESS] Saved {len(df_out)} bilateral trade records to {out_csv}")
    if not df_out.empty:
        print(f"Exporters: {df_out['exporter_iso3'].nunique()}")
        print(f"Importers: {df_out['importer_iso3'].nunique()}")
        print(f"Years: {df_out['year'].min()} - {df_out['year'].max()}")
        print("\nSample records:")
        print(df_out.head(5))

if __name__ == '__main__':
    main()
