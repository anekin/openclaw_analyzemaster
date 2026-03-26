#!/usr/bin/env python3
"""
Portfolio-Optimized Strategy Report
持仓股最优策略报告 - 针对10只持仓ETF定制
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/ubuntu/.openclaw/workspace-analyzer_agent/skills/etf-investment-analyzer/scripts')

from enhanced_etf_analyzer import EnhancedETFAnalyzer, EnhancedTradingSimulator
import pandas as pd
import numpy as np


def backtest_all_strategies(prices, code):
    """回测所有策略并返回结果"""
    results = {}
    
    # Buy & Hold
    results['Buy&Hold'] = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
    
    # MA Cross (5/20)
    ma5 = prices.rolling(5).mean()
    ma20 = prices.rolling(20).mean()
    position = 0
    entry = 0
    returns = []
    for i in range(20, len(prices)):
        if ma5.iloc[i] > ma20.iloc[i] and ma5.iloc[i-1] <= ma20.iloc[i-1]:
            if position == 0:
                position = 1
                entry = prices.iloc[i]
        elif ma5.iloc[i] < ma20.iloc[i] and ma5.iloc[i-1] >= ma20.iloc[i-1]:
            if position == 1:
                returns.append((prices.iloc[i] / entry - 1) * 100)
                position = 0
    if position == 1:
        returns.append((prices.iloc[-1] / entry - 1) * 100)
    results['MA5/20'] = sum(returns) if returns else 0
    
    # RSI (14)
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    position = 0
    entry = 0
    returns = []
    for i in range(14, len(prices)):
        if rsi.iloc[i] < 30 and position == 0:
            position = 1
            entry = prices.iloc[i]
        elif rsi.iloc[i] > 70 and position == 1:
            returns.append((prices.iloc[i] / entry - 1) * 100)
            position = 0
    if position == 1:
        returns.append((prices.iloc[-1] / entry - 1) * 100)
    results['RSI14'] = sum(returns) if returns else 0
    
    # Bollinger (20)
    ma20 = prices.rolling(20).mean()
    std20 = prices.rolling(20).std()
    upper = ma20 + 2 * std20
    lower = ma20 - 2 * std20
    position = 0
    entry = 0
    returns = []
    for i in range(20, len(prices)):
        if prices.iloc[i] < lower.iloc[i] and position == 0:
            position = 1
            entry = prices.iloc[i]
        elif prices.iloc[i] > upper.iloc[i] and position == 1:
            returns.append((prices.iloc[i] / entry - 1) * 100)
            position = 0
    if position == 1:
        returns.append((prices.iloc[-1] / entry - 1) * 100)
    results['Boll20'] = sum(returns) if returns else 0
    
    return results


def generate_portfolio_optimized_report():
    """生成持仓股最优策略报告"""
    
    analyzer = EnhancedETFAnalyzer()
    
    lines = [
        "=" * 80,
        f"📊 持仓股最优策略报告 - {datetime.now().strftime('%Y-%m-%d')}",
        f"分析时间: {datetime.now().strftime('%H:%M')}",
        f"数据周期: 2024+2025双年回测数据",
        "=" * 80,
    ]
    
    # 持仓股列表
    holdings = [
        ('510050.SH', '上证50ETF'),
        ('510300.SH', '沪深300ETF'),
        ('159915.SZ', '创业板ETF'),
        ('588000.SH', '科创50ETF'),
        ('513100.SH', '纳斯达克ETF'),
        ('513500.SH', '标普500ETF'),
        ('159806.SZ', '新能源ETF'),
        ('159995.SZ', '芯片ETF'),
        ('159227.SZ', '航空航天ETF'),
        ('159902.SZ', '中小100ETF'),
    ]
    
    # 策略回测对比表
    lines.extend([
        "",
        "🎯 持仓股策略回测对比 (2024-2025累计收益率 %)",
        "-" * 80,
        f"{'ETF名称':<12} {'Buy&Hold':>10} {'MA5/20':>10} {'RSI14':>10} {'Boll20':>10} {'🏆最优策略':<15}",
        "-" * 80,
    ])
    
    best_strategies = {}
    
    for code, name in holdings:
        data = analyzer.get_etf_data(code)
        if data is not None and len(data) > 60:
            prices = data['price']
            results = backtest_all_strategies(prices, code)
            
            # Find best strategy
            best = max(results.items(), key=lambda x: x[1])
            best_strategies[code] = best[0]
            
            lines.append(
                f"{name:<12} "
                f"{results['Buy&Hold']:>+9.2f}% "
                f"{results['MA5/20']:>+9.2f}% "
                f"{results['RSI14']:>+9.2f}% "
                f"{results['Boll20']:>+9.2f}% "
                f"{best[0]:<15}"
            )
    
    lines.append("-" * 80)
    
    # 当前持仓分析
    lines.extend([
        "",
        "📈 当前持仓分析与最优策略应用",
        "-" * 80,
        f"{'ETF':<12} {'现价':>8} {'盈亏':>10} {'当前策略':<16} {'操作建议'}",
        "-" * 80,
    ])
    
    portfolio = analyzer.analyze_portfolio()
    
    for h in portfolio['holdings']:
        if 'error' not in h:
            name = h.get('name', h['code'])[:10]
            price = h['current_price']
            profit = h.get('profit', 0)
            strategy = h.get('recommended_strategy', 'Hold')[:14]
            rec = h.get('recommendation', '持有')[:20]
            
            lines.append(f"{name:<12} {price:>8.3f} {profit:>+9.2f} {strategy:<16} {rec}")
    
    lines.append("-" * 80)
    
    # 账户汇总
    if portfolio['summary']['total_value'] > 0:
        s = portfolio['summary']
        lines.extend([
            "",
            "💰 账户汇总",
            "-" * 80,
            f"   总市值:   ¥{s['total_value']:,.2f}",
            f"   总成本:   ¥{s['total_cost']:,.2f}",
            f"   总盈亏:   ¥{s['total_profit']:+.2f} ({s['total_profit_pct']:+.2f}%)",
            "-" * 80,
        ])
    
    # 最优策略说明
    lines.extend([
        "",
        "📋 最优策略应用说明",
        "-" * 80,
        "基于2024+2025双年回测数据，各ETF最优策略如下:",
        "",
    ])
    
    for code, strategy in best_strategies.items():
        name = dict(holdings).get(code, code)
        lines.append(f"   • {name}: {strategy}")
    
    lines.extend([
        "",
        "策略选择逻辑:",
        "   • Buy&Hold: 适用于趋势明确的牛市",
        "   • MA Cross: 适用于波动较大的市场",
        "   • RSI: 适用于震荡市，捕捉超买超卖",
        "   • Bollinger: 适用于均值回归行情",
    ])
    
    # 今日操作清单
    lines.extend([
        "",
        "📌 今日操作清单（基于最优策略）",
        "-" * 80,
    ])
    
    actions = []
    for h in portfolio['holdings']:
        if 'error' not in h:
            rec = h.get('recommendation', '')
            if any(x in rec for x in ['止盈', '止损', '减仓']):
                actions.append(f"   [ ] {h.get('name', h['code'])}: {rec}")
    
    if actions:
        lines.extend(actions)
    else:
        lines.append("   暂无紧急操作，继续持有")
    
    lines.extend([
        "",
        "=" * 80,
        f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "*策略版本: 持仓股最优策略 (方案B增强版)*",
        "*数据来源: 2024+2025双年回测 + 2026年QVeris真实数据*",
        "=" * 80,
    ])
    
    return "\n".join(lines)


def main():
    print("=" * 80)
    print("持仓股最优策略报告生成器")
    print("=" * 80)
    
    report = generate_portfolio_optimized_report()
    print(report)
    
    # Save
    output_dir = '/home/ubuntu/.openclaw/workspace-analyzer_agent/reports'
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    filepath = f"{output_dir}/Portfolio_Optimized_{datetime.now().strftime('%Y-%m-%d')}.md"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存: {filepath}")


if __name__ == '__main__':
    main()
