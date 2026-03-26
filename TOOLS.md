# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 股票分析工具配置

### AKShare
- **状态**: ✅ 已安装 (v1.18.39)
- **Python环境**: `/home/ubuntu/.openclaw/workspace-stock_analyzer/venv/bin/python`
- **特点**: 免费、无需注册、数据丰富
- **适用场景**: A股实时/历史行情、基本面数据、宏观经济数据

### Tushare
- **Token**: `8bacc6df4a2e60ce93c5ce1aaddfeb14c854da49eb262861f2f57f07`
- **状态**: ✅ 已配置
- **注册时间**: 2026-03-14
- **特点**: 专业金融数据接口，积分制
- **适用场景**: 财务数据、机构持仓、龙虎榜等专业数据

### Stock Monitor Skill (已安装)
- **路径**: `/home/ubuntu/.openclaw/workspace/skills/openclaw-stock-monitor/`
- **来源**: GitHub (duhaipeng/openclaw-stock-monitor)
- **功能**: 
  - A股/港股/美股实时行情
  - 价格突破/涨跌幅提醒
  - 基础技术指标（MA、RSI）
- **使用**: `python3 skills/openclaw-stock-monitor/scripts/stock_check.py`

### 技术指标计算模块 (已扩展)
- **本地路径**: `/home/ubuntu/.openclaw/workspace/skills/openclaw-stock-monitor/scripts/technical_indicators.py`
- **GitHub仓库**: https://github.com/anekin/stock
- **功能**:
  - MA (移动平均线): MA5, MA10, MA20
  - MACD: DIF, DEA, MACD柱状图
  - KDJ: K值, D值, J值
  - BOLL (布林带): 上轨, 中轨, 下轨
  - RSI: RSI(14)
  - 自动买卖信号分析
- **使用**: `python3 technical_indicators.py [股票代码]`
- **文档**: `technical_indicators_README.md`

### QVeris (新增)
- **API Key**: `sk-PB-WKEjgzidzu6K2T4SpJV-c3jcHbvkfRUDKKJUHbAg`
- **状态**: ✅ 已配置
- **Skill路径**: `/home/ubuntu/.openclaw/workspace/skills/qveris-official/`
- **功能**: A股ETF历史数据获取（基于同花顺iFinD）
- **数据源**: 同花顺(THS) iFinD专业金融数据库
- **使用方式**:
  ```bash
  export QVERIS_API_KEY="sk-PB-WKEjgzidzu6K2T4SpJV-c3jcHbvkfRUDKKJUHbAg"
  node scripts/qveris_tool.mjs discover "China A-share ETF historical price data"
  node scripts/qveris_tool.mjs call ths_ifind.history_quotation.v1 --discovery-id <id> --params '{"codes": "510050.SH", "startdate": "20250301", "enddate": "20250323"}'
  ```

### akshare-stock Skill (新增)
- **路径**: `/home/ubuntu/.openclaw/workspace/skills/akshare-stock/`
- **功能**: A股量化数据工具（基于AKShare）
- **使用**: `python3 scripts/stock_cli.py quote`

### ETF Investment Analyzer Skill (新增)
- **路径**: `/home/ubuntu/.openclaw/workspace/skills/etf-investment-analyzer/`
- **包文件**: `/home/ubuntu/.openclaw/workspace/skills/etf-investment-analyzer.skill`
- **功能**: 完整的ETF投资分析系统
  - 多时间框架分析（长期1年+短期1月滚动数据）
  - 技术指标计算（MA, MACD, RSI, KDJ, 布林带）
  - 策略回测和优化
  - 自动每日报告生成
  - 飞书文档集成
- **配置文件**: `references/portfolio_config.json`
- **使用方式**:
  ```python
  from scripts.etf_analyzer import ETFAnalyzer
  analyzer = ETFAnalyzer()
  result = analyzer.analyze_etf('510050.SH')
  report = analyzer.analyze_portfolio()
  ```

### 使用方式
```bash
# 激活虚拟环境
source /home/ubuntu/.openclaw/workspace-stock_analyzer/venv/bin/activate

# 或直接调用
/home/ubuntu/.openclaw/workspace-stock_analyzer/venv/bin/python your_script.py

# Stock Monitor Skill
python3 /home/ubuntu/.openclaw/workspace/skills/openclaw-stock-monitor/scripts/stock_check.py

# QVeris获取A股ETF数据
python3 scripts/fetch_qveris_data.py

# ETF Investment Analyzer
python3 /home/ubuntu/.openclaw/workspace/skills/etf-investment-analyzer/scripts/etf_analyzer.py
```

---

## GitHub API 配置

### GitHub Token
- **状态**: ✅ 已配置
- **路径**: `/home/ubuntu/.openclaw/secrets/github_token.txt`
- **账号**: anekin
- **权限**: 可创建仓库、推送代码、管理Release

### 已安装GitHub相关Skill
- **github-ops**: 已安装于 `/home/ubuntu/.openclaw/workspace/skills/github-ops/`
- **功能**: 创建仓库、推送代码、创建Release、更新README
- **使用**: 通过 `GITHUB_TOKEN` 环境变量自动调用

---

Add whatever helps you do your job. This is your cheat sheet.
