# A股ETF交易策略回测系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

专业的A股ETF交易策略回测与监控系统，支持12种经典交易策略，覆盖1456只A股ETF。

## 📊 核心功能

- **策略回测**: 12种经典交易策略历史回测
- **ETF监控**: 1456只A股ETF实时监控
- **技术指标**: MA、MACD、RSI、KDJ、布林带等
- **FinClaw集成**: AI量化引擎支持

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行回测

```bash
# 2025年回测
python3 etf_strategy_backtest.py

# 2024年回测 (数据源恢复后)
python3 etf_backtest_2024.py
```

### ETF监控

```bash
# 启动ETF监控
python3 etf_monitor.py --all
```

## 📈 2025年回测结果

| 排名 | 策略 | 收益率 | 最大回撤 | 夏普比率 |
|------|------|--------|----------|----------|
| 1 | Buy&Hold | +35.02% | -13.50% | 1.55 |
| 2 | GoldenCross(MA5/MA20) | +27.88% | -8.64% | 1.56 |
| 3 | ATR_Breakout(14,2) | +24.37% | -9.05% | 1.38 |
| 4 | GoldenCross(MA10/MA60) | +19.21% | -9.49% | 0.96 |
| 5 | MACD(5,35,5) | +18.63% | -6.93% | 1.13 |

## 📁 项目结构

```
.
├── etf_strategy_backtest.py    # 主回测脚本
├── etf_backtest_2024.py        # 2024年回测脚本
├── etf_monitor.py              # ETF监控系统
├── backtest_results.json       # 回测结果数据
├── etf_list.json               # 1456只ETF列表
├── TEST_REPORT.md              # 测试报告
├── BACKTEST_REPORT.md          # 回测详细报告
└── FINCLAW_SKILL_REPORT.md     # FinClaw集成文档
```

## 🛠️ 技术栈

- **Python 3.8+**
- **AKShare**: A股数据源
- **Tushare**: 备用数据源
- **Pandas/NumPy**: 数据处理
- **FinClaw**: AI量化引擎

## 📊 支持策略

### 趋势跟踪
- MACD (标准/快速)
- Golden Cross (MA5/MA20, MA10/MA60)
- ATR Breakout
- Turtle Trading

### 均值回归
- RSI (标准/快速)
- Bollinger Bands
- KDJ

### 其他
- Dual Thrust
- Buy & Hold (基准)

## 📖 文档

- [测试报告](TEST_REPORT.md)
- [回测报告](BACKTEST_REPORT.md)
- [FinClaw集成](FINCLAW_SKILL_REPORT.md)
- [ETF监控说明](ETF_MONITOR_README.md)

## ⚠️ 免责声明

本系统仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。

## 📄 License

MIT License

## 🤝 贡献

欢迎提交Issue和PR！

---

*Created by AnalyzeMaster (📊) - 专业股票分析师*
