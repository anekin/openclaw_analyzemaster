# FinClaw Skill 安装与使用报告

## ✅ 安装状态

**FinClaw v5.1.0** 已成功安装！

- **安装路径**: `/home/ubuntu/.openclaw/workspace/skills/finclaw`
- **Python包**: `finclaw-ai==5.1.0`
- **虚拟环境**: `/home/ubuntu/.openclaw/workspace-stock_analyzer/venv`

---

## 📚 FinClaw 功能概览

### 核心功能

| 功能模块 | 命令 | 说明 |
|----------|------|------|
| **回测引擎** | `finclaw backtest` | 策略回测 |
| **技术分析** | `finclaw analyze` | 技术指标分析 |
| **股票筛选** | `finclaw screen` | 条件选股 |
| **模拟交易** | `finclaw paper` | 纸面交易 |
| **AI策略生成** | `finclaw generate-strategy` | 自然语言生成策略 |
| **MCP服务器** | `finclaw mcp serve` | AI Agent集成 |
| **A2A协议** | `finclaw a2a` | Agent间通信 |

### 内置策略 (15个)

#### 加密货币策略
- `grid-trading` - 网格交易
- `funding-rate` - 资金费率套利
- `dca` - 定投策略
- `btc-cycle` - BTC周期指标

#### 股票策略
- `pairs-trading` - 配对交易
- `sector-rotation` - 行业轮动
- `dividend-harvest` - 股息捕获

#### 通用策略
- `trend-following` - 趋势跟踪
- `breakout` - 突破策略
- `mean-reversion-bb` - 布林带均值回归
- `multi-factor` - 多因子模型
- `vwap` - VWAP回归
- `rsi-divergence` - RSI背离
- `ichimoku` - 一目均衡表
- `momentum-rotation` - 动量轮动

#### YAML DSL策略
- `golden-cross` - 金叉策略
- `rsi-mean-reversion` - RSI均值回归
- `breakout` - 突破策略
- `momentum` - 动量策略
- `value-investing` - 价值投资
- `dividend-aristocrat` - 股息贵族

### 支持的数据源

| 市场 | 数据源 |
|------|--------|
| 美股 | Yahoo Finance, Alpaca, Polygon, Alpha Vantage |
| A股 | AKShare, BaoStock, Tushare |
| 加密货币 | Binance, Bybit, Coinbase, Kraken, OKX |

---

## 🚀 使用示例

### 1. 基础回测
```bash
# 美股回测
finclaw backtest --ticker AAPL --strategy momentum --start 2023-01-01 --end 2024-12-31

# A股回测 (使用AKShare数据源)
finclaw backtest --ticker 510050 --strategy golden-cross --exchange akshare
```

### 2. 技术分析
```bash
finclaw analyze NVDA --indicators rsi,macd,bollinger,sma50
```

### 3. 实时行情
```bash
finclaw quote AAPL,MSFT,NVDA
finclaw quote 510050 --exchange akshare
```

### 4. AI策略生成
```bash
# 用自然语言生成策略
finclaw generate-strategy "buy when RSI < 30 and MACD golden cross, 5% stop loss"

# 中文也支持
finclaw generate-strategy "RSI低于30且MACD金叉时买入，5%止损"
```

### 5. 模拟交易
```bash
# 初始化账户
finclaw paper start --balance 100000

# 买入
finclaw paper buy AAPL 50

# 查看持仓
finclaw paper dashboard

# 运行策略
finclaw paper run-strategy golden-cross --symbols AAPL,MSFT
```

### 6. MCP服务器 (AI Agent集成)
```bash
# 启动MCP服务器
finclaw mcp serve

# 在Claude/Cursor/OpenClaw中配置
{
  "mcpServers": {
    "finclaw": {
      "command": "finclaw",
      "args": ["mcp", "serve"]
    }
  }
}
```

---

## 📊 与之前回测系统的对比

| 特性 | 自建回测脚本 | FinClaw Skill |
|------|--------------|---------------|
| 策略数量 | 12个 | 20+内置策略 |
| AI策略生成 | ❌ | ✅ |
| 多数据源 | AKShare | AKShare/Tushare/Yahoo等 |
| 模拟交易 | ❌ | ✅ |
| MCP/A2A支持 | ❌ | ✅ |
| 风险管理 | 基础 | 完整风控系统 |
| 可视化 | ❌ | 终端图表 |
| 回测报告 | 基础 | QuantStats风格 |

---

## 🔧 当前限制

### 数据源问题
- **AKShare**: 东方财富网站限流，暂时无法获取实时数据
- **解决方案**: 
  1. 等待限流解除
  2. 使用Tushare数据源（需要积分）
  3. 使用本地缓存数据

### 建议的使用方式

#### 方案1: 使用Tushare数据源
```bash
# 配置Tushare Token
export TUSHARE_TOKEN=your_token

# 使用Tushare回测
finclaw backtest --ticker 510050 --exchange tushare --strategy golden-cross
```

#### 方案2: 使用美股数据测试
```bash
# 美股数据稳定可用
finclaw backtest --ticker SPY --strategy momentum --start 2020-01-01
```

#### 方案3: 使用已有数据进行离线回测
```bash
# 使用之前保存的ETF数据
python3 /home/ubuntu/.openclaw/workspace-analyzer_agent/etf_strategy_backtest.py
```

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `/home/ubuntu/.openclaw/workspace/skills/finclaw/` | FinClaw Skill目录 |
| `/home/ubuntu/.openclaw/workspace-analyzer_agent/etf_strategy_backtest.py` | 自建回测脚本 |
| `/home/ubuntu/.openclaw/workspace-analyzer_agent/backtest_results.json` | 回测结果数据 |
| `/home/ubuntu/.openclaw/workspace-analyzer_agent/BACKTEST_REPORT.md` | 回测报告 |

---

## 💡 后续建议

1. **配置Tushare数据源** - 获取更稳定的A股数据
2. **设置定时任务** - 使用cron定时运行策略监控
3. **尝试AI策略生成** - 使用自然语言创建自定义策略
4. **集成MCP服务器** - 让AI Agent直接调用FinClaw功能

---

## 📞 帮助命令

```bash
# 查看所有命令
finclaw --help

# 查看具体命令帮助
finclaw backtest --help
finclaw strategy list

# 系统诊断
finclaw doctor

# 演示模式 (无需API Key)
finclaw demo
```

---

*报告生成时间: 2026-03-21*
