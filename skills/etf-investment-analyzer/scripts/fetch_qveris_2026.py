#!/usr/bin/env python3
"""
Fetch 2026 ETF data using QVeris (THS iFinD)
使用QVeris获取2026年真实ETF数据
"""
import json
import subprocess
import os
from datetime import datetime

QVERIS_API_KEY = "sk-PB-WKEjgzidzu6K2T4SpJV-c3jcHbvkfRUDKKJUHbAg"
QVERIS_SCRIPT = "/home/ubuntu/.openclaw/workspace/skills/qveris-official/scripts/qveris_tool.mjs"

# ETF codes to fetch (all 10 holdings)
ETF_CODES = {
    '510050.SH': '上证50ETF',
    '510300.SH': '沪深300ETF',
    '510500.SH': '中证500ETF',
    '159915.SZ': '创业板ETF',
    '588000.SH': '科创50ETF',
    '159902.SZ': '中小100ETF',
    '516160.SH': '新能源ETF',     # 更正：使用516160而非159806
    '159995.SZ': '芯片ETF',
    '159227.SZ': '航空航天ETF',
    '513100.SH': '纳斯达克ETF',  # 纳斯达克ETF (国泰)
    '513500.SH': '标普500ETF',   # 标普500ETF (博时)
}


def run_qveris_call(tool_id: str, discovery_id: str, params: dict) -> dict:
    """Call QVeris tool"""
    env = os.environ.copy()
    env['QVERIS_API_KEY'] = QVERIS_API_KEY
    
    params_str = json.dumps(params)
    
    cmd = [
        'node', QVERIS_SCRIPT,
        'call', tool_id,
        '--discovery-id', discovery_id,
        '--params', params_str
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            timeout=60
        )
        
        # Parse result - extract JSON from output
        output = result.stdout
        
        # Find JSON start
        json_start = output.find('{')
        if json_start >= 0:
            json_str = output[json_start:]
            return json.loads(json_str)
        
        return {'error': 'No JSON in output', 'output': output}
    
    except Exception as e:
        return {'error': str(e)}


def fetch_etf_data_qveris(etf_code: str, start_date: str, end_date: str) -> list:
    """Fetch ETF historical data from QVeris (THS iFinD)"""
    
    # Discovery ID for ths_ifind.history_quotation.v1
    discovery_id = "fd73b242-424f-4ee3-ad7e-849097728e59"
    tool_id = "ths_ifind.history_quotation.v1"
    
    params = {
        "codes": etf_code,
        "startdate": start_date,
        "enddate": end_date,
        "indicators": "close,open,high,low,volume",
        "interval": "1"
    }
    
    result = run_qveris_call(tool_id, discovery_id, params)
    
    if 'error' in result:
        print(f"   Error: {result['error']}")
        return []
    
    if 'data' not in result or not result['data']:
        return []
    
    # Parse data
    records = []
    for item in result['data'][0]:
        records.append({
            'date': item['time'],
            'price': float(item.get('close', 0)),
            'open': float(item.get('open', item.get('close', 0))),
            'high': float(item.get('high', item.get('close', 0))),
            'low': float(item.get('low', item.get('close', 0))),
            'volume': int(item.get('volume', 0))
        })
    
    return records


def load_existing_data(filepath: str) -> dict:
    """Load existing 2026 data"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_data(data: dict, filepath: str):
    """Save data to file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    """Main entry point"""
    print("=" * 70)
    print("📊 Fetching 2026 ETF Data via QVeris (THS iFinD)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Load existing data
    data_path = '/home/ubuntu/.openclaw/workspace-analyzer_agent/etf_price_data_2026.json'
    data_2026 = load_existing_data(data_path)
    
    print(f"\n📁 Existing data: {len(data_2026)} ETFs")
    
    # Date range: 2026-01-01 to today
    start_date = "20260101"
    end_date = datetime.now().strftime("%Y%m%d")
    
    # Fetch data for each ETF
    total_new = 0
    for code, name in ETF_CODES.items():
        print(f"\n🔹 Fetching {name} ({code})...", end=' ')
        
        records = fetch_etf_data_qveris(code, start_date, end_date)
        
        if records:
            # Normalize code (remove .SH/.SZ)
            norm_code = code.replace('.SH', '').replace('.SZ', '')
            
            # Merge with existing
            if norm_code in data_2026:
                existing_dates = {r['date'] for r in data_2026[norm_code]}
                new_records = [r for r in records if r['date'] not in existing_dates]
                data_2026[norm_code].extend(new_records)
                # Sort by date
                data_2026[norm_code] = sorted(data_2026[norm_code], key=lambda x: x['date'])
                added = len(new_records)
            else:
                data_2026[norm_code] = sorted(records, key=lambda x: x['date'])
                added = len(records)
            
            total_new += added
            print(f"✅ {len(data_2026[norm_code])} total (+{added} new), latest: {records[-1]['price']}")
        else:
            print("⚠️ No data")
    
    # Save
    save_data(data_2026, data_path)
    
    print(f"\n" + "=" * 70)
    print(f"✅ Data fetch complete!")
    print(f"   Total ETFs: {len(data_2026)}")
    print(f"   New records: {total_new}")
    print(f"   Saved to: {data_path}")
    print("=" * 70)


if __name__ == '__main__':
    main()
