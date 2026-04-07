# MEMORY.md - 长期记忆

## 我的身份
- **名字**: AnalyzeMaster
- **角色**: AI分析助手
- **专长**: 新闻分析、趋势判断、数据洞察、股票分析
- **风格**: 沉着、冷静、理性
- **Emoji**: 📊

## 关于我的用户（老板）
- 需要新闻分析和趋势判断方面的帮助
- 偏好简洁、理性的分析风格
- 时区: Asia/Shanghai (GMT+8)

## 股票分析能力

### 数据源配置（已就绪）
- **AKShare**: 已安装 (v1.18.39)，免费数据源
- **Tushare**: 已配置Token，积分制专业数据
- **Python环境**: `/home/ubuntu/.openclaw/workspace-stock_analyzer/venv/`

### 已安装Skill
- **stock-monitor**: GitHub开源Skill (duhaipeng/openclaw-stock-monitor)
  - 功能: A股/港股/美股实时行情、价格提醒、MA/RSI指标
  - 路径: `/home/ubuntu/.openclaw/workspace/skills/openclaw-stock-monitor/`

### 已掌握技能
1. 获取个股历史K线数据
2. 获取个股实时行情
3. 获取股票基本信息
4. 获取指数历史行情
5. 实时行情监控（基于stock-monitor Skill）

### 学习计划（2026-03-20制定）
- **第一阶段**: 技术指标计算（MA、MACD、RSI、KDJ、布林带）
- **第二阶段**: 财报分析能力（PE、PB、ROE、现金流）
- **第三阶段**: 量化策略回测
- **第四阶段**: 机器学习预测模型

## 重要事件记录

### 2026-03-15
- 首次与老板对话
- 分析了 159227 华夏国证航天航空行业ETF
- 验证了跨agent通信功能（与main agent、stock_analyzer通信）
- 发现系统中其他agent：main、rtl_agent、stock_analyzer
- 确认各agent的memory文件是独立的，不自动共享

### 2026-03-17
- 安装了STDF解析工具（pystdf库）
- 创建了STDF查看器脚本 `stdf_tool.py`
- 搭建了FTP服务器（vsftpd）用于文件上传
- 建立了任务记录机制（每日记忆文件）

### 2026-03-20
- 确认股票分析数据源配置（AKShare + Tushare）
- 制定股票分析能力提升计划
- 更新TOOLS.md记录数据源信息

## 系统认知
- OpenClaw多agent架构
- 可以通过sessions_send与其他agent通信
- 每个agent有独立的workspace和memory
- 可以显式读取其他agent的文件路径

## 语音交互能力（2026-04-07新增）

### 已安装Skills
- **feishu-voice-message**: 文字转语音消息（带波形图）
- **openai-whisper**: 本地语音识别（免费，准确度中等）
- **speech-recognition**: 硅基流动API语音识别（中文优化，准确度高）

### 配置信息
- 硅基流动API Key: 已配置
- 免费额度: 14元（约2000万Token）
- FFmpeg: 已安装（音频格式转换）

### 使用方式
- 🎙️ 发送语音消息 → 自动转文字
- 🔊 文字生成语音 → 发送飞书语音消息

## 待办/想法
- [ ] 学习技术指标计算
- [ ] 建立个股分析模板
- [ ] 实现自动化财报分析
- [ ] 探索量化策略
- [ ] 监控硅基流动API用量

## 偏好与边界
- 保持简洁、数据驱动的分析风格
- 不主动泄露用户隐私信息
- 不确定时先询问再行动

## 老板的沟通偏好（2026-04-07更新）
**重要**: 当老板的指令模棱两可、不够直接时，我应该：
1. 直接询问具体指令是什么
2. 或者提供几个选项让老板确认

**不要**: 猜测或假设老板的意图
