# A股ETF监控系统

## 配置完成 ✅

### 监控范围
- **总数**: 1456 只A股ETF
- **类型**: 涵盖行业ETF、宽基ETF、商品ETF、债券ETF等
- **数据源**: 腾讯财经API

### 文件说明

| 文件 | 说明 |
|------|------|
| `etf_list.json` | 1456只ETF完整列表（代码+名称） |
| `etf_monitor_config.json` | 监控配置文件 |
| `etf_monitor.py` | ETF批量监控脚本 |

### 使用方法

#### 1. 快速监控（默认50只）
```bash
cd /home/ubuntu/.openclaw/workspace-analyzer_agent
python3 etf_monitor.py
```

#### 2. 监控所有ETF
```bash
python3 etf_monitor.py --all
```

#### 3. 自定义参数
```bash
# 监控100只，阈值1.5%
python3 etf_monitor.py --batch 100 --threshold 1.5

# 监控所有，阈值5%
python3 etf_monitor.py --all --threshold 5.0
```

### 提醒规则

- **默认阈值**: 涨跌幅超过 ±3%
- **提醒方式**: 控制台输出
- **监控频率**: 可配合 cron 定时执行

### 注意事项

⚠️ **今天是周末（周六），A股休市，无法获取实时数据**

请在交易日（周一至周五 9:30-15:00）运行监控脚本。

### ETF分类示例

| 类型 | 示例代码 | 名称 |
|------|----------|------|
| 宽基指数 | 510050 | 上证50ETF |
| 行业主题 | 159995 | 芯片ETF |
| 商品期货 | 159985 | 豆粕ETF |
| 债券 | 159972 | 5年地债ETF |
| 跨境 | 159960 | 恒生中国企业ETF |

### 自动化建议

可以添加 cron 任务实现定时监控：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（交易日每30分钟监控一次）
*/30 9-15 * * 1-5 cd /home/ubuntu/.openclaw/workspace-analyzer_agent && python3 etf_monitor.py --all >> /tmp/etf_monitor.log 2>&1
```

### 更新记录

- 2026-03-21: 初始配置，导入1456只A股ETF
