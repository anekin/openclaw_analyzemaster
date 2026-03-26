#!/usr/bin/env python3
"""
Enhanced ETF Analyzer with Dynamic Strategy Selection (方案B - 平衡型)
动态策略切换 + 改进止盈止损 + 多因子确认
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class EnhancedETFAnalyzer:
    """
    增强型ETF分析器 - 方案B实现
    - 动态策略选择 (Buy&Hold <-> MA Cross)
    - 改进止盈止损
    - 多因子信号确认
    """
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.data_cache = {}
        self.data_2024 = None
        self.data_2025 = None
        self.data_2026 = None
        self._load_triple_year_data()
    
    def _load_config(self, path: str = None) -> Dict:
        """Load portfolio configuration"""
        if path is None:
            path = '/home/ubuntu/.openclaw/workspace-analyzer_agent/skills/etf-investment-analyzer/references/portfolio_config.json'
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'holdings': []}
    
    def _load_triple_year_data(self):
        """Load 2024, 2025, and 2026 historical data"""
        base_path = '/home/ubuntu/.openclaw/workspace-analyzer_agent'
        
        for year in [2024, 2025, 2026]:
            try:
                with open(f'{base_path}/etf_price_data_{year}.json', 'r') as f:
                    setattr(self, f'data_{year}', json.load(f))
            except (FileNotFoundError, json.JSONDecodeError):
                setattr(self, f'data_{year}', {})
    
    def get_etf_data(self, etf_code: str) -> Optional[pd.DataFrame]:
        """Get ETF data with triple-year support"""
        code = etf_code.replace('.SH', '').replace('.SZ', '')
        
        frames = []
        for year in [2024, 2025, 2026]:
            data = getattr(self, f'data_{year}')
            if data and code in data:
                df = pd.DataFrame(data[code])
                df['date'] = pd.to_datetime(df['date'])
                frames.append(df)
        
        if not frames:
            return None
        
        combined = pd.concat(frames, ignore_index=True)
        combined = combined.sort_values('date').drop_duplicates(subset=['date'])
        return combined.reset_index(drop=True)
    
    def calculate_ma(self, prices: pd.Series, window: int) -> pd.Series:
        """Calculate Moving Average"""
        return prices.rolling(window=window, min_periods=1).mean()
    
    def calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=window, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window, min_periods=1).mean()
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    def calculate_bollinger(self, prices: pd.Series, window: int = 20) -> Dict:
        """Calculate Bollinger Bands"""
        ma = prices.rolling(window=window, min_periods=1).mean()
        std = prices.rolling(window=window, min_periods=1).std()
        upper = ma + (std * 2)
        lower = ma - (std * 2)
        return {'upper': upper, 'middle': ma, 'lower': lower}
    
    def calculate_atr(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high = prices.rolling(window=2).max()
        low = prices.rolling(window=2).min()
        tr = high - low
        return tr.rolling(window=window, min_periods=1).mean()
    
    def determine_market_regime(self, prices: pd.Series) -> str:
        """
        判断市场状态 - 动态策略选择核心
        Returns: 'strong_bull', 'weak_bull', 'consolidation', 'weak_bear', 'strong_bear'
        """
        if len(prices) < 20:
            return 'unknown'
        
        ma20 = self.calculate_ma(prices, min(20, len(prices)//2)).iloc[-1]
        ma60 = self.calculate_ma(prices, min(60, len(prices))).iloc[-1]
        current = prices.iloc[-1]
        
        # Calculate trend strength
        trend_diff = abs(ma20 - ma60) / ma60 * 100
        
        if ma20 > ma60 and current > ma20:
            if trend_diff > 5:
                return 'strong_bull'  # 强势牛市 -> Buy&Hold
            else:
                return 'weak_bull'    # 弱势牛市 -> MA Cross
        elif ma20 < ma60 and current < ma20:
            if trend_diff > 5:
                return 'strong_bear'  # 强势熊市 -> 空仓
            else:
                return 'weak_bear'    # 弱势熊市 -> 减仓
        else:
            return 'consolidation'    # 震荡市 -> Bollinger
    
    def generate_signals_enhanced(self, indicators: Dict, price: float, 
                                   prev_price: float, regime: str) -> List[str]:
        """
        增强信号生成 - 多因子确认
        """
        signals = []
        
        ma5 = indicators['ma5'].iloc[-1]
        ma20 = indicators['ma20'].iloc[-1]
        ma60 = indicators['ma60'].iloc[-1] if indicators['ma60'] is not None else ma20
        rsi = indicators['rsi'].iloc[-1]
        bb = indicators['bollinger']
        
        # 根据市场状态选择策略
        if regime == 'strong_bull':
            # 强势牛市: 只关注趋势延续信号
            if price > ma5 > ma20:
                signals.append('强势多头-持有')
        
        elif regime == 'weak_bull':
            # 弱势牛市: MA交叉 + RSI确认
            ma5_prev = indicators['ma5'].iloc[-2]
            ma20_prev = indicators['ma20'].iloc[-2]
            
            if ma5 > ma20 and ma5_prev <= ma20_prev and rsi < 40:
                signals.append('MA金叉+RSI确认-买入')
            elif ma5 < ma20 and ma5_prev >= ma20_prev and rsi > 60:
                signals.append('MA死叉+RSI确认-卖出')
        
        elif regime == 'consolidation':
            # 震荡市: Bollinger + RSI
            if price < bb['lower'].iloc[-1] and rsi < 40:
                signals.append('跌破下轨+RSI超卖-买入')
            elif price > bb['upper'].iloc[-1] and rsi > 60:
                signals.append('突破上轨+RSI超买-卖出')
        
        elif regime in ['weak_bear', 'strong_bear']:
            # 熊市: 减仓信号
            if price < ma20:
                signals.append('空头市场-减仓')
        
        # 通用风险信号
        if rsi > 80:
            signals.append('RSI严重超买-警惕')
        elif rsi < 20:
            signals.append('RSI严重超卖-关注')
        
        return signals
    
    def calculate_position_size(self, prices: pd.Series, base_position: float = 0.2) -> float:
        """
        动态仓位管理 - 根据ATR调整
        """
        if len(prices) < 20:
            return base_position
        
        atr = self.calculate_atr(prices).iloc[-1]
        current_price = prices.iloc[-1]
        atr_pct = atr / current_price
        
        # 高波动减仓，低波动正常仓位
        if atr_pct > 0.02:  # ATR > 2%
            return base_position * 0.5
        elif atr_pct < 0.01:  # ATR < 1%
            return base_position * 1.2
        else:
            return base_position
    
    def analyze_etf(self, etf_code: str) -> Dict:
        """Analyze single ETF with enhanced strategy"""
        data = self.get_etf_data(etf_code)
        
        if data is None or len(data) < 10:
            return {'error': 'Insufficient data', 'code': etf_code}
        
        prices = data['price']
        current_price = prices.iloc[-1]
        
        # Calculate indicators
        indicators = {
            'ma5': self.calculate_ma(prices, min(5, len(prices))),
            'ma20': self.calculate_ma(prices, min(20, len(prices))),
            'ma60': self.calculate_ma(prices, min(60, len(prices))),
            'rsi': self.calculate_rsi(prices, min(14, len(prices)-1) if len(prices) > 1 else 1),
            'bollinger': self.calculate_bollinger(prices, min(20, len(prices))),
            'atr': self.calculate_atr(prices)
        }
        
        # Determine market regime
        regime = self.determine_market_regime(prices)
        
        # Generate signals
        prev_price = prices.iloc[-2] if len(prices) >= 2 else current_price
        signals = self.generate_signals_enhanced(indicators, current_price, prev_price, regime)
        
        # Calculate returns
        long_return = (current_price / prices.iloc[0] - 1) * 100
        short_return = (current_price / prices.iloc[-20] - 1) * 100 if len(prices) >= 20 else 0
        
        # Calculate position size
        position_size = self.calculate_position_size(prices)
        
        # Determine recommended strategy
        strategy_map = {
            'strong_bull': 'Buy & Hold',
            'weak_bull': 'MA Cross (5/20)',
            'consolidation': 'Bollinger Mean Reversion',
            'weak_bear': 'Reduce Position',
            'strong_bear': 'Cash'
        }
        
        return {
            'code': etf_code,
            'current_price': current_price,
            'long_return': long_return,
            'short_return': short_return,
            'rsi': indicators['rsi'].iloc[-1],
            'ma20': indicators['ma20'].iloc[-1],
            'ma60': indicators['ma60'].iloc[-1] if indicators['ma60'] is not None else indicators['ma20'].iloc[-1],
            'atr_pct': indicators['atr'].iloc[-1] / current_price * 100,
            'market_regime': regime,
            'recommended_strategy': strategy_map.get(regime, 'Hold'),
            'position_size': position_size,
            'signals': signals,
            'data_points': len(prices)
        }
    
    def analyze_portfolio(self) -> Dict:
        """Analyze entire portfolio with enhanced strategy"""
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
                
                # Generate recommendation based on profit and regime
                recommendation = self._generate_recommendation_enhanced(analysis, profit_pct)
                
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
    
    def _generate_recommendation_enhanced(self, analysis: Dict, profit_pct: float) -> str:
        """Generate enhanced trading recommendation"""
        regime = analysis.get('market_regime', '')
        signals = analysis.get('signals', [])
        position_size = analysis.get('position_size', 0.2)
        
        # Profit-based rules
        if profit_pct > 50:
            return f'🎯 止盈30%仓位 (盈利{profit_pct:.1f}%)'
        elif profit_pct > 30:
            return f'⚠️ 启动移动止损-10% (盈利{profit_pct:.1f}%)'
        elif profit_pct < -20:
            return f'🛑 回撤>20%减仓50% (亏损{profit_pct:.1f}%)'
        elif profit_pct < -30:
            return f'⛔ 强制止损 (亏损{profit_pct:.1f}%)'
        
        # Regime-based recommendations
        if regime == 'strong_bull':
            return '💪 强势牛市-持有 (建议仓位' + f'{position_size*100:.0f}%)'
        elif regime == 'weak_bull':
            return '📈 弱势牛市-MA交叉策略'
        elif regime == 'consolidation':
            return '↔️ 震荡市-高抛低吸'
        elif regime in ['weak_bear', 'strong_bear']:
            return '🔻 熊市-减仓观望'
        
        return '⏸️ 持有观望'


class EnhancedTradingSimulator:
    """
    增强型交易模拟器 - 方案B实现
    - 动态止盈止损
    - 仓位管理
    - 交易记录
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {code: {'shares': int, 'cost': float, 'highest': float}}
        self.trades = []
    
    def buy(self, code: str, price: float, shares: int, reason: str = '') -> bool:
        """Execute buy order"""
        cost = price * shares
        if cost > self.cash:
            return False
        
        self.cash -= cost
        
        if code in self.positions:
            total_shares = self.positions[code]['shares'] + shares
            total_cost = self.positions[code]['shares'] * self.positions[code]['cost'] + cost
            self.positions[code]['shares'] = total_shares
            self.positions[code]['cost'] = total_cost / total_shares
        else:
            self.positions[code] = {
                'shares': shares,
                'cost': price,
                'highest': price,
                'entry_date': datetime.now().isoformat()
            }
        
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
    
    def update_stop_loss(self, code: str, current_price: float) -> Optional[str]:
        """
        更新移动止损
        Returns: action if triggered, None otherwise
        """
        if code not in self.positions:
            return None
        
        pos = self.positions[code]
        cost = pos['cost']
        highest = pos['highest']
        shares = pos['shares']
        
        # Update highest price
        if current_price > highest:
            pos['highest'] = current_price
            highest = current_price
        
        profit_pct = (current_price / cost - 1) * 100
        drawdown_from_high = (current_price - highest) / highest * 100
        
        # 方案B止盈止损规则
        if profit_pct > 50:
            # 盈利>50%: 止盈50%仓位
            return 'take_profit_50'
        elif profit_pct > 30:
            # 盈利>30%: 移动止损-10%
            if drawdown_from_high < -10:
                return 'trailing_stop_10'
        elif profit_pct < -20:
            # 回撤>20%: 减仓50%
            return 'reduce_50'
        elif profit_pct < -30:
            # 回撤>30%: 清仓
            return 'stop_loss'
        
        return None
    
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


if __name__ == '__main__':
    # Test the enhanced analyzer
    analyzer = EnhancedETFAnalyzer()
    
    print("=" * 70)
    print("Enhanced ETF Analyzer - 方案B测试")
    print("=" * 70)
    
    # Test single ETF
    result = analyzer.analyze_etf('510050.SH')
    if 'error' not in result:
        print(f"\n🔹 上证50ETF Analysis:")
        print(f"   现价: {result['current_price']:.3f}")
        print(f"   市场状态: {result['market_regime']}")
        print(f"   推荐策略: {result['recommended_strategy']}")
        print(f"   建议仓位: {result['position_size']*100:.0f}%")
        print(f"   RSI: {result['rsi']:.1f}")
        print(f"   ATR: {result['atr_pct']:.2f}%")
        print(f"   信号: {', '.join(result['signals']) if result['signals'] else '无'}")
    
    # Test portfolio
    print("\n" + "=" * 70)
    print("持仓组合分析:")
    print("=" * 70)
    
    portfolio = analyzer.analyze_portfolio()
    if portfolio['summary']['total_value'] > 0:
        summary = portfolio['summary']
        print(f"   总市值: ¥{summary['total_value']:,.2f}")
        print(f"   总盈亏: ¥{summary['total_profit']:+.2f} ({summary['total_profit_pct']:+.2f}%)")
        
        print("\n   持仓详情:")
        for h in portfolio['holdings']:
            if 'error' not in h:
                print(f"   - {h['name']}: {h['market_regime']} | {h['recommendation']}")
