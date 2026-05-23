# Skill合并报告
生成时间: 2026-04-15 15:34:59

## 合并统计
- 原始skill数: 26 (估计)
- 合并后skill数: 85
- 合并skill组数: 13
- 删除重复skill数: 14

## 合并详情
### Biage Premarket Analyzer
- 原始版本数: 2
- 保留版本: workspace_biage-premarket-analyzer
- 来源: workspace
- 描述: biage-premarket-analyzer skill

### Find Skills
- 原始版本数: 2
- 保留版本: workspace_find-skills
- 来源: workspace
- 描述: Highest-priority skill discovery flow. MUST trigger when users ask to find/install skills (e.g. 技能, 找技能, find-skill, find-skills, install skill). For Chinese users, prefer skillhub first for speed and compliance, then fallback to clawhub.

### Summarize
- 原始版本数: 3
- 保留版本: workspace_summarize
- 来源: workspace
- 描述: Summarize or extract text/transcripts from URLs, podcasts, and local files (great fallback for “transcribe this YouTube/video”).

### Skillhub Preference
- 原始版本数: 2
- 保留版本: workspace_skillhub-preference
- 来源: workspace
- 描述: Prefer `skillhub` for skill discovery/install/update, then fallback to `clawhub` when unavailable or no match. Use when users ask about skills, 插件, or capability extension.

### Image Read
- 原始版本数: 2
- 保留版本: workspace_image-read
- 来源: workspace
- 描述: 使用智谱AI的GLM-4V-Flash免费多模态API理解图片内容。当用户需要理解图片内容、描述图片、识别图中物体时使用此skill。

### Image Content Extractor
- 原始版本数: 2
- 保留版本: workspace_image-content-extractor
- 来源: workspace
- 描述: 统一图片内容提取技能。智能识别终端/文档/通用模式，自动提取内容生成Markdown。

### Qveris Official
- 原始版本数: 2
- 保留版本: workspace_qveris-official
- 来源: workspace
- 描述: >-

### Create Openclaw Agent
- 原始版本数: 2
- 保留版本: workspace_create-openclaw-agent
- 来源: workspace
- 描述: ** 一键创建新的 OpenClaw agent，包含完整的身份定义、团队集成和配置

### Vision Bot
- 原始版本数: 2
- 保留版本: workspace_vision-bot
- 来源: workspace
- 描述: Analyze images via URL or base64. Auto-detects mode: OCR, object counting, or full description.

### Stock Analysis
- 原始版本数: 2
- 保留版本: workspace_stock-analysis
- 来源: workspace
- 描述: Analyze stocks and cryptocurrencies using Yahoo Finance data. Supports portfolio management, watchlists with alerts, dividend analysis, 8-dimension stock scoring, viral trend detection (Hot Scanner), and rumor/early signal detection. Use for stock analysis, portfolio tracking, earnings reactions, crypto monitoring, trending stocks, or finding rumors before they hit mainstream.

### Data Analyst
- 原始版本数: 2
- 保留版本: workspace_data-analyst
- 来源: workspace
- 描述: Data visualization, report generation, SQL queries, and spreadsheet automation. Transform your AI agent into a data-savvy analyst that turns raw data into actionable insights.

### Vision Tagger
- 原始版本数: 2
- 保留版本: workspace_vision-tagger
- 来源: workspace
- 描述: Tag and annotate images using Apple Vision framework (macOS only). Detects faces, bodies, hands, text (OCR), barcodes, objects, scene labels, and saliency regions. Use for image analysis, photo tagging, posture monitoring, or any task requiring computer vision on images.

### Subagent Driven Development
- 原始版本数: 2
- 保留版本: workspace_subagent-driven-development
- 来源: workspace
- 描述: Use when executing implementation plans with independent tasks in the current session

## 下一步建议
1. 验证重要skill功能正常
2. 清理物理skill目录（如果需要）
3. 定期运行整合脚本保持skill整洁
