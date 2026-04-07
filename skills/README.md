# Skills 目录备份清单

本目录包含已安装的 OpenClaw Skills，用于快速恢复环境。

## 已安装 Skills (15个)

### 🎙️ 语音交互 (4个)
| Skill | 来源 | 功能 |
|-------|------|------|
| edge-tts | clawhub | TTS依赖库 |
| feishu-voice-message | clawhub | 飞书语音消息生成 |
| openai-whisper | clawhub | 本地语音识别 |
| speech-recognition | clawhub | 硅基流动API语音识别 |

### 📊 股票分析 (4个)
| Skill | 来源 | 功能 |
|-------|------|------|
| etf-daily-report | 本地 | ETF交易日报自动生成 |
| etf-investment-analyzer | 本地 | ETF投资分析、技术指标、策略回测 |
| stock-data-downloader | 本地 | 股票数据下载 |
| stock-data-hub | 本地 | 多源股票数据获取 |

### 🔍 搜索与信息 (3个)
| Skill | 来源 | 功能 |
|-------|------|------|
| find-skills-skill | clawhub | 搜索发现OpenClaw技能 |
| multi-search-engine | clawhub | 17个搜索引擎集成 |
| openclaw-tavily-search | clawhub | Tavily API网页搜索 |

### 🤖 系统与自动化 (2个)
| Skill | 来源 | 功能 |
|-------|------|------|
| ke-office-automation | clawhub | Excel/Word/文件批量处理 |
| memory-setup-openclaw | clawhub | 记忆系统配置 |

### 🧠 自我提升 (1个)
| Skill | 来源 | 功能 |
|-------|------|------|
| self-improve | clawhub | 自动学习改进，每3天运行 |

### 📦 包文件 (1个)
| 文件 | 说明 |
|------|------|
| etf-investment-analyzer.skill | ETF分析器打包文件 |

## 恢复方法

### 从 ClawHub 安装
```bash
# 语音交互
npx clawhub install edge-tts --force
npx clawhub install feishu-voice-message --force
npx clawhub install openai-whisper --force
npx clawhub install speech-recognition --force

# 搜索
npx clawhub install find-skills-skill --force
npx clawhub install multi-search-engine --force
npx clawhub install openclaw-tavily-search --force

# 系统与自动化
npx clawhub install ke-office-automation --force
npx clawhub install memory-setup-openclaw --force

# 自我提升
npx clawhub install self-improve --force
```

### 本地 Skills
本地开发的 skills 需要从源码恢复：
- etf-daily-report/
- etf-investment-analyzer/
- stock-data-downloader/
- stock-data-hub/

## 注意事项
1. 部分 skills 可能需要额外配置（如 API Key）
2. 安装后检查 SKILL.md 了解具体使用方法
3. 某些 skills 可能有系统依赖（如 FFmpeg）

---
**最后更新**: 2026-04-07
**备份目的**: 数字分身复活时使用
