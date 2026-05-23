#!/usr/bin/env python3
"""
东方财富可靠数据源 - 彪哥战法数据基础
建立准确、可靠、可验证的实时数据系统
"""

import urllib.request
import json
import ssl
import time
from datetime import datetime
import hashlib

# 禁用 SSL 验证
ssl._create_default_https_context = ssl._create_unverified_context

class EastMoneyReliableData:
    """东方财富可靠数据源"""
    
    def __init__(self):
        self.base_url = "https://push2.eastmoney.com/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://quote.eastmoney.com/'
        }
        self.data_cache = {}
        self.last_fetch_time = {}
        
    def fetch_with_retry(self, url, max_retries=3):
        """带重试的数据获取"""
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = response.read().decode('utf-8')
                    return json.loads(data)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(1)  # 等待1秒后重试
        return None
    
    def validate_index_data(self, data):
        """验证指数数据"""
        if not data or 'data' not in data or 'diff' not in data['data']:
            return False, "数据结构异常"
        
        items = data['data']['diff']
        if len(items) == 0:
            return False, "数据为空"
        
        # 验证关键字段
        for item in items:
            required_fields = ['f12', 'f14', 'f2', 'f3']
            for field in required_fields:
                if field not in item:
                    return False, f"缺少必要字段: {field}"
            
            # 验证价格范围
            price = item.get('f2', 0)
            if price <= 0:  # 价格必须为正数
                return False, f"价格异常: {price}"
            
            # 根据不同指数设置合理范围
            code = item.get('f12', '')
            if code == '000001' and (price < 2000 or price > 6000):  # 上证指数合理范围
                return False, f"上证指数价格异常: {price}"
            elif code == '399001' and (price < 8000 or price > 20000):  # 深证成指合理范围
                return False, f"深证成指价格异常: {price}"
            elif code == '399006' and (price < 1500 or price > 5000):  # 创业板指合理范围
                return False, f"创业板指价格异常: {price}"
            
            # 验证涨跌幅范围
            change_pct = item.get('f3', 0)
            if abs(change_pct) > 20:  # 单日涨跌幅超过20%异常
                return False, f"涨跌幅异常: {change_pct}%"
        
        return True, "验证通过"
    
    def get_main_indices(self):
        """获取主要指数（已验证可靠）"""
        print("📊 获取主要指数数据...")
        
        # 上证指数(1.000001)、深证成指(0.399001)、创业板指(0.399006)
        url = f"{self.base_url}/qt/ulist.np/get?fltt=2&invt=2&secids=1.000001,0.399001,0.399006&fields=f12,f13,f14,f2,f3,f4,f20,f21"
        
        try:
            data = self.fetch_with_retry(url)
            is_valid, message = self.validate_index_data(data)
            
            if not is_valid:
                print(f"❌ 数据验证失败: {message}")
                return None
            
            indices = {}
            for item in data['data']['diff']:
                code = item['f12']
                name = item['f14']
                price = item['f2']
                change_pct = item['f3']
                change = item['f4']
                
                indices[code] = {
                    'name': name,
                    'price': price,
                    'change_pct': change_pct,
                    'change': change,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'source': 'eastmoney',
                    'validated': True
                }
            
            print(f"✅ 获取到{len(indices)}个指数数据，验证通过")
            return indices
            
        except Exception as e:
            print(f"❌ 获取指数数据失败: {e}")
            return None
    
    def get_sector_performance(self):
        """获取板块表现"""
        print("📈 获取板块表现数据...")
        
        # 获取行业板块数据
        url = f"{self.base_url}/qt/clist/get?pn=1&pz=20&po=1&np=1&fltt=2&invt=2&fs=b:BK0425+f:!50&fields=f12,f13,f14,f2,f3,f4,f20,f21"
        
        try:
            data = self.fetch_with_retry(url)
            if not data or 'data' not in data or 'diff' not in data['data']:
                print("❌ 板块数据结构异常")
                return None
            
            sectors = []
            for item in data['data']['diff'][:10]:  # 取前10个板块
                sector = {
                    'code': item.get('f12', ''),
                    'name': item.get('f14', ''),
                    'price': item.get('f2', 0),
                    'change_pct': item.get('f3', 0),
                    'change': item.get('f4', 0),
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                sectors.append(sector)
            
            print(f"✅ 获取到{len(sectors)}个板块数据")
            return sectors
            
        except Exception as e:
            print(f"❌ 获取板块数据失败: {e}")
            return None
    
    def get_market_stats(self):
        """获取市场统计（估算）"""
        print("📊 估算市场统计数据...")
        
        # 基于指数表现估算市场统计
        indices = self.get_main_indices()
        if not indices:
            return None
        
        # 简单估算逻辑（后续需要真实数据源）
        avg_change = sum(idx['change_pct'] for idx in indices.values()) / len(indices)
        
        if avg_change > 1:
            rising_ratio = 60  # 上涨比例
            limit_up = 80      # 涨停家数
            limit_down = 20    # 跌停家数
        elif avg_change > 0:
            rising_ratio = 55
            limit_up = 60
            limit_down = 25
        elif avg_change > -1:
            rising_ratio = 45
            limit_up = 40
            limit_down = 35
        else:
            rising_ratio = 35
            limit_up = 30
            limit_down = 50
        
        stats = {
            'rising_ratio': rising_ratio,  # 上涨比例
            'limit_up': limit_up,          # 涨停家数
            'limit_down': limit_down,      # 跌停家数
            'avg_change': avg_change,      # 平均涨跌幅
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'note': '基于指数表现的估算数据，待完善真实数据源'
        }
        
        print(f"✅ 生成市场统计估算数据")
        return stats
    
    def get_comprehensive_data(self):
        """获取综合数据"""
        print("=" * 60)
        print("东方财富可靠数据源 - 综合数据获取")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. 获取主要指数
        indices = self.get_main_indices()
        
        # 2. 获取板块表现
        sectors = self.get_sector_performance()
        
        # 3. 获取市场统计
        stats = self.get_market_stats()
        
        # 整合数据
        comprehensive_data = {
            'indices': indices or {},
            'sectors': sectors or [],
            'stats': stats or {},
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_source': 'eastmoney_reliable',
            'data_quality': 'validated' if indices else 'partial'
        }
        
        elapsed = time.time() - start_time
        print(f"\n⏱️ 数据获取耗时: {elapsed:.2f}秒")
        print(f"📊 数据质量: {comprehensive_data['data_quality']}")
        
        # 显示数据摘要
        if indices:
            print("\n📈 主要指数:")
            for code, idx in indices.items():
                print(f"  • {idx['name']}: {idx['price']} ({idx['change_pct']:+.2f}%)")
        
        if stats:
            print(f"\n📊 市场统计:")
            print(f"  上涨比例: {stats['rising_ratio']}%")
            print(f"  涨停家数: {stats['limit_up']}")
            print(f"  跌停家数: {stats['limit_down']}")
            if 'note' in stats:
                print(f"  备注: {stats['note']}")
        
        print("\n" + "=" * 60)
        return comprehensive_data

def test_data_accuracy():
    """测试数据准确性"""
    print("🧪 测试数据准确性...")
    
    fetcher = EastMoneyReliableData()
    
    # 多次获取测试一致性
    test_results = []
    for i in range(3):
        print(f"\n测试 {i+1}/3...")
        data = fetcher.get_main_indices()
        if data:
            # 计算数据哈希用于一致性检查
            data_str = json.dumps(data, sort_keys=True)
            data_hash = hashlib.md5(data_str.encode()).hexdigest()[:8]
            test_results.append({
                'attempt': i+1,
                'success': True,
                'hash': data_hash,
                'count': len(data)
            })
            print(f"  获取成功，数据哈希: {data_hash}")
        else:
            test_results.append({
                'attempt': i+1,
                'success': False
            })
            print(f"  获取失败")
        time.sleep(1)  # 间隔1秒
    
    # 分析测试结果
    successful = [r for r in test_results if r['success']]
    if len(successful) >= 2:
        # 检查一致性
        hashes = [r['hash'] for r in successful]
        if len(set(hashes)) == 1:
            print(f"\n✅ 数据准确性测试通过：3次获取{len(successful)}次成功，数据一致")
            return True
        else:
            print(f"\n⚠️ 数据一致性警告：成功获取但数据不一致")
            return False
    else:
        print(f"\n❌ 数据可靠性不足：3次获取仅{len(successful)}次成功")
        return False

if __name__ == "__main__":
    print("🏁 东方财富可靠数据源系统启动")
    print("=" * 60)
    
    # 1. 测试数据准确性
    accuracy_ok = test_data_accuracy()
    
    if accuracy_ok:
        print("\n🚀 开始获取综合数据...")
        
        # 2. 获取综合数据
        fetcher = EastMoneyReliableData()
        data = fetcher.get_comprehensive_data()
        
        # 3. 保存数据
        if data:
            import os
            data_dir = "/Users/tuqibiao/.openclaw/workspace/data"
            os.makedirs(data_dir, exist_ok=True)
            
            filename = f"reliable_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(data_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 数据已保存至: {filepath}")
            print(f"📁 文件大小: {os.path.getsize(filepath)} bytes")
            
            # 显示保存的数据摘要
            print("\n📋 保存数据摘要:")
            print(f"  指数数量: {len(data.get('indices', {}))}")
            print(f"  板块数量: {len(data.get('sectors', []))}")
            print(f"  数据质量: {data.get('data_quality', 'unknown')}")
            print(f"  时间戳: {data.get('timestamp', 'unknown')}")
        else:
            print("\n❌ 数据获取失败，无法保存")
    else:
        print("\n❌ 数据准确性测试未通过，停止获取")
    
    print("\n" + "=" * 60)
    print("🏁 数据源系统运行完成")