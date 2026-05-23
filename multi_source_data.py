#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彪哥战法多数据源自动切换模块
方案A：腾讯财经 + 新浪财经 + 东方财富
60秒本地缓存，自动切换，最高稳定性
"""

import json
import time
import subprocess
import requests
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

class MultiSourceDataFetcher:
    """多数据源自动切换数据获取器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 60  # 60秒缓存
        self.data_sources = [
            self._fetch_tencent,    # 腾讯财经
            self._fetch_sina,       # 新浪财经  
            self._fetch_eastmoney,  # 东方财富
        ]
    
    def get_stock_data(self, stock_code: str) -> Dict:
        """
        获取股票数据，自动切换数据源
        stock_code格式：上证指数=sh000001，深证成指=sz399001
        """
        # 检查缓存
        cache_key = f"{stock_code}_{int(time.time() // self.cache_duration)}"
        if cache_key in self.cache:
            print(f"使用缓存数据: {stock_code}")
            return self.cache[cache_key]
        
        # 尝试所有数据源
        for source_func in self.data_sources:
            try:
                print(f"尝试数据源: {source_func.__name__}")
                data = source_func(stock_code)
                if data and self._validate_data(data):
                    # 缓存数据
                    self.cache[cache_key] = data
                    print(f"数据源成功: {source_func.__name__}")
                    return data
            except Exception as e:
                print(f"数据源失败 {source_func.__name__}: {e}")
                continue
        
        # 所有数据源都失败
        print("所有数据源均失败，返回空数据")
        return {"error": "所有数据源均失败", "timestamp": datetime.now().isoformat()}
    
    def _fetch_tencent(self, stock_code: str) -> Optional[Dict]:
        """腾讯财经数据源"""
        try:
            # 腾讯财经API
            url = f"http://qt.gtimg.cn/q={stock_code}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                content = response.text
                # 解析腾讯财经格式
                return self._parse_tencent_data(content, stock_code)
        except Exception as e:
            raise Exception(f"腾讯财经失败: {e}")
        return None
    
    def _fetch_sina(self, stock_code: str) -> Optional[Dict]:
        """新浪财经数据源"""
        try:
            # 新浪财经API
            url = f"http://hq.sinajs.cn/list={stock_code}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                content = response.text
                # 解析新浪财经格式
                return self._parse_sina_data(content, stock_code)
        except Exception as e:
            raise Exception(f"新浪财经失败: {e}")
        return None
    
    def _fetch_eastmoney(self, stock_code: str) -> Optional[Dict]:
        """东方财富数据源（使用curl确保稳定性）"""
        try:
            # 使用curl命令，避免Python requests库的连接问题
            if stock_code.startswith("sh"):
                secid = f"1.{stock_code[2:]}"
            elif stock_code.startswith("sz"):
                secid = f"0.{stock_code[2:]}"
            else:
                secid = stock_code
            
            cmd = f'curl -s "http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f43,f57,f58,f169,f170"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                if data.get("rc") == 0 and "data" in data:
                    return self._parse_eastmoney_data(data["data"], stock_code)
        except Exception as e:
            raise Exception(f"东方财富失败: {e}")
        return None
    
    def _parse_tencent_data(self, content: str, stock_code: str) -> Dict:
        """解析腾讯财经数据"""
        # 腾讯财经格式：v_sh000001="1~上证指数~000001~3919.29~-29.26~-0.74~..."
        parts = content.split("=")
        if len(parts) >= 2:
            data_str = parts[1].strip('";')
            fields = data_str.split("~")
            if len(fields) >= 6:
                return {
                    "source": "tencent",
                    "code": stock_code,
                    "name": fields[1],
                    "price": float(fields[3]) if fields[3] else 0,
                    "change": float(fields[4]) if fields[4] else 0,
                    "change_percent": float(fields[5]) if fields[5] else 0,
                    "timestamp": datetime.now().isoformat()
                }
        return {}
    
    def _parse_sina_data(self, content: str, stock_code: str) -> Dict:
        """解析新浪财经数据"""
        # 新浪财经格式：var hq_str_sh000001="上证指数,3919.290,-29.260,-0.74,3919.290,3919.290,...";
        parts = content.split("=")
        if len(parts) >= 2:
            data_str = parts[1].strip('";')
            fields = data_str.split(",")
            if len(fields) >= 4:
                return {
                    "source": "sina",
                    "code": stock_code,
                    "name": fields[0],
                    "price": float(fields[1]) if fields[1] else 0,
                    "change": float(fields[2]) if fields[2] else 0,
                    "change_percent": float(fields[3]) if fields[3] else 0,
                    "timestamp": datetime.now().isoformat()
                }
        return {}
    
    def _parse_eastmoney_data(self, data: Dict, stock_code: str) -> Dict:
        """解析东方财富数据"""
        return {
            "source": "eastmoney",
            "code": stock_code,
            "name": data.get("f58", ""),
            "price": data.get("f43", 0) / 100 if data.get("f43") else 0,
            "change": data.get("f169", 0) / 100 if data.get("f169") else 0,
            "change_percent": data.get("f170", 0) / 100 if data.get("f170") else 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def _validate_data(self, data: Dict) -> bool:
        """验证数据有效性"""
        required_fields = ["price", "change", "change_percent"]
        for field in required_fields:
            if field not in data or data[field] is None:
                return False
        return True
    
    def get_market_indices(self) -> Dict:
        """获取主要市场指数数据"""
        indices = {
            "sh000001": "上证指数",
            "sz399001": "深证成指",
            "sz399006": "创业板指",
        }
        
        results = {}
        for code, name in indices.items():
            try:
                data = self.get_stock_data(code)
                if data and not data.get("error"):
                    results[code] = data
                    print(f"获取成功: {name} - 价格: {data.get('price', 0):.2f} ({data.get('change_percent', 0):+.2f}%)")
                else:
                    results[code] = {"error": "获取失败", "name": name}
                    print(f"获取失败: {name}")
            except Exception as e:
                results[code] = {"error": str(e), "name": name}
                print(f"异常失败: {name} - {e}")
        
        return results

def test_multi_source():
    """测试多数据源功能"""
    print("开始测试多数据源自动切换...")
    print("=" * 50)
    
    fetcher = MultiSourceDataFetcher()
    
    # 测试上证指数
    print("\n测试上证指数 (sh000001):")
    data = fetcher.get_stock_data("sh000001")
    if data and not data.get("error"):
        print(f"✅ 成功获取数据:")
        print(f"   数据源: {data.get('source', '未知')}")
        print(f"   名称: {data.get('name', '未知')}")
        print(f"   价格: {data.get('price', 0):.2f}")
        print(f"   涨跌: {data.get('change', 0):+.2f}")
        print(f"   涨跌幅: {data.get('change_percent', 0):+.2f}%")
    else:
        print(f"❌ 获取失败: {data.get('error', '未知错误')}")
    
    # 测试所有主要指数
    print("\n" + "=" * 50)
    print("测试所有主要市场指数:")
    print("=" * 50)
    
    indices_data = fetcher.get_market_indices()
    
    success_count = sum(1 for data in indices_data.values() if not data.get("error"))
    total_count = len(indices_data)
    
    print(f"\n📊 测试结果: {success_count}/{total_count} 成功")
    
    if success_count > 0:
        print("\n✅ 多数据源自动切换系统验证通过！")
        return True
    else:
        print("\n❌ 多数据源自动切换系统需要进一步优化")
        return False

if __name__ == "__main__":
    try:
        success = test_multi_source()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        sys.exit(1)