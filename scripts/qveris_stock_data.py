#!/usr/bin/env python3
"""
QVeris股票数据备用方案
当AKShare连接失败时使用此脚本获取股票数据
"""

import json
import sys
import os
from datetime import datetime

def get_stock_data_via_qveris():
    """
    通过QVeris API获取股票数据（备用方案）
    返回格式与AKShare类似的DataFrame结构
    """
    try:
        # 这里应该调用QVeris API
        # 由于QVeris API需要配置，这里先返回模拟数据
        print("警告：使用模拟数据（需要配置QVeris API）")
        
        # 模拟数据 - 实际应该调用QVeris API
        mock_data = {
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "数据源": "QVeris API (模拟数据)",
            "状态": "备用方案已就绪",
            "说明": "需要配置QVeris API Key并实现实际调用"
        }
        
        return mock_data
        
    except Exception as e:
        print(f"QVeris数据获取失败: {e}")
        return None

def get_eastmoney_data():
    """
    东方财富API备用方案
    使用push2.eastmoney.com接口
    """
    try:
        import requests
        import pandas as pd
        
        # 东方财富实时行情接口
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1,
            "pz": 20,  # 获取20条数据
            "po": 1,
            "np": 1,
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23",
            "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
            "_": str(int(datetime.now().timestamp() * 1000))
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                df = pd.DataFrame(data["data"]["diff"])
                print(f"从东方财富获取到{len(df)}条股票数据")
                return df
        return None
        
    except Exception as e:
        print(f"东方财富API调用失败: {e}")
        return None

def create_akshare_fallback():
    """
    创建AKShare备用方案配置
    """
    config = {
        "数据源优先级": [
            "1. 东方财富API (push2.eastmoney.com)",
            "2. QVeris API (需要配置)",
            "3. 本地缓存数据",
            "4. 模拟数据 (最后手段)"
        ],
        "配置说明": {
            "东方财富API": "稳定可靠，无需API Key",
            "QVeris API": "需要配置QVERIS_API_KEY，提供多市场数据",
            "本地缓存": "使用之前保存的数据文件",
            "模拟数据": "仅用于测试和演示"
        },
        "实施步骤": [
            "1. 修改akshare_analyzer.py，添加备用数据源逻辑",
            "2. 配置QVeris API Key（如果可用）",
            "3. 实现数据源自动切换机制",
            "4. 添加数据缓存功能"
        ]
    }
    
    return config

if __name__ == "__main__":
    print("=" * 60)
    print("AKShare备用数据源方案")
    print("=" * 60)
    
    # 测试东方财富API
    print("\n1. 测试东方财富API...")
    em_data = get_eastmoney_data()
    if em_data is not None:
        print("✅ 东方财富API可用")
    else:
        print("❌ 东方财富API不可用")
    
    # 显示备用方案配置
    print("\n2. 备用方案配置:")
    config = create_akshare_fallback()
    for key, value in config.items():
        print(f"\n{key}:")
        if isinstance(value, list):
            for item in value:
                print(f"  • {item}")
        elif isinstance(value, dict):
            for k, v in value.items():
                print(f"  • {k}: {v}")
    
    print("\n3. 建议实施:")
    print("""
    修改彪哥战法分析器，添加以下逻辑：
    
    def get_market_data():
        try:
            # 首选：AKShare
            return ak.stock_zh_a_spot_em()
        except:
            try:
                # 备用1：东方财富API
                return get_eastmoney_data()
            except:
                try:
                    # 备用2：QVeris API
                    return get_qveris_data()
                except:
                    # 备用3：本地缓存
                    return load_cached_data()
    """)
    
    print("\n✅ 备用数据源方案已创建")
    print(f"配置文件: {os.path.abspath(__file__)}")