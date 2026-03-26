#!/usr/bin/env python3
"""
Daily Analysis Report Generator
每日分析报告生成器 - 支持双年数据、策略回测、模拟交易
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add scripts to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from etf_analyzer import ETFAnalyzer, TradingSimulator


def generate_daily_report(analyzer: ETFAnalyzer, simulator: TradingSimulator = None) -> str:
    """Generate comprehensive daily analysis report"""
    
    lines = [
        "=" * 70,
        f"📊 ETF持仓分析报告 - {datetime.now().strftime('%Y-%m-%d')}",
        f"分析时间: {datetime.now().strftime('%H:%M')}",
        f"数据周期: 2024+2025+2026历史数据",
        "=" * 70,
    ]
    
    # Portfolio analysis
    portfolio = analyzer.analyze_portfolio()
    
    if portfolio['summary']['total_value'] > 0:
        summary = portfolio['summary']
        lines.extend([
            "",
            "💰 账户总览",
            "-" * 70,
            f"   总市值:   ¥{summary['total_value']:,.2f}",
            f"   总成本:   ¥{summary['total_cost']:,.2f}",
            f"   总盈亏:   ¥{summary['total_profit']:+.2f} ({summary['total_profit_pct']:+.2f}%)",
            "-" * 70,
        ])
        
        # Holdings detail
        lines.extend([
            "",
            "📈 持仓明细",
            "-" * 70,
            f"{'名称':<12} {'代码':<10} {'现价':>8} {'盈亏':>10} {'盈亏%':>8} {'趋势':<8} {'建议'}",
            "-" * 70,
        ])
        
        for h in portfolio['holdings']:
            if 'error' not in h:
                name = h.get('name', h['code'])[:10]
                code = h['code'][:10]
                price = h['current_price']
                profit = h.get('profit', 0)
                profit_pct = h.get('profit_pct', 0)
                trend = h.get('trend', '未知')[:6]
                rec = h.get('recommendation', '持有')[:12]
                
                lines.append(f"{name:<12} {code:<10} {price:>8.3f} {profit:>+10.2f} {profit_pct:>+7.2f}% {trend:<8} {rec}")
        
        lines.append("-" * 70)
    
    # Strategy backtest summary
    lines.extend([
        "",
        "🎯 策略回测摘要 (基于双年数据)",
        "-" * 70,
    ])
    
    # Get first holding for strategy comparison
    holdings = analyzer.config.get('holdings', [])
    if holdings:
        sample_code = holdings[0]['code']
        optimal = analyzer.get_optimal_strategy(sample_code)
        
        if 'error' not in optimal:
            lines.append(f"   最优策略: {optimal['optimal_strategy']}")
            lines.append("")
            lines.append("   策略对比:")
            for result in optimal['all_results'][:3]:
                lines.append(f"      {result['strategy']:<20} 收益: {result['total_return']:>+7.2f}%  交易: {result['trades']:>2}次")
    
    # Trading signals
    lines.extend([
        "",
        "📢 今日交易信号",
        "-" * 70,
    ])
    
    has_signal = False
    for h in portfolio['holdings']:
        if 'error' not in h and h.get('signals'):
            has_signal = True
            lines.append(f"   {h.get('name', h['code'])}: {', '.join(h['signals'])}")
    
    if not has_signal:
        lines.append("   暂无明确交易信号")
    
    # Simulator report
    if simulator:
        lines.extend([
            "",
            "🎮 模拟交易状态",
            "-" * 70,
        ])
        
        # Get current prices for portfolio valuation
        current_prices = {}
        for h in portfolio['holdings']:
            if 'error' not in h:
                current_prices[h['code']] = h['current_price']
        
        sim_status = simulator.get_portfolio_value(current_prices)
        lines.extend([
            f"   初始资金: ¥{simulator.initial_capital:,.2f}",
            f"   当前现金: ¥{sim_status['cash']:,.2f}",
            f"   持仓市值: ¥{sim_status['position_value']:,.2f}",
            f"   总资产:   ¥{sim_status['total_value']:,.2f}",
            f"   总收益:   {sim_status['total_return']:+.2f}%",
            f"   交易次数: {len(simulator.trades)}",
        ])
        
        if simulator.trades:
            lines.append("")
            lines.append("   最近交易:")
            for trade in simulator.trades[-5:]:
                action = "买入" if trade['action'] == 'BUY' else "卖出"
                lines.append(f"      {action} {trade['code']} {trade['shares']}股 @ ¥{trade['price']:.3f}")
    
    # Operation checklist
    lines.extend([
        "",
        "📋 今日操作清单",
        "-" * 70,
    ])
    
    for h in portfolio['holdings']:
        if 'error' not in h:
            rec = h.get('recommendation', '')
            if '止盈' in rec or '止损' in rec or '补仓' in rec:
                lines.append(f"   [ ] {h.get('name', h['code'])}: {rec}")
    
    lines.extend([
        "",
        "=" * 70,
        f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "*数据来源: 2024+2025历史数据 + 2026年QVeris真实数据*",
        "=" * 70,
    ])
    
    return "\n".join(lines)


def save_report(report: str, output_dir: str = None):
    """Save report to file"""
    if output_dir is None:
        output_dir = '/home/ubuntu/.openclaw/workspace-analyzer_agent/reports'
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    filename = f"ETF_Analysis_{datetime.now().strftime('%Y-%m-%d')}.md"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return filepath


def main():
    """Main entry point"""
    print("=" * 70)
    print("ETF Daily Analysis Report Generator")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = ETFAnalyzer()
    
    # Initialize simulator (load from saved state if exists)
    simulator = TradingSimulator(initial_capital=100000)
    
    # Generate report
    report = generate_daily_report(analyzer, simulator)
    
    # Print to console
    print(report)
    
    # Save to file
    filepath = save_report(report)
    print(f"\n✅ 报告已保存: {filepath}")
    
    return report


if __name__ == '__main__':
    main()
