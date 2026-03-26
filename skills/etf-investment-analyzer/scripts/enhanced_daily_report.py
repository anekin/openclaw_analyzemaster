#!/usr/bin/env python3
"""
Enhanced Daily Report Generator - 方案B实现
生成包含动态策略选择的每日分析报告
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_etf_analyzer import EnhancedETFAnalyzer, EnhancedTradingSimulator


def generate_enhanced_report(analyzer: EnhancedETFAnalyzer, simulator: EnhancedTradingSimulator = None) -> str:
    """Generate comprehensive daily analysis report with enhanced strategy"""
    
    lines = [
        "=" * 70,
        f"📊 ETF持仓分析报告 - {datetime.now().strftime('%Y-%m-%d')} (方案B-平衡型)",
        f"分析时间: {datetime.now().strftime('%H:%M')}",
        f"数据周期: 2024+2025+2026历史数据",
        f"策略: 动态策略选择 + 改进止盈止损 + 多因子确认",
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
        
        # Holdings detail with enhanced info
        lines.extend([
            "",
            "📈 持仓明细 (方案B动态策略)",
            "-" * 70,
            f"{'名称':<12} {'现价':>8} {'盈亏%':>8} {'市场状态':<12} {'策略':<16} {'建议'}",
            "-" * 70,
        ])
        
        for h in portfolio['holdings']:
            if 'error' not in h:
                name = h.get('name', h['code'])[:10]
                price = h['current_price']
                profit_pct = h.get('profit_pct', 0)
                regime = h.get('market_regime', 'unknown')[:10]
                strategy = h.get('recommended_strategy', 'Hold')[:14]
                rec = h.get('recommendation', '持有')[:16]
                
                lines.append(f"{name:<12} {price:>8.3f} {profit_pct:>+7.2f}% {regime:<12} {strategy:<16} {rec}")
        
        lines.append("-" * 70)
    
    # Market regime distribution
    lines.extend([
        "",
        "📊 市场状态分布",
        "-" * 70,
    ])
    
    regime_count = {}
    for h in portfolio['holdings']:
        if 'error' not in h:
            regime = h.get('market_regime', 'unknown')
            regime_count[regime] = regime_count.get(regime, 0) + 1
    
    regime_names = {
        'strong_bull': '强势牛市',
        'weak_bull': '弱势牛市',
        'consolidation': '震荡市',
        'weak_bear': '弱势熊市',
        'strong_bear': '强势熊市'
    }
    
    for regime, count in regime_count.items():
        name = regime_names.get(regime, regime)
        lines.append(f"   {name}: {count}只ETF")
    
    # Strategy recommendations
    lines.extend([
        "",
        "🎯 方案B策略说明",
        "-" * 70,
        "   动态策略选择:",
        "   - 强势牛市 (MA20>MA60, 差距>5%): Buy & Hold",
        "   - 弱势牛市 (MA20>MA60, 差距<5%): MA Cross (5/20)",
        "   - 震荡市: Bollinger均值回归",
        "   - 熊市: 减仓/空仓",
        "",
        "   改进止盈止损:",
        "   - 盈利>50%: 止盈30%仓位",
        "   - 盈利>30%: 启动移动止损-10%",
        "   - 回撤>20%: 减仓50%",
        "   - 回撤>30%: 强制清仓",
        "",
        "   多因子确认:",
        "   - 买入: MA金叉 + RSI<40",
        "   - 卖出: MA死叉 + RSI>60",
    ])
    
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
            for signal in h['signals']:
                lines.append(f"   {h.get('name', h['code'])}: {signal}")
    
    if not has_signal:
        lines.append("   暂无明确交易信号")
    
    # Action items
    lines.extend([
        "",
        "📋 今日操作清单 (方案B)",
        "-" * 70,
    ])
    
    action_items = []
    for h in portfolio['holdings']:
        if 'error' not in h:
            rec = h.get('recommendation', '')
            if any(x in rec for x in ['止盈', '止损', '减仓', '清仓']):
                action_items.append(f"   [ ] {h.get('name', h['code'])}: {rec}")
    
    if action_items:
        lines.extend(action_items)
    else:
        lines.append("   暂无紧急操作")
    
    # Simulator status
    if simulator:
        lines.extend([
            "",
            "🎮 模拟交易状态",
            "-" * 70,
            "   账户信息:",
            "   - 起始日期: 2025-03-25",
            "   - 运行天数: 2天",
            "",
        ])
        
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
    
    lines.extend([
        "",
        "=" * 70,
        f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "*策略版本: 方案B - 平衡型动态策略*",
        "*数据来源: 2024+2025历史数据 + 2026年QVeris真实数据*",
        "=" * 70,
    ])
    
    return "\n".join(lines)


def save_report(report: str, output_dir: str = None):
    """Save report to file"""
    if output_dir is None:
        output_dir = '/home/ubuntu/.openclaw/workspace-analyzer_agent/reports'
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    filename = f"ETF_Analysis_Enhanced_{datetime.now().strftime('%Y-%m-%d')}.md"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return filepath


def sync_to_feishu(portfolio: dict, simulator: EnhancedTradingSimulator = None):
    """Sync report to Feishu document and move to target folder"""
    import subprocess
    import json
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Build markdown content
    summary = portfolio['summary']
    
    content = f"""# ETF交易日报-{today}

> 分析时间: {datetime.now().strftime('%H:%M')} | 策略版本: 方案B-平衡型 | 数据周期: 2024+2025+2026历史数据

---

## 💰 账户总览

| 指标 | 数值 |
|------|------|
| 总市值 | ¥{summary['total_value']:,.2f} |
| 总成本 | ¥{summary['total_cost']:,.2f} |
| **总盈亏** | **¥{summary['total_profit']:+.2f} ({summary['total_profit_pct']:+.2f}%)** |

---

## 📈 持仓明细 (全部10只ETF)

| 名称 | 现价 | 盈亏% | 市场状态 | 策略 | 建议 |
|------|------|-------|----------|------|------|
"""
    
    for h in portfolio['holdings']:
        if 'error' not in h:
            regime_map = {
                'strong_bull': '强势牛市',
                'weak_bull': '弱势牛市', 
                'consolidation': '震荡市',
                'weak_bear': '弱势熊市',
                'strong_bear': '强势熊市'
            }
            regime = regime_map.get(h.get('market_regime', ''), h.get('market_regime', ''))
            content += f"| {h.get('name', h['code'])} | {h['current_price']:.3f} | {h.get('profit_pct', 0):+.2f}% | {regime} | {h.get('recommended_strategy', 'Hold')} | {h.get('recommendation', '持有')} |\n"
    
    content += f"""
---

## 📋 今日操作清单

"""
    
    for h in portfolio['holdings']:
        if 'error' not in h:
            rec = h.get('recommendation', '')
            if any(x in rec for x in ['止盈', '止损', '减仓', '清仓']):
                content += f"- [ ] **{h.get('name', h['code'])}**: {rec}\n"
    
    if simulator:
        content += f"""
---

## 🎮 模拟交易状态

### 账户信息
- **起始日期**: 2025-03-25
- **运行天数**: 2天

### 资金状况
| 指标 | 数值 |
|------|------|
| 初始资金 | ¥{simulator.initial_capital:,.2f} |
| 当前现金 | ¥{simulator.cash:,.2f} |
| 持仓市值 | ¥0.00 |
| 总资产 | ¥{simulator.cash:,.2f} |
| 总收益 | +0.00% |
| 交易次数 | {len(simulator.trades)} |
"""
    
    content += f"""
---

> *报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*  
> *数据来源: 2024+2025历史数据 + 2026年QVeris真实数据*
"""
    
    return content


def create_and_move_feishu_doc(content: str, folder_token: str = None):
    """Create Feishu doc and move to target folder using OpenClaw CLI"""
    import subprocess
    import json
    import re
    
    today = datetime.now().strftime('%Y-%m-%d')
    title = f"ETF交易日报-{today}"
    
    # Create doc using feishu_doc tool
    print(f"\n📤 正在创建飞书文档: {title}")
    
    # Use OpenClaw CLI to create doc
    cmd = [
        'openclaw', 'tools', 'feishu_doc', 'create',
        '--title', title,
        '--content', content
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        
        # Parse doc token from output
        doc_match = re.search(r'document_id["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]+)', output)
        if doc_match:
            doc_token = doc_match.group(1)
            print(f"✅ 飞书文档创建成功: {doc_token}")
            
            # Move to target folder if specified
            if folder_token:
                print(f"📁 正在移动到目标文件夹...")
                move_cmd = [
                    'openclaw', 'tools', 'feishu_drive', 'move',
                    '--file-token', doc_token,
                    '--folder-token', folder_token
                ]
                move_result = subprocess.run(move_cmd, capture_output=True, text=True, timeout=30)
                if move_result.returncode == 0:
                    print(f"✅ 文档已移动到目标文件夹")
                else:
                    print(f"⚠️ 移动文档失败: {move_result.stderr}")
                    print(f"   文档仍可在'我的文档'中查看")
            
            return doc_token
        else:
            print(f"⚠️ 无法解析文档ID，输出: {output[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ 创建飞书文档失败: {e}")
        return None


def main():
    """Main entry point"""
    print("=" * 70)
    print("Enhanced ETF Daily Analysis Report Generator (方案B)")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = EnhancedETFAnalyzer()
    
    # Initialize simulator
    simulator = EnhancedTradingSimulator(initial_capital=100000)
    
    # Generate report
    report = generate_enhanced_report(analyzer, simulator)
    
    # Print to console
    print(report)
    
    # Save to file
    filepath = save_report(report)
    print(f"\n✅ 报告已保存: {filepath}")
    
    # Sync to Feishu
    print("\n" + "=" * 70)
    print("正在同步到飞书文档...")
    print("=" * 70)
    
    portfolio = analyzer.analyze_portfolio()
    content = sync_to_feishu(portfolio, simulator)
    
    # Target folder token (from user)
    folder_token = "YeEEfZ0f1lvroGdQnCGc6EMvn4b"
    doc_token = create_and_move_feishu_doc(content, folder_token)
    
    if doc_token:
        print(f"\n✅ 飞书文档同步完成!")
        print(f"📄 文档链接: https://feishu.cn/docx/{doc_token}")
    else:
        print(f"\n⚠️ 飞书文档同步失败，请检查配置")
    
    return report


if __name__ == '__main__':
    main()
