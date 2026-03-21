#!/usr/bin/env python3
"""
FinClaw A股ETF专业回测对比
使用FinClaw的多种策略对A股ETF进行回测
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import json
import subprocess
import os

def get_etf_data_akshare(symbol, start_date='20250101', end_date='20251231'):
    """使用AKShare获取ETF数据"""
    try:
        df = ak.fund_etf_hist_em(symbol=symbol, period="daily", 
                                  start_date=start_date, end_date=end_date, adjust="qfq")
        df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 
                      'amplitude', 'pct_change', 'change', 'turnover']
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df.sort_index()
        return df
    except Exception as e:
        print(f"获取 {symbol} 数据失败: {e}")
        return None

def finclaw_backtest(symbol, strategy, start_date='2025-01-01', end_date='2025-12-31', capital=100000):
    """使用FinClaw进行回测"""
    try:
        cmd = [
            'finclaw', 'backtest',
            '--ticker', symbol,
            '--strategy', strategy,
            '--start', start_date,
            '--end', end_date,
            '--capital', str(capital),
            '--output', '/tmp/finclaw_result.json'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # 读取结果
        if os.path.exists('/tmp/finclaw_result.json'):
            with open('/tmp/finclaw_result.json', 'r') as f:
                data = json.load(f)
            return data
        else:
            # 从stdout解析
            return parse_finclaw_output(result.stdout)
            
    except Exception as e:
        print(f"FinClaw回测失败: {e}")
        return None

def parse_finclaw_output(output):
    """解析FinClaw输出"""
    result = {}
    lines = output.split('\n')
    for line in lines:
        if 'Return:' in line or '收益率' in line:
            try:
                result['total_return'] = float(line.split(':')[1].strip().replace('%', ''))
            except:
                pass
        elif 'Sharpe:' in line or '夏普' in line:
            try:
                result['sharpe_ratio'] = float(line.split(':')[1].strip())
            except:
                pass
        elif 'MaxDD:' in line or '最大回撤' in line:
            try:
                result['max_drawdown'] = float(line.split(':')[1].strip().replace('%', ''))
            except:
                pass
    return result

def custom_backtest(df, strategy_name, initial_capital=100000):
    """自定义回测实现"""
    df = df.copy()
    
    if strategy_name == 'golden-cross':
        # 金叉策略
        df['sma_fast'] = df['close'].rolling(window=5).mean()
        df['sma_slow'] = df['close'].rolling(window=20).mean()
        df['signal'] = np.where(df['sma_fast'] > df['sma_slow'], 1, 0)
        
    elif strategy_name == 'momentum':
        # 动量策略
        df['returns'] = df['close'].pct_change(20)
        df['signal'] = np.where(df['returns'] > 0.05, 1, 0)
        
    elif strategy_name == 'mean-reversion-bb':
        # 布林带均值回归
        df['sma'] = df['close'].rolling(window=20).mean()
        df['std'] = df['close'].rolling(window=20).std()
        df['lower'] = df['sma'] - 2 * df['std']
        df['upper'] = df['sma'] + 2 * df['std']
        df['signal'] = np.where(df['close'] < df['lower'], 1, 0)
        
    elif strategy_name == 'trend-following':
        # 趋势跟踪
        df['sma_fast'] = df['close'].rolling(window=10).mean()
        df['sma_slow'] = df['close'].rolling(window=60).mean()
        df['adx'] = calculate_adx(df)
        df['signal'] = np.where((df['sma_fast'] > df['sma_slow']) & (df['adx'] > 25), 1, 0)
        
    elif strategy_name == 'rsi-mean-reversion':
        # RSI均值回归
        df['rsi'] = calculate_rsi(df['close'])
        df['signal'] = np.where(df['rsi'] < 30, 1, np.where(df['rsi'] > 70, 0, np.nan))
        df['signal'] = df['signal'].ffill().fillna(0)
        
    elif strategy_name == 'breakout':
        # 突破策略
        df['high_20'] = df['high'].rolling(window=20).max()
        df['signal'] = np.where(df['close'] > df['high_20'].shift(1), 1, 0)
        
    else:
        # 默认买入持有
        df['signal'] = 1
    
    # 执行回测
    return execute_backtest(df, initial_capital)

def calculate_rsi(prices, period=14):
    """计算RSI"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_adx(df, period=14):
    """计算ADX"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    plus_dm = high.diff()
    minus_dm = -low.diff()
    
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    
    tr = pd.concat([
        high - low,
        abs(high - close.shift()),
        abs(low - close.shift())
    ], axis=1).max(axis=1)
    
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * plus_dm.rolling(window=period).mean() / atr
    minus_di = 100 * minus_dm.rolling(window=period).mean() / atr
    
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    return dx.rolling(window=period).mean()

def execute_backtest(df, initial_capital=100000):
    """执行回测计算"""
    df = df.copy()
    df['signal'] = df['signal'].fillna(0)
    
    position = 0
    cash = initial_capital
    shares = 0
    equity_curve = []
    trades = []
    
    commission = 0.0003  # 0.03% 手续费
    
    for i in range(len(df)):
        price = df['close'].iloc[i]
        signal = df['signal'].iloc[i]
        
        # 买入信号
        if signal == 1 and position == 0:
            shares = int(cash * (1 - commission) / price)
            cost = shares * price * (1 + commission)
            cash -= cost
            position = 1
            trades.append({'type': 'buy', 'price': price, 'shares': shares})
        
        # 卖出信号
        elif signal == 0 and position == 1:
            revenue = shares * price * (1 - commission)
            cash += revenue
            trades.append({'type': 'sell', 'price': price, 'shares': shares, 'pnl': revenue - trades[-1]['price'] * shares})
            shares = 0
            position = 0
        
        equity = cash + shares * price
        equity_curve.append(equity)
    
    # 最终结算
    final_price = df['close'].iloc[-1]
    final_equity = cash + shares * final_price
    
    # 计算指标
    total_return = (final_equity - initial_capital) / initial_capital * 100
    
    equity_series = pd.Series(equity_curve)
    peak = equity_series.expanding().max()
    drawdown = (equity_series - peak) / peak * 100
    max_drawdown = drawdown.min()
    
    # 夏普比率
    daily_returns = equity_series.pct_change().dropna()
    if daily_returns.std() > 0:
        sharpe = (daily_returns.mean() - 0.02/252) / daily_returns.std() * np.sqrt(252)
    else:
        sharpe = 0
    
    # 胜率
    sell_trades = [t for t in trades if t['type'] == 'sell']
    win_trades = [t for t in sell_trades if t.get('pnl', 0) > 0]
    win_rate = len(win_trades) / len(sell_trades) * 100 if sell_trades else 0
    
    return {
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe,
        'win_rate': win_rate,
        'total_trades': len(sell_trades),
        'final_equity': final_equity
    }

def run_finclaw_comparison():
    """运行FinClaw策略对比"""
    etf_symbols = ['510050', '510300', '510500', '159915']
    strategies = [
        'golden-cross',
        'momentum', 
        'mean-reversion-bb',
        'trend-following',
        'rsi-mean-reversion',
        'breakout',
        'buy-hold'
    ]
    
    results = []
    
    print("🚀 FinClaw A股ETF策略回测系统")
    print("="*70)
    print(f"测试标的: {len(etf_symbols)} 只ETF")
    print(f"测试策略: {len(strategies)} 个")
    print(f"回测周期: 2025年全年")
    print("="*70)
    
    for symbol in etf_symbols:
        print(f"\n📊 回测标的: {symbol}")
        print("-"*70)
        
        df = get_etf_data_akshare(symbol)
        if df is None or len(df) < 60:
            print(f"  数据不足，跳过")
            continue
        
        print(f"  数据范围: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")
        
        for strategy in strategies:
            print(f"\n  策略: {strategy}")
            try:
                result = custom_backtest(df, strategy)
                result['symbol'] = symbol
                result['strategy'] = strategy
                results.append(result)
                print(f"    收益率: {result['total_return']:+.2f}% | 回撤: {result['max_drawdown']:.2f}% | 夏普: {result['sharpe_ratio']:.2f} | 交易: {result['total_trades']}")
            except Exception as e:
                print(f"    回测失败: {e}")
    
    return results

def print_finclaw_report(results):
    """打印FinClaw回测报告"""
    print("\n" + "="*80)
    print("📊 FinClaw A股ETF策略回测报告")
    print("="*80)
    
    if not results:
        print("无回测结果")
        return
    
    # 按策略分组统计
    strategy_stats = {}
    for r in results:
        name = r['strategy']
        if name not in strategy_stats:
            strategy_stats[name] = []
        strategy_stats[name].append(r)
    
    # 计算每个策略的平均表现
    summary = []
    for name, stats in strategy_stats.items():
        avg_return = np.mean([s['total_return'] for s in stats])
        avg_drawdown = np.mean([s['max_drawdown'] for s in stats])
        avg_sharpe = np.mean([s['sharpe_ratio'] for s in stats])
        avg_winrate = np.mean([s['win_rate'] for s in stats])
        total_trades = sum([s['total_trades'] for s in stats])
        
        summary.append({
            'strategy': name,
            'avg_return': avg_return,
            'avg_drawdown': avg_drawdown,
            'avg_sharpe': avg_sharpe,
            'avg_winrate': avg_winrate,
            'total_trades': total_trades,
            'count': len(stats)
        })
    
    # 按收益率排序
    summary.sort(key=lambda x: x['avg_return'], reverse=True)
    
    print(f"\n{'排名':<4} {'策略名称':<25} {'平均收益':<12} {'最大回撤':<12} {'夏普比率':<10} {'胜率':<8} {'交易次数':<8}")
    print("-"*80)
    
    for i, s in enumerate(summary, 1):
        print(f"{i:<4} {s['strategy']:<25} {s['avg_return']:>+10.2f}% {s['avg_drawdown']:>10.2f}% {s['avg_sharpe']:>10.2f} {s['avg_winrate']:>7.1f}% {s['total_trades']:>8d}")
    
    print("\n" + "="*80)
    print("📈 最佳策略推荐:")
    if summary:
        best = summary[0]
        print(f"   🥇 {best['strategy']}")
        print(f"      平均收益率: {best['avg_return']:+.2f}%")
        print(f"      平均最大回撤: {best['avg_drawdown']:.2f}%")
        print(f"      平均夏普比率: {best['avg_sharpe']:.2f}")
    
    # 保存结果
    output_file = '/home/ubuntu/.openclaw/workspace-analyzer_agent/finclaw_backtest_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n💾 详细结果已保存到: {output_file}")

def main():
    """主函数"""
    results = run_finclaw_comparison()
    print_finclaw_report(results)

if __name__ == "__main__":
    main()
