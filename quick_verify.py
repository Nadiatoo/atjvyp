#!/usr/bin/env python3
"""
快速验证修正后的数据源
"""

import urllib.request
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&secids=1.000001,0.399001,0.399006&fields=f12,f13,f14,f2,f3"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        print("✅ API连接成功")
        print(f"📊 获取到{len(data['data']['diff'])}个指数数据")
        
        for item in data['data']['diff']:
            code = item['f12']
            name = item['f14']
            price = item['f2']
            change_pct = item['f3']
            
            # 验证逻辑
            if price <= 0:
                status = "❌ 价格异常"
            elif code == '000001' and (price < 2000 or price > 6000):
                status = "❌ 上证指数范围异常"
            elif code == '399001' and (price < 8000 or price > 20000):
                status = "❌ 深证成指范围异常"
            elif code == '399006' and (price < 1500 or price > 5000):
                status = "❌ 创业板指范围异常"
            else:
                status = "✅ 验证通过"
            
            print(f"{name}({code}): {price} ({change_pct:+.2f}%) - {status}")
            
except Exception as e:
    print(f"❌ 验证失败: {e}")