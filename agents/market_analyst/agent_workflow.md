# 盘前分析Agent - 工作流程

## 每日工作流程概览

### 时间线
```
06:00 - 系统自检与预热
07:00 - 数据预加载与准备
07:30 - 初步分析与计算
08:00 - 正式执行盘前分析
08:05 - 生成分析报告
08:08 - 发送报告到飞书
08:10 - 记录执行日志
08:15 - 清理临时文件
22:00 - 每日总结与优化
```

## 详细工作步骤

### 阶段1：系统自检 (06:00-07:00)

#### 1.1 健康检查
```python
def health_check():
    # 检查技能可用性
    check_skill("biage-premarket-analyzer")
    check_skill("qveris-official")
    check_skill("web_search")
    
    # 检查数据源连接
    test_data_source("qveris_api")
    test_data_source("rss_feeds")
    
    # 检查飞书连接
    test_feishu_connection()
    
    # 检查存储空间
    check_disk_space("/Users/tuqibiao/.openclaw/workspace")
    
    return health_status
```

#### 1.2 资源准备
- 清理临时文件
- 准备日志文件
- 加载配置文件
- 初始化分析模型

#### 1.3 权限验证
- 验证技能调用权限
- 验证文件访问权限
- 验证网络访问权限
- 验证时间权限

### 阶段2：数据预加载 (07:00-07:30)

#### 2.1 全球市场数据
```python
def load_global_market_data():
    # 美股收盘数据
    us_stocks = qveris.get_us_market_data()
    
    # 港股数据
    hk_stocks = qveris.get_hk_market_data()
    
    # 日股数据
    jp_stocks = qveris.get_jp_market_data()
    
    # 大宗商品
    commodities = qveris.get_commodity_data()
    
    # 汇率数据
    exchange_rates = qveris.get_exchange_rates()
    
    return {
        "us": us_stocks,
        "hk": hk_stocks,
        "jp": jp_stocks,
        "commodities": commodities,
        "exchange_rates": exchange_rates
    }
```

#### 2.2 新闻资讯收集
```python
def collect_news():
    # 宏观政策新闻
    macro_news = web_search("央行 证监会 政策", count=10)
    
    # 行业动态新闻
    industry_news = web_search("新能源 AI 医药", count=10)
    
    # 国际新闻
    international_news = web_search("美联储 地缘政治", count=10)
    
    # RSS订阅新闻
    rss_news = fetch_rss_feeds()
    
    return {
        "macro": macro_news,
        "industry": industry_news,
        "international": international_news,
        "rss": rss_news
    }
```

#### 2.3 A股昨日数据
```python
def load_a_stock_data():
    # 指数收盘数据
    indices = qveris.get_a_share_indices()
    
    # 涨跌家数
    advance_decline = qveris.get_advance_decline()
    
    # 涨停个股
    limit_up = qveris.get_limit_up_stocks()
    
    # 资金流向
    money_flow = qveris.get_money_flow()
    
    return {
        "indices": indices,
        "advance_decline": advance_decline,
        "limit_up": limit_up,
        "money_flow": money_flow
    }
```

### 阶段3：初步分析 (07:30-08:00)

#### 3.1 季节判断计算
```python
def calculate_season_judgment():
    # 获取历史数据
    historical_data = load_historical_data(days=20)
    
    # 计算技术指标
    technical_indicators = calculate_technical_indicators(historical_data)
    
    # 应用彪哥战法模型
    season_result = biaoge_season_model.predict(technical_indicators)
    
    # 计算评分
    score = calculate_season_score(season_result, technical_indicators)
    
    return {
        "season": season_result,
        "score": score,
        "indicators": technical_indicators
    }
```

#### 3.2 龙头中军筛选
```python
def screen_dragon_and_zhongjun():
    # 获取热门板块
    hot_sectors = qveris.get_hot_sectors()
    
    # 筛选龙头候选
    dragon_candidates = screen_dragon_candidates(hot_sectors)
    
    # 筛选中军候选
    zhongjun_candidates = screen_zhongjun_candidates(hot_sectors)
    
    # 技术面分析
    technical_analysis = analyze_technical_patterns(dragon_candidates + zhongjun_candidates)
    
    # 基本面分析
    fundamental_analysis = analyze_fundamentals(dragon_candidates + zhongjun_candidates)
    
    return {
        "dragon": dragon_candidates[:5],  # 前5名
        "zhongjun": zhongjun_candidates[:5],  # 前5名
        "technical": technical_analysis,
        "fundamental": fundamental_analysis
    }
```

### 阶段4：正式分析 (08:00-08:05)

#### 4.1 执行盘前分析脚本
```bash
# 调用核心分析技能
python3 /Users/tuqibiao/.openclaw/skills/biage-premarket-analyzer/premarket_analysis_v2.py
```

#### 4.2 整合分析结果
```python
def integrate_analysis_results():
    # 整合所有数据
    integrated_data = {
        "global_markets": global_market_data,
        "news": news_data,
        "a_stocks": a_stock_data,
        "season": season_judgment,
        "candidates": dragon_zhongjun_data,
        "timestamp": current_time()
    }
    
    # 生成综合分析
    comprehensive_analysis = generate_comprehensive_analysis(integrated_data)
    
    # 计算仓位建议
    position_suggestion = calculate_position_suggestion(season_judgment)
    
    # 生成风险提示
    risk_warnings = generate_risk_warnings(integrated_data)
    
    return {
        "analysis": comprehensive_analysis,
        "position": position_suggestion,
        "risks": risk_warnings,
        "data": integrated_data
    }
```

### 阶段5：报告生成 (08:05-08:08)

#### 5.1 生成文本报告
```python
def generate_text_report(analysis_results):
    # 报告头部
    report = f"📈 【彪哥战法】盘前消息分析 [{current_time()}]\n"
    report += "━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    # 季节判断
    report += f"🎯 季节判断：{analysis_results['season']['name']}（评分：{analysis_results['season']['score']}分）\n"
    report += f"💰 仓位提醒：{analysis_results['position']}%（基于季节判断）\n\n"
    
    # 全球市场
    report += "🌍 全球市场：\n"
    for market in analysis_results['data']['global_markets']:
        report += f"  {market['name']}: {market['value']} {market['change']}\n"
    
    # 重要新闻
    report += "\n📰 重要新闻：\n"
    for i, news in enumerate(analysis_results['data']['news']['macro'][:3], 1):
        report += f"  {i}. {news['title']}\n"
    
    # 龙头中军
    report += "\n🔥 龙头候选（重点关注）：\n"
    for i, stock in enumerate(analysis_results['data']['candidates']['dragon'], 1):
        report += f"  {i}. {stock['name']}（{stock['code']}） - 逻辑：{stock['logic']}\n"
    
    report += "\n⚓ 中军候选（趋势跟踪）：\n"
    for i, stock in enumerate(analysis_results['data']['candidates']['zhongjun'], 1):
        report += f"  {i}. {stock['name']}（{stock['code']}） - 逻辑：{stock['logic']}\n"
    
    # 策略建议
    report += f"\n💡 盘前策略：{analysis_results['analysis']['strategy']}\n"
    
    # 风险提示
    report += f"⚠️ 风险提示：{analysis_results['risks']}\n"
    
    return report
```

#### 5.2 保存报告文件
```python
def save_report_files(text_report, analysis_data):
    # 保存文本报告
    text_path = f"/Users/tuqibiao/.openclaw/workspace/reports/premarket_{current_date()}.txt"
    save_text_file(text_path, text_report)
    
    # 保存JSON数据
    json_path = f"/Users/tuqibiao/.openclaw/workspace/reports/premarket_{current_date()}.json"
    save_json_file(json_path, analysis_data)
    
    # 保存临时文件（用于调试）
    temp_path = f"/tmp/premarket_report_{current_timestamp()}.txt"
    save_text_file(temp_path, text_report)
    
    return {
        "text": text_path,
        "json": json_path,
        "temp": temp_path
    }
```

### 阶段6：报告发送 (08:08-08:10)

#### 6.1 发送到飞书
```python
def send_to_feishu(report_text, file_paths):
    # 发送文本消息
    message.send(
        channel="feishu",
        to="user:ou_cde15d08540b24715fa99809729cf1be",
        message=report_text
    )
    
    # 记录发送状态
    log_send_status(success=True, timestamp=current_time())
    
    return True
```

#### 6.2 错误处理
```python
def handle_send_error(error, report_text, file_paths):
    # 记录错误
    log_error("发送失败", error)
    
    # 尝试备用发送方式
    try:
        # 保存到本地，等待手动发送
        backup_path = f"/Users/tuqibiao/Desktop/盘前分析_{current_date()}.txt"
        save_text_file(backup_path, report_text)
        
        # 发送错误通知
        send_error_notification(f"盘前分析发送失败，报告已保存到：{backup_path}")
        
        return False
    except Exception as e:
        log_error("备用方案失败", e)
        return False
```

### 阶段7：日志记录 (08:10-08:15)

#### 7.1 执行日志
```python
def record_execution_log():
    log_entry = {
        "date": current_date(),
        "start_time": execution_start_time,
        "end_time": current_time(),
        "duration": calculate_duration(execution_start_time, current_time()),
        "status": "success" if send_success else "partial_success",
        "data_sources": list_used_data_sources(),
        "skills_used": list_used_skills(),
        "report_size": len(report_text),
        "send_status": send_success,
        "errors": list_errors(),
        "warnings": list_warnings()
    }
    
    # 保存到Agent记忆
    save_to_memory("execution_log", log_entry)
    
    # 保存到系统日志
    save_to_system_log("premarket_agent", log_entry)
    
    return log_entry
```

#### 7.2 性能指标
```python
def record_performance_metrics():
    metrics = {
        "data_collection_time": data_collection_duration,
        "analysis_time": analysis_duration,
        "report_generation_time": report_generation_duration,
        "send_time": send_duration,
        "total_time": total_duration,
        "memory_usage": get_memory_usage(),
        "cpu_usage": get_cpu_usage(),
        "disk_usage": get_disk_usage(),
        "network_usage": get_network_usage()
    }
    
    # 保存性能指标
    save_performance_metrics(metrics)
    
    # 检查是否超阈值
    check_performance_thresholds(metrics)
    
    return metrics
```

### 阶段8：清理与优化 (08:15-22:00)

#### 8.1 清理临时文件
```python
def cleanup_temp_files():
    # 清理临时数据文件
    cleanup_directory("/tmp/premarket_*")
    
    # 清理过期的报告文件（保留最近7天）
    cleanup_old_files("/Users/tuqibiao/.openclaw/workspace/reports/", days=7)
    
    # 清理日志文件（保留最近30天）
    cleanup_old_files("/Users/tuqibiao/.openclaw/workspace/logs/", days=30)
    
    return True
```

#### 8.2 每日总结
```python
def daily_summary():
    # 汇总今日执行情况
    summary = {
        "date": current_date(),
        "execution_count": 1,  # 盘前分析每日一次
        "success_rate": 1.0 if send_success else 0.0,
        "average_duration": total_duration,
        "data_quality": assess_data_quality(),
        "report_quality": assess_report_quality(),
        "issues_found": list_issues(),
        "improvements_made": list_improvements(),
        "next_day_plan": generate_next_day_plan()
    }
    
    # 保存每日总结
    save_daily_summary(summary)
    
    # 发送总结报告（可选）
    if need_send_summary():
        send_summary_report(summary)
    
    return summary
```

## 异常处理流程

### 数据获取失败
1. **尝试备用数据源**
2. **使用缓存数据**
3. **标记数据不完整**
4. **记录错误并继续**

### 分析计算错误
1. **简化分析模型**
2. **使用默认值**
3. **标记分析受限**
4. **记录错误并继续**

### 报告生成失败
1. **生成简化报告**
2. **保存原始数据**
3. **标记报告异常**
4. **记录错误并继续**

### 发送失败
1. **重试发送（最多3次）**
2. **保存到本地文件**
3. **发送错误通知**
4. **记录错误状态**

## 质量控制

### 数据质量检查
- 数据完整性检查
- 数据准确性验证
- 数据时效性检查
- 数据一致性检查

### 分析质量检查
- 逻辑正确性检查
- 计算准确性检查
- 结论合理性检查
- 风险覆盖检查

### 报告质量检查
- 格式规范性检查
- 内容完整性检查
- 语言准确性检查
- 重点突出性检查

## 优化机制

### 性能优化
- 数据缓存优化
- 计算算法优化
- 内存使用优化
- 执行时间优化

### 质量优化
- 分析模型优化
- 筛选算法优化
- 报告模板优化
- 错误处理优化

### 用户体验优化
- 报告可读性优化
- 发送时间优化
- 错误提示优化
- 交互体验优化

---
**流程版本**: v1.0  
**创建时间**: 2026-03-16  
**最后更新**: 2026-03-16  
**下次评审**: 2026-03-23