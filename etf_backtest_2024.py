#!/usr/bin/env python3
"""
A股ETF交易策略回测对比 - 2024年数据
使用2024年一整年的历史数据对比各个策略的收益率
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
import json
import time

# 策略定义 (与之前相同)
class TradingStrategy:
    def __init__(self, name):
        self.name = name
    
    def generate_signals(self, df):
        raise NotImplementedError

class MACDStrategy(TradingStrategy):
    def __init__(self, fast=12, slow=26, signal=9):
        super().__init__(f"MACD({fast},{slow},{signal})")
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def generate_signals(self, df):
        df = df.copy()
        ema_fast = df['close'].ewm(span=self.fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.slow, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['signal'] = df['macd'].ewm(span=self.signal, adjust=False).mean()
        df['signal_line'] = 0
        df.loc[df['macd'] > df['signal'], 'signal_line'] = 1
        df.loc[df['macd'] < df['signal'], 'signal_line'] = -1
        df['position'] = df['signal_line'].diff()
        df['signal'] = 0
        df.loc[df['position'] > 0, 'signal'] = 1
        df.loc[df['position'] < 0, 'signal'] = -1
        return df['signal']

class RSIStrategy(TradingStrategy):
    def __init__(self, period=14, oversold=30, overbought=70):
        super().__init__(f"RSI({period})")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, df):
        df = df.copy()
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        df['signal'] = 0
        df.loc[df['rsi'] < self.oversold, 'signal'] = 1
        df.loc[df['rsi'] > self.overbought, 'signal'] = -1
        return df['signal']

class BollingerStrategy(TradingStrategy):
    def __init__(self, period=20, std_dev=2):
        super().__init__(f"Bollinger({period},{std_dev})")
        self.period = period
        self.std_dev = std_dev
    
    def generate_signals(self, df):
        df = df.copy()
        df['sma'] = df['close'].rolling(window=self.period).mean()
        df['std'] = df['close'].rolling(window=self.period).std()
        df['upper'] = df['sma'] + (df['std'] * self.std_dev)
        df['lower'] = df['sma'] - (df['std'] * self.std_dev)
        df['signal'] = 0
        df.loc[df['close'] < df['lower'], 'signal'] = 1
        df.loc[df['close'] > df['upper'], 'signal'] = -1
        return df['signal']

class GoldenCrossStrategy(TradingStrategy):
    def __init__(self, short=5, long=20):
        super().__init__(f"GoldenCross(MA{short}/MA{long})")
        self.short = short
        self.long = long
    
    def generate_signals(self, df):
        df = df.copy()
        df['ma_short'] = df['close'].rolling(window=self.short).mean()
        df['ma_long'] = df['close'].rolling(window=self.long).mean()
        df['signal_line'] = 0
        df.loc[df['ma_short'] > df['ma_long'], 'signal_line'] = 1
        df.loc[df['ma_short'] < df['ma_long'], 'signal_line'] = -1
        df['position'] = df['signal_line'].diff()
        df['signal'] = 0
        df.loc[df['position'] > 0, 'signal'] = 1
        df.loc[df['position'] < 0, 'signal'] = -1
        return df['signal']

class KDJStrategy(TradingStrategy):
    def __init__(self, n=9, m1=3, m2=3):
        super().__init__(f"KDJ({n},{m1},{m2})")
        self.n = n
        self.m1 = m1
        self.m2 = m2
    
    def generate_signals(self, df):
        df = df.copy()
        low_list = df['low'].rolling(window=self.n, min_periods=self.n).min()
        high_list = df['high'].rolling(window=self.n, min_periods=self.n).max()
        rsv = (df['close'] - low_list) / (high_list - low_list) * 100
        df['K'] = rsv.ewm(alpha=1/self.m1, adjust=False).mean()
        df['D'] = df['K'].ewm(alpha=1/self.m2, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']
        df['signal'] = 0
        df.loc[(df['K'] < 20) & (df['D'] < 20), 'signal'] = 1
        df.loc[(df['K'] > 80) & (df['D'] > 80), 'signal'] = -1
        return df['signal']

class ATRStrategy(TradingStrategy):
    def __init__(self, period=14, multiplier=2):
        super().__init__(f"ATR_Breakout({period},{multiplier})")
        self.period = period
        self.multiplier = multiplier
    
    def generate_signals(self, df):
        df = df.copy()
        df['high_low'] = df['high'] - df['low']
        df['high_close'] = abs(df['high'] - df['close'].shift())
        df['low_close'] = abs(df['low'] - df['close'].shift())
        df['tr'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=self.period).mean()
        df['upper'] = df['close'].rolling(window=self.period).max()
        df['lower'] = df['close'].rolling(window=self.period).min()
        df['signal'] = 0
        df.loc[df['close'] > df['upper'].shift(1), 'signal'] = 1
        df.loc[df['close'] < df['lower'].shift(1), 'signal'] = -1
        return df['signal']

class TurtleStrategy(TradingStrategy):
    def __init__(self, entry_period=20, exit_period=10):
        super().__init__(f"Turtle({entry_period},{exit_period})")
        self.entry_period = entry_period
        self.exit_period = exit_period
    
    def generate_signals(self, df):
        df = df.copy()
        df['entry_high'] = df['high'].rolling(window=self.entry_period).max()
        df['entry_low'] = df['low'].rolling(window=self.entry_period).min()
        df['exit_high'] = df['high'].rolling(window=self.exit_period).max()
        df['exit_low'] = df['low'].rolling(window=self.exit_period).min()
        df['signal'] = 0
        df.loc[df['close'] > df['entry_high'].shift(1), 'signal'] = 1
        df.loc[df['close'] < df['exit_low'].shift(1), 'signal'] = -1
        return df['signal']

class BuyAndHoldStrategy(TradingStrategy):
    def __init__(self):
        super().__init__("Buy&Hold")
    
    def generate_signals(self, df):
        signals = pd.Series(0, index=df.index)
        signals.iloc[0] = 1
        return signals

def backtest_strategy(df, strategy, initial_capital=100000, commission=0.0003):
    df = df.copy()
    signals = strategy.generate_signals(df)
    df['signal'] = signals
    
    position = 0
    cash = initial_capital
    shares = 0
    trades = []
    equity_curve = []
    
    for i in range(len(df)):
        row = df.iloc[i]
        price = row['close']
        signal = row['signal']
        
        if signal == 1 and position == 0:
            shares = int(cash * (1 - commission) / price)
            cost = shares * price * (1 + commission)
            cash -= cost
            position = 1
            trades.append({'type': 'buy', 'price': price, 'shares': shares})
        
        elif signal == -1 and position == 1:
            revenue = shares * price * (1 - commission)
            cash += revenue
            trades.append({'type': 'sell', 'price': price, 'shares': shares})
            shares = 0
            position = 0
        
        equity = cash + shares * price
        equity_curve.append({'date': df.index[i], 'equity': equity, 'price': price})
    
    final_price = df['close'].iloc[-1]
    final_equity = cash + shares * final_price
    
    equity_df = pd.DataFrame(equity_curve)
    equity_df.set_index('date', inplace=True)
    
    total_return = (final_equity - initial_capital) / initial_capital * 100
    
    equity_df['peak'] = equity_df['equity'].expanding().max()
    equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak'] * 100
    max_drawdown = equity_df['drawdown'].min()
    
    days = (df.index[-1] - df.index[0]).days
    if days > 0:
        annual_return = ((final_equity / initial_capital) ** (365 / days) - 1) * 100
    else:
        annual_return = 0
    
    if len(equity_df) > 1:
        daily_returns = equity_df['equity'].pct_change().dropna()
        if daily_returns.std() > 0:
            sharpe_ratio = (daily_returns.mean() - 0.02/252) / daily_returns.std() * np.sqrt(252)
        else:
            sharpe_ratio = 0
    else:
        sharpe_ratio = 0
    
    if len(trades) > 0:
        sell_trades = [t for t in trades if t['type'] == 'sell']
        if len(sell_trades) > 0:
            win_trades = [t for t in sell_trades if t.get('pnl', 0) > 0]
            win_rate = len(win_trades) / len(sell_trades) * 100
        else:
            win_rate = 0
    else:
        win_rate = 0
    
    return {
        'strategy': strategy.name,
        'initial_capital': initial_capital,
        'final_equity': final_equity,
        'total_return': total_return,
        'annual_return': annual_return,
        'max_drawdown': max_drawdown,
        'sharpe_ratio': sharpe_ratio,
        'win_rate': win_rate,
        'total_trades': len([t for t in trades if t['type'] == 'sell']),
        'trades': trades,
        'equity_curve': equity_curve
    }

def get_etf_data_with_retry(symbol, start_date='20240101', end_date='20241231', max_retries=3):
    """获取ETF历史数据，带重试机制"""
    for attempt in range(max_retries):
        try:
            print(f"    尝试 {attempt+1}/{max_retries} 获取 {symbol} 数据...")
            df = ak.fund_etf_hist_em(symbol=symbol, period="daily", 
                                      start_date=start_date, end_date=end_date, adjust="qfq")
            df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 
                          'amplitude', 'pct_change', 'change', 'turnover']
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df = df.sort_index()
            print(f"    ✅ 成功获取 {len(df)} 条数据")
            return df
        except Exception as e:
            print(f"    ❌ 失败: {str(e)[:50]}")
            if attempt < max_retries - 1:
                time.sleep(2)
    return None

def run_backtest_comparison_2024():
    """运行2024年回测对比"""
    etf_symbols = ['510050', '510300', '510500', '159915']
    strategies = [
        BuyAndHoldStrategy(),
        MACDStrategy(12, 26, 9),
        MACDStrategy(5, 35, 5),
        RSIStrategy(14, 30, 70),
        RSIStrategy(6, 20, 80),
        BollingerStrategy(20, 2),
        GoldenCrossStrategy(5, 20),
        GoldenCrossStrategy(10, 60),
        KDJStrategy(9, 3, 3),
        ATRStrategy(14, 2),
        TurtleStrategy(20, 10),
    ]
    
    results = []
    
    print("🚀 A股ETF交易策略回测系统 - 2024年数据")
    print("="*70)
    print(f"测试标的: {len(etf_symbols)} 只ETF")
    print(f"测试策略: {len(strategies)} 个")
    print(f"回测周期: 2024年全年")
    print("="*70)
    
    for symbol in etf_symbols:
        print(f"\n📊 回测标的: {symbol}")
        print("-"*70)
        
        df = get_etf_data_with_retry(symbol, '20240101', '20241231')
        if df is None or len(df) < 60:
            print(f"  数据不足，跳过")
            continue
        
        print(f"  数据范围: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"  数据条数: {len(df)}")
        
        for strategy in strategies:
            print(f"\n  测试策略: {strategy.name}")
            try:
                result = backtest_strategy(df, strategy)
                result['symbol'] = symbol
                results.append(result)
                print(f"    总收益率: {result['total_return']:+.2f}% | 最大回撤: {result['max_drawdown']:.2f}% | 夏普: {result['sharpe_ratio']:.2f}")
            except Exception as e:
                print(f"    回测失败: {e}")
    
    return results

def print_comparison_report(results):
    """打印对比报告"""
    print("\n" + "="*80)
    print("📊 A股ETF交易策略回测对比报告 - 2024年")
    print("="*80)
    
    if not results:
        print("无回测结果")
        return
    
    strategy_stats = {}
    for r in results:
        name = r['strategy']
        if name not in strategy_stats:
            strategy_stats[name] = []
        strategy_stats[name].append(r)
    
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
    
    summary.sort(key=lambda x: x['avg_return'], reverse=True)
    
    print(f"\n{'排名':<4} {'策略名称':<25} {'平均收益':<12} {'最大回撤':<12} {'夏普比率':<10} {'胜率':<8} {'交易次数':<8}")
    print("-"*80)
    
    for i, s in enumerate(summary, 1):
        print(f"{i:<4} {s['strategy']:<25} {s['avg_return']:>+10.2f}% {s['avg_drawdown']:>10.2f}% {s['avg_sharpe']:>10.2f} {s['avg_winrate']:>7.1f}% {s['total_trades']:>8d}")
    
    print("\n" + "="*80)
    print("📈 最佳策略推荐 (2024年数据):")
    if summary:
        best = summary[0]
        print(f"   🥇 {best['strategy']}")
        print(f"      平均收益率: {best['avg_return']:+.2f}%")
        print(f"      平均最大回撤: {best['avg_drawdown']:.2f}%")
        print(f"      平均夏普比率: {best['avg_sharpe']:.2f}")
    
    # 对比2024 vs 2025
    print("\n" + "="*80)
    print("📊 2024 vs 2025 对比:")
    print("-"*80)
    print("2024年市场环境与2025年不同，策略表现会有差异")
    print("建议结合多年数据进行策略选择")
    
    output_file = '/home/ubuntu/.openclaw/workspace-analyzer_agent/backtest_results_2024.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n💾 详细结果已保存到: {output_file}")

def main():
    results = run_backtest_comparison_2024()
    print_comparison_report(results)

if __name__ == "__main__":
    main()
