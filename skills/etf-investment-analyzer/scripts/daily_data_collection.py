#!/usr/bin/env python3
"""
Daily Data Collection Script
每日数据采集脚本 - 采集2026年实时数据
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import akshare as ak
except ImportError:
    print("⚠️ AKShare not available, using mock data")
    ak = None


def load_existing_data(filepath: str) -> dict:
    """Load existing 2026 data if available"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_data(data: dict, filepath: str):
    """Save data to file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def fetch_etf_data_akshare(etf_code: str) -> list:
    """Fetch ETF historical data from AKShare"""
    if ak is None:
        return []
    
    try:
        # Format code for AKShare
        if etf_code.startswith('15') or etf_code.startswith('16'):
            symbol = f"{etf_code}.SZ"
        else:
            symbol = f"{etf_code}.SH"
        
        # Fetch data from 2026-01-01 to today
        df = ak.fund_etf_hist_em(
            symbol=etf_code,
            period="daily",
            start_date="20260101",
            end_date=datetime.now().strftime("%Y%m%d"),
            adjust="qfq"
        )
        
        if df is None or df.empty:
            return []
        
        # Convert to our format
        records = []
        for _, row in df.iterrows():
            records.append({
                'date': row['日期'],
                'price': float(row['收盘']),
                'open': float(row['开盘']),
                'high': float(row['最高']),
                'low': float(row['最低']),
                'volume': int(row['成交量'])
            })
        
        return records
    except Exception as e:
        print(f"   ⚠️ Error fetching {etf_code}: {e}")
        return []


def collect_daily_data():
    """Collect daily data for all tracked ETFs"""
    print("=" * 70)
    print("📊 ETF Daily Data Collection - 2026")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # ETF codes to track
    etf_codes = [
        '510050',  # 上证50
        '510300',  # 沪深300
        '510500',  # 中证500
        '159915',  # 创业板
        '588000',  # 科创50
        '159902',  # 中小100
        '159806',  # 新能源
        '159995',  # 芯片
        '159227',  # 航空航天
    ]
    
    # Load existing 2026 data
    data_2026_path = '/home/ubuntu/.openclaw/workspace-analyzer_agent/etf_price_data_2026.json'
    data_2026 = load_existing_data(data_2026_path)
    
    print(f"\n📁 Existing 2026 data: {len(data_2026)} ETFs")
    
    # Collect data for each ETF
    new_records = 0
    for code in etf_codes:
        print(f"\n🔹 Fetching {code}...", end=' ')
        
        records = fetch_etf_data_akshare(code)
        
        if records:
            # Merge with existing data
            if code in data_2026:
                existing_dates = {r['date'] for r in data_2026[code]}
                new_records_list = [r for r in records if r['date'] not in existing_dates]
                data_2026[code].extend(new_records_list)
                data_2026[code] = sorted(data_2026[code], key=lambda x: x['date'])
                added = len(new_records_list)
            else:
                data_2026[code] = records
                added = len(records)
            
            new_records += added
            print(f"✅ {len(data_2026[code])} total records (+{added} new)")
        else:
            print("⚠️ No data")
    
    # Save updated data
    save_data(data_2026, data_2026_path)
    
    print(f"\n" + "=" * 70)
    print(f"✅ Data collection complete!")
    print(f"   Total ETFs: {len(data_2026)}")
    print(f"   New records: {new_records}")
    print(f"   Saved to: {data_2026_path}")
    print("=" * 70)
    
    return data_2026


def generate_daily_summary(data_2026: dict):
    """Generate daily summary"""
    summary = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().isoformat(),
        'etfs_tracked': list(data_2026.keys()),
        'total_records': sum(len(records) for records in data_2026.values()),
        'latest_prices': {}
    }
    
    for code, records in data_2026.items():
        if records:
            latest = records[-1]
            summary['latest_prices'][code] = {
                'date': latest['date'],
                'price': latest['price'],
                'volume': latest.get('volume', 0)
            }
    
    # Save summary
    summary_path = f"/home/ubuntu/.openclaw/workspace-analyzer_agent/data/daily/daily_summary_{datetime.now().strftime('%Y-%m-%d')}.json"
    save_data(summary, summary_path)
    
    return summary


def main():
    """Main entry point"""
    print("Starting daily data collection...\n")
    
    # Collect data
    data_2026 = collect_daily_data()
    
    # Generate summary
    summary = generate_daily_summary(data_2026)
    
    print("\n📋 Daily Summary:")
    print(f"   ETFs tracked: {len(summary['etfs_tracked'])}")
    print(f"   Total records: {summary['total_records']}")
    print(f"   Latest prices available: {len(summary['latest_prices'])}")
    
    return data_2026


if __name__ == '__main__':
    main()
