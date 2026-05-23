# quant-apply

Unified job application system for quantitative finance internships.
整合多个开源工具，一键海投量化/金融暑期实习。

## Architecture

```
quant-apply/
├── config/               ← 统一配置入口
│   ├── profile.yaml      ← 个人信息
│   ├── search.yaml       ← 搜索条件+目标公司
│   └── platforms/        ← 各平台配置
├── src/
│   ├── cli.py            ← 统一入口
│   ├── platforms/        ← 平台适配器
│   │   ├── boss/         ← Boss直聘 (via boss-agent-cli)
│   │   ├── ats/          ← 海外ATS (via AutoApply)
│   │   └── linkedin/     ← LinkedIn (via jobclaw)
│   └── core/             ← 核心引擎
└── data/                 ← SQLite 投递追踪
```

## Quick Start

```bash
# 1. Setup
bash scripts/setup.sh

# 2. Login
python src/cli.py boss login

# 3. Run
python src/cli.py boss run --city 深圳 --limit 30

# 4. Check stats
python src/cli.py stats
```

## Platform Integrations

| Platform | Tool | Status |
|----------|------|--------|
| Boss直聘 | boss-agent-cli | ✅ |
| 猎聘/51job | Auto-JobHunter | 🚧 |
| Greenhouse/Lever/Workday | AutoApply | 🚧 |
| LinkedIn | jobclaw | 🚧 |
