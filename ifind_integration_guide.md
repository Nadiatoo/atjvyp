# iFinD API 集成指南

## 📋 目录
1. [安全配置](#安全配置)
2. [环境设置](#环境设置)
3. [连接测试](#连接测试)
4. [API调用示例](#api调用示例)
5. [替换现有数据源](#替换现有数据源)
6. [故障排除](#故障排除)

## 🔐 安全配置

### 重要安全原则
- ✅ **永远不要**在代码中硬编码token
- ✅ **永远不要**提交token到版本控制
- ✅ **使用环境变量**或安全的配置存储
- ✅ **定期刷新**access_token
- ✅ **监控**API使用量

### 已提供的Refresh Token
你的Refresh Token已提供（JWT格式）：
- 用户ID: `862900073`
- 刷新过期时间: `2026-05-20 16:37:03`
- Token格式: JWT (header.payload.signature)

## 🛠️ 环境设置

### 方法一：临时环境变量
```bash
# 1. 设置环境变量
export IFIND_REFRESH_TOKEN="eyJzaWduX3RpbWUiOiIyMDI2LTA0LTIwIDE3OjQ2OjU2In0=.eyJ1aWQiOiI4NjI5MDAwNzMiLCJ1c2VyIjp7InJlZnJlc2hUb2tlbkV4cGlyZWRUaW1lIjoiMjAyNi0wNS0yMCAxNjozNzowMyIsInVzZXJJZCI6Ijg2MjkwMDA3MyJ9fQ==.3CF5C8F32F6F9B854BFFAF1DD4771664AE4EFBECB9EB6AA4B06EBBCAFC7B69D6"

# 2. 运行设置脚本
bash /Users/tuqibiao/.openclaw/workspace/setup_ifind_env.sh
```

### 方法二：永久环境变量
```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
echo 'export IFIND_REFRESH_TOKEN="你的refresh_token"' >> ~/.zshrc
echo 'export IFIND_ACCESS_TOKEN="你的access_token"' >> ~/.zshrc
source ~/.zshrc
```

### 方法三：使用配置文件（推荐）
创建 `~/.openclaw/ifind_config.json`：
```json
{
  "refresh_token": "你的refresh_token",
  "access_token": "你的access_token",
  "base_url": "https://quantapi.10jqka.com.cn"
}
```

## 🔌 连接测试

### 第一步：测试环境变量
```bash
# 检查环境变量
echo $IFIND_REFRESH_TOKEN | head -c 50
```

### 第二步：运行连接测试
```bash
# 测试完整连接
python3 /Users/tuqibiao/.openclaw/workspace/test_ifind_connection.py
```

### 预期结果
```
✅ iFinD API 连接测试通过
```

## 📡 API调用示例

### 1. 刷新Access Token
```python
import requests

def refresh_ifind_token(refresh_token):
    """使用refresh_token获取access_token"""
    url = "https://quantapi.10jqka.com.cn/oauth2/refresh_token"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("access_token")
    return None
```

### 2. 获取股票数据
```python
def get_stock_quote(access_token, symbol="000001"):
    """获取股票行情"""
    url = "https://quantapi.10jqka.com.cn/api/v1/stock/quote"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "symbol": symbol,
        "fields": "symbol,name,last_close,open,high,low,volume,amount"
    }
    
    response = requests.get(url, headers=headers, params=params)
    return response.json() if response.status_code == 200 else None
```

### 3. 获取市场数据
```python
def get_market_data(access_token):
    """获取市场概况"""
    url = "https://quantapi.10jqka.com.cn/api/v1/market/overview"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None
```

## 🔄 替换现有数据源

### 步骤1：创建iFinD数据获取类
```python
# ifind_data_fetcher.py
import os
import requests
from datetime import datetime

class IFindDataFetcher:
    def __init__(self):
        self.refresh_token = os.getenv("IFIND_REFRESH_TOKEN")
        self.access_token = None
        self.base_url = "https://quantapi.10jqka.com.cn"
        
    def _refresh_access_token(self):
        """刷新access_token"""
        # 实现token刷新逻辑
        pass
    
    def get_main_indices(self):
        """获取主要指数 - 替换东方财富版本"""
        # 实现iFinD版本
        pass
    
    def get_market_overview(self):
        """获取市场概况"""
        pass
    
    def get_stock_ranking(self):
        """获取股票排行"""
        pass
```

### 步骤2：修改彪哥战法脚本
```python
# biage_premarket_ifind.py (iFinD版本)
from ifind_data_fetcher import IFindDataFetcher

class BiagePremarketIFind:
    def __init__(self):
        self.fetcher = IFindDataFetcher()
        
    def run_analysis(self):
        """运行盘前分析"""
        # 使用iFinD数据源
        indices = self.fetcher.get_main_indices()
        market_data = self.fetcher.get_market_overview()
        # ... 其他分析逻辑
```

### 步骤3：更新定时任务
修改 `HEARTBEAT.md` 中的执行命令：
```bash
# 从
python3 /Users/tuqibiao/.openclaw/workspace/biage_premarket_eastmoney.py 2>&1

# 改为
python3 /Users/tuqibiao/.openclaw/workspace/biage_premarket_ifind.py 2>&1
```

## 🚀 快速开始

### 立即测试
```bash
# 1. 设置环境变量
export IFIND_REFRESH_TOKEN="你的token"

# 2. 测试连接
python3 /Users/tuqibiao/.openclaw/workspace/test_ifind_connection.py

# 3. 如果成功，创建iFinD版本的彪哥战法
cp /Users/tuqibiao/.openclaw/workspace/biage_premarket_eastmoney.py \
   /Users/tuqibiao/.openclaw/workspace/biage_premarket_ifind.py
```

### 分阶段迁移
1. **第一阶段**：测试连接，验证token有效性
2. **第二阶段**：创建基础数据获取类
3. **第三阶段**：替换关键数据获取函数
4. **第四阶段**：全面替换并测试

## 🔧 故障排除

### 常见问题

#### Q1: Token无效或过期
```
❌ 刷新失败，状态码: 401
```
**解决方案**：
1. 重新登录网页版获取新token
2. 检查token格式是否正确
3. 确认账号权限

#### Q2: API调用返回空数据
```
✅ API连接成功，但数据为空
```
**解决方案**：
1. 检查API端点是否正确
2. 确认请求参数
3. 查看iFinD文档中的示例

#### Q3: 网络连接问题
```
❌ 网络请求失败: timed out
```
**解决方案**：
1. 检查网络连接
2. 增加请求超时时间
3. 添加重试机制

### 调试工具
```python
# debug_ifind.py
import requests
import json

# 打印完整请求和响应
response = requests.get(url, headers=headers)
print(f"URL: {url}")
print(f"Headers: {headers}")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")
```

## 📞 支持与资源

### iFinD官方资源
- **接口官网**: https://quantapi.10jqka.com.cn
- **文档中心**: https://quantapi.10jqka.com.cn/?page=helpCenter
- **技术支持**: 952555

### 本地文件参考
- `数据接口环境部署说明.pdf` - 详细部署指南
- `同花顺iFind-MCP产品介绍.pdf` - MCP集成方案
- `数据接口网页版超级命令介绍.docx` - 网页版工具使用

## ✅ 下一步行动

根据你的优先级选择：

### 选项A：快速测试（推荐）
1. 运行测试脚本确认连接
2. 获取一次数据验证质量
3. 决定是否继续集成

### 选项B：完整替换
1. 创建iFind数据获取类
2. 逐功能替换东方财富API
3. 并行运行测试对比数据质量

### 选项C：混合方案
1. iFind用于关键数据（财务报表等）
2. 东方财富用于实时行情
3. 逐步迁移

---

**已准备就绪**：
- ✅ 安全配置模板
- ✅ 连接测试脚本
- ✅ 环境设置脚本
- ✅ 集成指南文档

**需要你**：
- 🔑 确认token有效性
- 🎯 选择集成方案
- ⏰ 安排实施时间

**回复你的选择，我可以立即开始相应的工作。**