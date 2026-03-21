#!/usr/bin/env python3
"""
ETF批量监控脚本
支持A股所有ETF的批量监控
"""

import json
import sys
import time
from datetime import datetime
import subprocess
import os

def get_stock_data(stock_code):
    """获取股票数据"""
    # 添加前缀
    if stock_code.startswith('6'):
        code = f"sh{stock_code}"
    elif stock_code.startswith('0') or stock_code.startswith('3'):
        code = f"sz{stock_code}"
    else:
        code = stock_code
    
    try:
        # 使用腾讯财经API
        cmd = f'curl -s "https://qt.gtimg.cn/q={code}" | iconv -f gbk -t utf-8 2>/dev/null'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            data = result.stdout.strip()
            if 'v_' in data and '~' in data:
                # 解析数据格式: v_sh000001="1~上证指数~000001~4133.43~4123.14~..."
                parts = data.split('=')[1].strip('"').split('~')
                if len(parts) > 30:
                    return {
                        'name': parts[1],
                        'code': stock_code,
                        'price': parts[3],
                        'prev_close': parts[4],
                        'open': parts[5],
                        'high': parts[33],
                        'low': parts[34],
                        'change': parts[31],
                        'change_percent': parts[32],
                        'volume': parts[6],
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
    except Exception as e:
        pass
    
    return None

def check_alert_rules(stock_data, rules):
    """检查提醒规则"""
    alerts = []
    
    if not stock_data:
        return alerts
    
    try:
        current_price = float(stock_data['price'])
        change_percent = float(stock_data['change_percent'])
        
        # 涨跌幅提醒
        if 'change_threshold' in rules and abs(change_percent) > rules['change_threshold']:
            direction = "📈上涨" if change_percent > 0 else "📉下跌"
            alerts.append(f"{direction}: {stock_data['name']} ({stock_data['code']}) {change_percent:+.2f}%")
        
    except (ValueError, KeyError) as e:
        pass
    
    return alerts

def load_etf_list():
    """加载ETF列表"""
    workspace = os.path.dirname(os.path.abspath(__file__))
    etf_file = os.path.join(workspace, 'etf_list.json')
    
    try:
        with open(etf_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载ETF列表失败: {e}")
        return []

def monitor_etfs(batch_size=50, alert_threshold=3.0):
    """批量监控ETF"""
    etf_list = load_etf_list()
    
    if not etf_list:
        print("❌ 无法加载ETF列表")
        return
    
    print(f"📊 A股ETF批量监控")
    print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 总数: {len(etf_list)} 只ETF")
    print(f"⚡ 阈值: 涨跌幅超过 ±{alert_threshold}% 时提醒")
    print("=" * 60)
    
    all_alerts = []
    success_count = 0
    fail_count = 0
    
    # 分批处理
    total = len(etf_list)
    for i in range(0, min(total, batch_size)):
        etf = etf_list[i]
        code = etf['code']
        name = etf['name']
        
        data = get_stock_data(code)
        if data:
            success_count += 1
            try:
                change_percent = float(data['change_percent'])
                price = float(data['price'])
                
                # 只显示涨跌幅超过阈值的
                if abs(change_percent) >= alert_threshold:
                    direction = "📈" if change_percent > 0 else "📉"
                    print(f"{direction} {name} ({code}): {price:.3f} ({change_percent:+.2f}%)")
                    
                    # 检查提醒
                    alerts = check_alert_rules(data, {'change_threshold': alert_threshold})
                    all_alerts.extend(alerts)
            except:
                pass
        else:
            fail_count += 1
        
        # 每10只显示进度
        if (i + 1) % 10 == 0:
            print(f"  ... 已处理 {i+1}/{min(total, batch_size)}")
        
        # 添加小延迟避免请求过快
        time.sleep(0.2)
    
    print("=" * 60)
    print(f"✅ 成功: {success_count} | ❌ 失败: {fail_count}")
    
    # 输出提醒汇总
    if all_alerts:
        print(f"\n🔔 异动提醒 ({len(all_alerts)}条):")
        for alert in all_alerts[:20]:  # 最多显示20条
            print(f"  • {alert}")
        if len(all_alerts) > 20:
            print(f"  ... 还有 {len(all_alerts)-20} 条提醒")
    else:
        print("\n✅ 暂无超过阈值的异动")
    
    print(f"\n监控完成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def monitor_all_etfs(alert_threshold=3.0):
    """监控所有ETF，只返回异动列表"""
    etf_list = load_etf_list()
    
    if not etf_list:
        return []
    
    alerts = []
    print(f"正在扫描 {len(etf_list)} 只ETF...")
    
    for i, etf in enumerate(etf_list):
        code = etf['code']
        name = etf['name']
        
        data = get_stock_data(code)
        if data:
            try:
                change_percent = float(data['change_percent'])
                if abs(change_percent) >= alert_threshold:
                    direction = "📈" if change_percent > 0 else "📉"
                    alerts.append({
                        'name': name,
                        'code': code,
                        'price': data['price'],
                        'change_percent': change_percent,
                        'alert': f"{direction} {name} ({code}): {change_percent:+.2f}%"
                    })
            except:
                pass
        
        # 显示进度
        if (i + 1) % 100 == 0:
            print(f"  已扫描 {i+1}/{len(etf_list)}...")
        
        time.sleep(0.15)
    
    return alerts

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='A股ETF批量监控')
    parser.add_argument('--batch', '-b', type=int, default=50, help='每批监控数量 (默认: 50)')
    parser.add_argument('--threshold', '-t', type=float, default=3.0, help='涨跌幅阈值 %% (默认: 3.0)')
    parser.add_argument('--all', '-a', action='store_true', help='监控所有ETF')
    
    args = parser.parse_args()
    
    if args.all:
        alerts = monitor_all_etfs(alert_threshold=args.threshold)
        print(f"\n{'='*60}")
        print(f"📊 全市场扫描完成，发现 {len(alerts)} 只异动ETF:")
        print(f"{'='*60}")
        
        # 按涨跌幅排序
        alerts.sort(key=lambda x: abs(x['change_percent']), reverse=True)
        
        for item in alerts[:30]:  # 显示前30
            print(f"  {item['alert']}")
        
        if len(alerts) > 30:
            print(f"  ... 还有 {len(alerts)-30} 只")
    else:
        monitor_etfs(batch_size=args.batch, alert_threshold=args.threshold)

if __name__ == "__main__":
    main()
