#!/usr/bin/env python3
"""
ETF Analyzer - Core analysis engine (Updated)
支持2024+2025双年数据、策略回测、模拟交易
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class ETFAnalyzer:
    """ETF Investment Analyzer with Dual-Year Data Support"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.data_cache = {}
        self.data_2024 = None
        self.data_2025 = None
        self._load_dual_year_data()
    
    def _load_config(self, path: str = None) -> Dict:
        """Load portfolio configuration"""
        if path is None:
            path = '/home/ubuntu/.openclaw/workspace-analyzer_agent/skills/etf-investment-analyzer/references/portfolio_config.json'
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'holdings': []}
    
    def _load_dual_year_data(self):
        """Load 2024, 2025, and 2026 historical data"""
        base_path = '/home/ubuntu/.openclaw/workspace-analyzer_agent'
        
        # Load 2024 data
        try:
            with open(f'{base_path}/etf_price_data_2024.json', 'r') as f:
                self.data_2024 = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data_2024 = {}
        
        # Load 2025 data
        try:
            with open(f'{base_path}/etf_price_data_2025.json', 'r') as f:
                self.data_2025 = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data_2025 = {}
        
        # Load 2026 data (if exists)
        try:
            with open(f'{base_path}/etf_price_data_2026.json', 'r') as f:
                self.data_2026 = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data_2026 = {}
    
    def get_etf_data(self, etf_code: str, use_dual_year: bool = True) -> Optional[pd.DataFrame]:
        """Get ETF data with 2024+2025+2026 triple-year support"""
        # Normalize code
        code = etf_code.replace('.SH', '').replace('.SZ', '')
        
        frames = []
        
        # Load 2024 data if available
        if use_dual_year and self.data_2024 and code in self.data_2024:
            df_2024 = pd.DataFrame(self.data_2024[code])
            df_2024['date'] = pd.to_datetime(df_2024['date'])
            frames.append(df_2024)
        
        # Load 2025 data
        if self.data_2025 and code in self.data_2025:
            df_2025 = pd.DataFrame(self.data_2025[code])
            df_2025['date'] = pd.to_datetime(df_2025['date'])
            frames.append(df_2025)
        
        # Load 2026 data (real-time collected)
        if hasattr(self, 'data_2026') and self.data_2026 and code in self.data_2026:
            df_2026 = pd.DataFrame(self.data_2026[code])
            df_2026['date'] = pd.to_datetime(df_2026['date'])
            frames.append(df_2026)
        
        if not frames:
            return None
        
        # Combine and sort
        combined = pd.concat(frames, ignore_index=True)
        combined = combined.sort_values('date').drop_duplicates(subset=['date'])
        return combined.reset_index(drop=True)
    
    def calculate_ma(self, prices: pd.Series, window: int) -> pd.Series:
        """Calculate Moving Average"""
        return prices.rolling(window=window, min_periods=1).mean()
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        dif = ema_fast - ema_slow
        dea = dif.ewm(span=signal, adjust=False).mean()
        macd = 2 * (dif - dea)
        return {'dif': dif, 'dea': dea, 'macd': macd}
    
    def calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI with proper handling"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=window, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window, min_periods=1).mean()
        rs = gain / (loss + 1e-10)  # Avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # Fill NaN with neutral value
    
    def calculate_bollinger(self, prices: pd.Series, window: int = 20, num_std: int = 2) -> Dict:
        """Calculate Bollinger Bands"""
        ma = prices.rolling(window=window, min_periods=1).mean()
        std = prices.rolling(window=window, min_periods=1).std()
        upper = ma + (std * num_std)
        lower = ma - (std * num_std)
        return {'upper': upper, 'middle': ma, 'lower': lower}
    
    def calculate_kdj(self, prices: pd.Series, n: int = 9, m1: int = 3, m2: int = 3) -> Dict:
        """Calculate KDJ"""
        low_list = prices.rolling(window=n, min_periods=1).min()
        high_list = prices.rolling(window=n, min_periods=1).max()
        
        # Avoid division by zero
        range_val = high_list - low_list
        rsv = np.where(range_val > 0, (prices - low_list) / range_val * 100, 50)
        rsv = pd.Series(rsv, index=prices.index)
        
        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d
        return {'k': k, 'd': d, 'j': j}
    
    def generate_signals(self, indicators: Dict, price: float, prev_price: float) -> List[str]:
        """Generate trading signals with improved logic"""
        signals = []
        
        # MACD signal - golden cross / death cross
        macd_dif = indicators['macd']['dif']
        macd_dea = indicators['macd']['dea']
        if len(macd_dif) >= 2:
            if macd_dif.iloc[-1] > macd_dea.iloc[-1] and macd_dif.iloc[-2] <= macd_dea.iloc[-2]:
                signals.append('MACD金叉')
            elif macd_dif.iloc[-1] < macd_dea.iloc[-1] and macd_dif.iloc[-2] >= macd_dea.iloc[-2]:
                signals.append('MACD死叉')
        
        # RSI signal
        rsi_val = indicators['rsi14'].iloc[-1]
        if rsi_val > 70:
            signals.append('RSI超买')
        elif rsi_val < 30:
            signals.append('RSI超卖')
        
        # Bollinger signal
        upper = indicators['bollinger']['upper'].iloc[-1]
        lower = indicators['bollinger']['lower'].iloc[-1]
        if price > upper:
            signals.append('突破布林上轨')
        elif price < lower:
            signals.append('跌破布林下轨')
        
        # KDJ signal
        kdj_k = indicators['kdj']['k']
        kdj_d = indicators['kdj']['d']
        if len(kdj_k) >= 2:
            if kdj_k.iloc[-1] > kdj_d.iloc[-1] and kdj_k.iloc[-2] <= kdj_d.iloc[-2]:
                signals.append('KDJ金叉')
            elif kdj_k.iloc[-1] < kdj_d.iloc[-1] and kdj_k.iloc[-2] >= kdj_d.iloc[-2]:
                signals.append('KDJ死叉')
        
        # Trend signal
        ma5 = indicators['ma5'].iloc[-1]
        ma20 = indicators['ma20'].iloc[-1]
        if price > ma5 > ma20:
            signals.append('多头排列')
        elif price < ma5 < ma20:
            signals.append('空头排列')
        
        return signals
    
    def analyze_etf(self, etf_code: str, data: pd.DataFrame = None, use_dual_year: bool = True) -> Dict:
        """Analyze single ETF with comprehensive indicators"""
        if data is None:
            data = self.get_etf_data(etf_code, use_dual_year)
        
        if data is None or len(data) < 20:
            return {'error': 'Insufficient data', 'code': etf_code}
        
        prices = data['price'] if 'price' in data.columns else data['close']
        
        # Calculate indicators
        indicators = {
            'ma5': self.calculate_ma(prices, 5),
            'ma10': self.calculate_ma(prices, 10),
            'ma20': self.calculate_ma(prices, 20),
            'ma60': self.calculate_ma(prices, 60) if len(prices) >= 60 else None,
            'macd': self.calculate_macd(prices),
            'rsi6': self.calculate_rsi(prices, 6),
            'rsi14': self.calculate_rsi(prices, 14),
            'bollinger': self.calculate_bollinger(prices),
            'kdj': self.calculate_kdj(prices)
        }
        
        current_price = prices.iloc[-1]
        prev_price = prices.iloc[-2] if len(prices) >= 2 else current_price
        
        # Generate signals
        signals = self.generate_signals(indicators, current_price, prev_price)
        
        # Calculate returns
        long_return = (current_price / prices.iloc[0] - 1) * 100
        short_return = (current_price / prices.iloc[-20] - 1) * 100 if len(prices) >= 20 else 0
        
        # Determine trend
        trend = self._determine_trend(indicators, current_price)
        
        return {
            'code': etf_code,
            'current_price': current_price,
            'long_return': long_return,
            'short_return': short_return,
            'rsi6': indicators['rsi6'].iloc[-1],
            'rsi14': indicators['rsi14'].iloc[-1],
            'ma5': indicators['ma5'].iloc[-1],
            'ma20': indicators['ma20'].iloc[-1],
            'ma60': indicators['ma60'].iloc[-1] if indicators['ma60'] is not None else None,
            'signals': signals,
            'trend': trend,
            'indicators': indicators,
            'data_points': len(prices)
        }
    
    def _determine_trend(self, indicators: Dict, price: float) -> str:
        """Determine market trend"""
        ma5 = indicators['ma5'].iloc[-1]
        ma20 = indicators['ma20'].iloc[-1]
        ma60 = indicators['ma60'].iloc[-1] if indicators['ma60'] is not None else None
        
        if price > ma5 > ma20:
            if ma60 and ma20 > ma60:
                return '强势多头'
            return '多头'
        elif price < ma5 < ma20:
            if ma60 and ma20 < ma60:
                return '强势空头'
            return '空头'
        else:
            return '震荡'
    
    def backtest_strategy(self, etf_code: str, strategy: str = 'buy_hold', 
                         start_date: str = None, end_date: str = None) -> Dict:
        """Backtest trading strategy"""
        data = self.get_etf_data(etf_code)
        if data is None or len(data) < 60:
            return {'error': 'Insufficient data for backtest'}
        
        prices = data['price'] if 'price' in data.columns else data['close']
        
        if strategy == 'buy_hold':
            return self._backtest_buy_hold(prices)
        elif strategy == 'ma_cross':
            return self._backtest_ma_cross(prices)
        elif strategy == 'rsi':
            return self._backtest_rsi(prices)
        elif strategy == 'bollinger':
            return self._backtest_bollinger(prices)
        else:
            return {'error': f'Unknown strategy: {strategy}'}
    
    def _backtest_buy_hold(self, prices: pd.Series) -> Dict:
        """Backtest Buy & Hold strategy"""
        total_return = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
        max_price = prices.expanding().max()
        drawdown = ((prices - max_price) / max_price * 100).min()
        
        return {
            'strategy': 'Buy & Hold',
            'total_return': total_return,
            'max_drawdown': drawdown,
            'trades': 1,
            'win_rate': 100 if total_return > 0 else 0
        }
    
    def _backtest_ma_cross(self, prices: pd.Series, short: int = 5, long: int = 20) -> Dict:
        """Backtest MA Crossover strategy"""
        ma_short = prices.rolling(short).mean()
        ma_long = prices.rolling(long).mean()
        
        position = 0
        trades = []
        entry_price = 0
        
        for i in range(long, len(prices)):
            if ma_short.iloc[i] > ma_long.iloc[i] and ma_short.iloc[i-1] <= ma_long.iloc[i-1]:
                if position == 0:
                    position = 1
                    entry_price = prices.iloc[i]
            elif ma_short.iloc[i] < ma_long.iloc[i] and ma_short.iloc[i-1] >= ma_long.iloc[i-1]:
                if position == 1:
                    profit = (prices.iloc[i] / entry_price - 1) * 100
                    trades.append(profit)
                    position = 0
        
        if position == 1:
            profit = (prices.iloc[-1] / entry_price - 1) * 100
            trades.append(profit)
        
        total_return = sum(trades) if trades else 0
        win_rate = len([t for t in trades if t > 0]) / len(trades) * 100 if trades else 0
        
        return {
            'strategy': f'MA Cross ({short}/{long})',
            'total_return': total_return,
            'trades': len(trades),
            'win_rate': win_rate,
            'avg_profit': np.mean(trades) if trades else 0
        }
    
    def _backtest_rsi(self, prices: pd.Series, period: int = 14) -> Dict:
        """Backtest RSI strategy"""
        rsi = self.calculate_rsi(prices, period)
        
        position = 0
        trades = []
        entry_price = 0
        
        for i in range(period, len(prices)):
            if rsi.iloc[i] < 30 and position == 0:
                position = 1
                entry_price = prices.iloc[i]
            elif rsi.iloc[i] > 70 and position == 1:
                profit = (prices.iloc[i] / entry_price - 1) * 100
                trades.append(profit)
                position = 0
        
        if position == 1:
            profit = (prices.iloc[-1] / entry_price - 1) * 100
            trades.append(profit)
        
        total_return = sum(trades) if trades else 0
        win_rate = len([t for t in trades if t > 0]) / len(trades) * 100 if trades else 0
        
        return {
            'strategy': f'RSI ({period})',
            'total_return': total_return,
            'trades': len(trades),
            'win_rate': win_rate,
            'avg_profit': np.mean(trades) if trades else 0
        }
    
    def _backtest_bollinger(self, prices: pd.Series, window: int = 20) -> Dict:
        """Backtest Bollinger Bands strategy"""
        bb = self.calculate_bollinger(prices, window)
        
        position = 0
        trades = []
        entry_price = 0
        
        for i in range(window, len(prices)):
            if prices.iloc[i] < bb['lower'].iloc[i] and position == 0:
                position = 1
                entry_price = prices.iloc[i]
            elif prices.iloc[i] > bb['upper'].iloc[i] and position == 1:
                profit = (prices.iloc[i] / entry_price - 1) * 100
                trades.append(profit)
                position = 0
        
        if position == 1:
            profit = (prices.iloc[-1] / entry_price - 1) * 100
            trades.append(profit)
        
        total_return = sum(trades) if trades else 0
        win_rate = len([t for t in trades if t > 0]) / len(trades) * 100 if trades else 0
        
        return {
            'strategy': f'Bollinger ({window})',
            'total_return': total_return,
            'trades': len(trades),
            'win_rate': win_rate,
            'avg_profit': np.mean(trades) if trades else 0
        }
    
    def analyze_portfolio(self, holdings: List[Dict] = None) -> Dict:
        """Analyze entire portfolio"""
        if holdings is None:
            holdings = self.config.get('holdings', [])
        
        results = []
        total_value = 0
        total_cost = 0
        
        for holding in holdings:
            analysis = self.analyze_etf(holding['code'])
            if 'error' not in analysis:
                current_value = analysis['current_price'] * holding['shares']
                cost_value = holding['cost'] * holding['shares']
                profit = current_value - cost_value
                profit_pct = (analysis['current_price'] / holding['cost'] - 1) * 100
                
                # Generate recommendation
                recommendation = self._generate_recommendation(analysis, profit_pct)
                
                analysis.update({
                    'name': holding.get('name', holding['code']),
                    'shares': holding['shares'],
                    'cost': holding['cost'],
                    'market_value': current_value,
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'recommendation': recommendation
                })
                
                total_value += current_value
                total_cost += cost_value
            
            results.append(analysis)
        
        total_profit = total_value - total_cost
        total_profit_pct = (total_value / total_cost - 1) * 100 if total_cost > 0 else 0
        
        return {
            'holdings': results,
            'summary': {
                'total_value': total_value,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'total_profit_pct': total_profit_pct
            }
        }
    
    def _generate_recommendation(self, analysis: Dict, profit_pct: float) -> str:
        """Generate trading recommendation"""
        signals = analysis.get('signals', [])
        trend = analysis.get('trend', '震荡')
        
        if profit_pct > 50:
            return '考虑部分止盈 (盈利超50%)'
        elif profit_pct < -20:
            return '严格止损/逢低补仓 (深度浮亏)'
        elif profit_pct < -15:
            return '持有观望/逢低补仓'
        elif 'RSI超卖' in signals or '跌破布林下轨' in signals:
            return '关注反弹机会'
        elif 'RSI超买' in signals:
            return '考虑减仓'
        elif '多头排列' in signals:
            return '持有'
        elif trend == '强势多头':
            return '持有'
        else:
            return '持有观望'
    
    def get_optimal_strategy(self, etf_code: str) -> Dict:
        """Find optimal strategy for ETF based on backtest"""
        strategies = ['buy_hold', 'ma_cross', 'rsi', 'bollinger']
        results = []
        
        for strategy in strategies:
            result = self.backtest_strategy(etf_code, strategy)
            if 'error' not in result:
                results.append(result)
        
        if not results:
            return {'error': 'No valid backtest results'}
        
        # Sort by total return
        results.sort(key=lambda x: x['total_return'], reverse=True)
        
        return {
            'etf_code': etf_code,
            'optimal_strategy': results[0]['strategy'],
            'all_results': results
        }


class TradingSimulator:
    """Simulated trading system"""
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {code: {'shares': int, 'cost': float}}
        self.trades = []
    
    def buy(self, code: str, price: float, shares: int, reason: str = '') -> bool:
        """Execute buy order"""
        cost = price * shares
        if cost > self.cash:
            return False
        
        self.cash -= cost
        
        if code in self.positions:
            # Update average cost
            total_shares = self.positions[code]['shares'] + shares
            total_cost = self.positions[code]['shares'] * self.positions[code]['cost'] + cost
            self.positions[code]['shares'] = total_shares
            self.positions[code]['cost'] = total_cost / total_shares
        else:
            self.positions[code] = {'shares': shares, 'cost': price}
        
        self.trades.append({
            'time': datetime.now().isoformat(),
            'action': 'BUY',
            'code': code,
            'price': price,
            'shares': shares,
            'amount': cost,
            'reason': reason
        })
        
        return True
    
    def sell(self, code: str, price: float, shares: int, reason: str = '') -> bool:
        """Execute sell order"""
        if code not in self.positions or self.positions[code]['shares'] < shares:
            return False
        
        revenue = price * shares
        self.cash += revenue
        
        self.positions[code]['shares'] -= shares
        if self.positions[code]['shares'] == 0:
            del self.positions[code]
        
        self.trades.append({
            'time': datetime.now().isoformat(),
            'action': 'SELL',
            'code': code,
            'price': price,
            'shares': shares,
            'amount': revenue,
            'reason': reason
        })
        
        return True
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Dict:
        """Get current portfolio value"""
        position_value = 0
        for code, pos in self.positions.items():
            if code in current_prices:
                position_value += pos['shares'] * current_prices[code]
        
        total_value = self.cash + position_value
        
        return {
            'cash': self.cash,
            'position_value': position_value,
            'total_value': total_value,
            'total_return': (total_value / self.initial_capital - 1) * 100,
            'positions': self.positions
        }
    
    def get_trade_report(self) -> str:
        """Generate trade report"""
        lines = [
            "=" * 60,
            "📊 模拟交易报告",
            "=" * 60,
            f"初始资金: ¥{self.initial_capital:,.2f}",
            f"当前现金: ¥{self.cash:,.2f}",
            f"持仓数量: {len(self.positions)}",
            f"交易次数: {len(self.trades)}",
            "-" * 60,
            "交易记录:",
        ]
        
        for trade in self.trades[-10:]:  # Show last 10 trades
            lines.append(f"  {trade['action']} {trade['code']} {trade['shares']}股 @ ¥{trade['price']:.3f} - {trade['reason']}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


if __name__ == '__main__':
    # Test the analyzer
    analyzer = ETFAnalyzer()
    
    print("=" * 60)
    print("ETF Investment Analyzer - Test Run")
    print("=" * 60)
    
    # Test single ETF analysis
    result = analyzer.analyze_etf('510050')
    if 'error' not in result:
        print(f"\n🔹 上证50ETF Analysis:")
        print(f"   现价: {result['current_price']:.3f}")
        print(f"   趋势: {result['trend']}")
        print(f"   RSI(14): {result['rsi14']:.1f}")
        print(f"   信号: {', '.join(result['signals']) if result['signals'] else '无'}")
    
    # Test backtest
    print("\n" + "=" * 60)
    print("策略回测结果:")
    print("=" * 60)
    
    for strategy in ['buy_hold', 'ma_cross', 'rsi', 'bollinger']:
        result = analyzer.backtest_strategy('510050', strategy)
        if 'error' not in result:
            print(f"   {result['strategy']}: 收益 {result['total_return']:+.2f}%, 交易 {result['trades']}次")
    
    # Test portfolio analysis
    print("\n" + "=" * 60)
    print("持仓组合分析:")
    print("=" * 60)
    
    portfolio = analyzer.analyze_portfolio()
    if portfolio['summary']['total_value'] > 0:
        summary = portfolio['summary']
        print(f"   总市值: ¥{summary['total_value']:,.2f}")
        print(f"   总盈亏: ¥{summary['total_profit']:+.2f} ({summary['total_profit_pct']:+.2f}%)")
    else:
        print("   暂无持仓数据")
    
    # Test simulator
    print("\n" + "=" * 60)
    print("模拟交易测试:")
    print("=" * 60)
    
    sim = TradingSimulator(initial_capital=100000)
    sim.buy('510050', 3.105, 1000, reason='测试买入')
    print(f"   买入 510050 1000股 @ ¥3.105")
    print(f"   当前现金: ¥{sim.cash:,.2f}")
    print(sim.get_trade_report())
