#!/usr/bin/env python3
"""
简化测试 - 验证东方财富数据源可用性
"""

import urllib.request
import json
import ssl
from datetime import datetime

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

def test_eastmoney_api():
    """测试东方财富API可用性"""
    print("🔍 测试东方财富API可用性...")
    
    # 测试URL：获取上证指数、深证成指、创业板指
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&secids=1.000001,0.399001,0.399006&fields=f12,f13,f14,f2,f3"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://quote.eastmoney.com/'
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if 'data' in data and 'diff' in data['data']:
                indices = data['data']['diff']
                print(f"✅ API测试成功，获取到{len(indices)}个指数数据")
                
                print("\n📊 实时指数数据:")
                for item in indices:
                    code = item.get('f12', '')
                    name = item.get('f14', '')
                    price = item.get('f2', 0)
                    change_pct = item.get('f3', 0)
                    print(f"  • {name}({code}): {price} ({change_pct:+.2f}%)")
                
                # 数据验证
                is_valid = True
                for item in indices:
                    price = item.get('f2', 0)
                    change_pct = item.get('f3', 0)
                    
                    if price <= 0:
                        print(f"❌ 数据异常: {item.get('f14')}价格={price}")
                        is_valid = False
                    if abs(change_pct) > 20:
                        print(f"⚠️ 数据警告: {item.get('f14')}涨跌幅={change_pct}%")
                
                if is_valid:
                    print("\n🎯 数据验证: 通过")
                    return True
                else:
                    print("\n⚠️ 数据验证: 部分异常")
                    return False
            else:
                print("❌ API返回数据结构异常")
                return False
                
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

def test_market_stats():
    """测试市场统计数据获取"""
    print("\n🔍 测试市场统计数据...")
    
    # 尝试获取板块数据
    url = "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5&po=1&np=1&fltt=2&invt=2&fs=b:BK0425+f:!50&fields=f12,f13,f14,f2,f3"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if 'data' in data and 'diff' in data['data']:
                sectors = data['data']['diff']
                print(f"✅ 获取到{len(sectors)}个板块数据")
                
                print("\n📈 板块表现前5:")
                for i, item in enumerate(sectors[:5], 1):
                    name = item.get('f14', '')
                    change_pct = item.get('f3', 0)
                    print(f"  {i}. {name}: {change_pct:+.2f}%")
                
                return True
            else:
                print("❌ 板块数据结构异常")
                return False
                
    except Exception as e:
        print(f"❌ 板块数据获取失败: {e}")
        return False

def main():
    print("=" * 60)
    print("东方财富数据源可用性测试")
    print("=" * 60)
    
    # 记录开始时间
    start_time = datetime.now()
    
    # 1. 测试指数API
    api_ok = test_eastmoney_api()
    
    # 2. 测试板块数据
    stats_ok = test_market_stats()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"  指数API: {'✅ 通过' if api_ok else '❌ 失败'}")
    print(f"  板块数据: {'✅ 通过' if stats_ok else '❌ 失败'}")
    
    if api_ok and stats_ok:
        print("\n🎉 所有测试通过！东方财富数据源可用")
        print("💡 建议: 立即将此数据源集成到彪哥战法系统")
    elif api_ok:
        print("\n⚠️ 部分测试通过，指数数据可用")
        print("💡 建议: 先集成指数数据，再完善其他数据")
    else:
        print("\n❌ 主要测试失败，需要寻找替代数据源")
    
    # 显示测试耗时
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n⏱️ 测试耗时: {elapsed:.2f}秒")
    print("=" * 60)

if __name__ == "__main__":
    main()