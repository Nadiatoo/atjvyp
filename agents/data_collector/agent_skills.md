# 数据收集Agent技能配置

## 可用技能列表

### 核心数据收集技能
1. **qveris-official**
   - **功能**: 多市场实时数据查询
   - **权限**: 已授权
   - **使用频率**: 高频
   - **配置状态**: 已安装，需验证API Key

2. **web_fetch**
   - **功能**: 网页内容抓取和解析
   - **权限**: 已授权
   - **使用频率**: 中频
   - **配置状态**: 已安装，可用

3. **agent-reach**
   - **功能**: 社交媒体和新闻平台数据采集
   - **权限**: 已授权
   - **使用频率**: 中频
   - **配置状态**: 已安装，需验证配置

### 数据处理技能
4. **data_processing**
   - **功能**: 数据清洗、转换、分析
   - **权限**: 已授权
   - **使用频率**: 高频
   - **配置状态**: 已安装，可用

### 备用数据源技能
5. **akshare** (通过tushare-finance skill)
   - **功能**: A股历史数据和基础信息
   - **权限**: 已授权
   - **使用频率**: 低频（备用）
   - **配置状态**: 已安装，网络依赖

6. **tushare-finance**
   - **功能**: 专业A股数据接口
   - **权限**: 已授权
   - **使用频率**: 中频
   - **配置状态**: 已安装，需API Key

## 技能使用规范

### 数据采集优先级
1. **首选**: QVeris API (实时性最好，免费额度)
2. **次选**: 东方财富API (A股实时行情)
3. **备用**: Tushare Pro (需API Key，数据全面)
4. **最后**: AkShare (网络依赖，可能不稳定)

### 数据质量要求
1. **实时数据**: 延迟不超过5分钟
2. **历史数据**: 完整无缺失
3. **财务数据**: 经过审计的官方数据
4. **新闻资讯**: 来源可靠，时间准确

### 错误处理策略
1. **主数据源失败**: 自动切换到备用数据源
2. **所有数据源失败**: 记录错误并报告总负责人
3. **数据质量问题**: 标记异常并记录日志
4. **网络超时**: 重试3次，每次间隔5秒

## 技能调用示例

### QVeris API调用示例
```python
# 获取股票实时行情
from qveris import QVerisClient
client = QVerisClient(api_key="YOUR_API_KEY")
stock_data = client.get_stock_quote("AAPL")
```

### 东方财富API调用示例
```python
# 获取A股实时行情
import requests
url = "http://push2.eastmoney.com/api/qt/stock/get"
params = {"secid": "1.000001", "fields": "f43,f57,f58,f169,f170"}
response = requests.get(url, params=params)
data = response.json()
```

### Web内容抓取示例
```python
# 抓取财经新闻
from web_fetch import fetch_content
news = fetch_content("https://finance.sina.com.cn")
```

## 权限配置
- **技能调用**: 允许调用上述所有技能
- **数据存储**: 允许写入`/workspace/data/`目录
- **网络访问**: 允许访问外部API和网站
- **文件访问**: 仅限自身工作区和共享数据目录

## 监控指标
- **技能调用成功率**: 目标≥99%
- **数据采集延迟**: 目标≤5分钟
- **API调用频率**: 符合各平台限制
- **错误率**: 目标≤1%