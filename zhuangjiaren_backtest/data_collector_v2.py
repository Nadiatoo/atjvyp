#!/usr/bin/env python3
"""
庄稼人战法 - 增强版数据采集模块
使用akshare库获取A股市场历史数据（修复版）
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import time

class DataCollector:
    """数据采集器"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def get_index_data(self, start_date="20210101", end_date="20251231"):
        """获取主要指数数据 - 使用正确的akshare API"""
        indices = {
            "上证指数": "000001",
            "深证成指": "399001", 
            "创业板指": "399006",
            "沪深300": "000300",
            "中证1000": "000852"
        }
        
        result = {}
        for name, code in indices.items():
            try:
                # 使用正确的API
                df = ak.index_zh_a_hist(symbol=code, period="daily", 
                                        start_date=start_date, end_date=end_date)
                if df is not None and len(df) > 0:
                    df['日期'] = pd.to_datetime(df['日期'])
                    result[name] = df
                    print(f"✓ 获取{name}数据: {len(df)}条")
                    # 保存单个文件
                    df.to_csv(f"{self.data_dir}/index_{name}.csv", index=False, encoding='utf-8-sig')
                else:
                    print(f"✗ 获取{name}返回空数据")
            except Exception as e:
                print(f"✗ 获取{name}失败: {e}")
            time.sleep(0.5)  # 避免请求过快
                
        return result
    
    def get_sector_board_data(self):
        """获取概念板块历史数据"""
        # 主要概念板块（根据战法可能的主线板块）
        key_sectors = {
            # 2021主线
            "锂电池": "BK0577",
            "光伏": "BK0531",
            "新能源车": "BK0579",
            "有色": "BK0548",
            "化工": "BK0532",
            "煤炭": "BK0543",
            "钢铁": "BK0539",
            # 2022主线  
            "新冠药物": "BK1065",
            "基建": "BK0423",
            "房地产": "BK0451",
            "医药": "BK0465",
            # 2023主线
            "AI": "BK0559",
            "ChatGPT": "BK1064",
            "半导体": "BK0539",
            "传媒": "BK0486",
            "计算机": "BK0534",
            # 2024主线
            "高股息": "BK1081",
            "银行": "BK0475",
            "电力": "BK0428",
            "中特估": "BK1080",
            # 其他重要板块
            "证券": "BK0473",
            "保险": "BK0474",
            "酿酒": "BK0477",
            "元器件": "BK0459",
        }
        
        result = {}
        print("\n开始采集概念板块数据...")
        for name, code in key_sectors.items():
            try:
                # 获取板块历史数据
                df = ak.stock_board_concept_hist_em(symbol=name, period="daily",
                                                    start_date="20210101", end_date="20251231")
                if df is not None and len(df) > 0:
                    df['日期'] = pd.to_datetime(df['日期'])
                    result[name] = df
                    print(f"✓ 获取板块{name}: {len(df)}条")
                    df.to_csv(f"{self.data_dir}/sector_{name}.csv", index=False, encoding='utf-8-sig')
                else:
                    print(f"✗ 板块{name}返回空数据")
            except Exception as e:
                print(f"✗ 获取板块{name}失败: {e}")
            time.sleep(0.3)
                
        return result
    
    def get_limit_up_data_range(self, start_date, end_date):
        """获取指定日期范围的涨停数据"""
        current = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        
        all_data = []
        while current <= end:
            date_str = current.strftime("%Y%m%d")
            try:
                df = ak.stock_zt_pool_em(date=date_str)
                if df is not None and len(df) > 0:
                    df['日期'] = date_str
                    all_data.append(df)
                    print(f"✓ {date_str} 涨停数据: {len(df)}条")
            except Exception as e:
                print(f"✗ {date_str} 涨停数据获取失败")
            
            current += timedelta(days=1)
            time.sleep(0.2)
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            combined.to_csv(f"{self.data_dir}/limit_up_all.csv", index=False, encoding='utf-8-sig')
            return combined
        return None
    
    def get_limit_down_data_range(self, start_date, end_date):
        """获取指定日期范围的跌停数据"""
        current = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        
        all_data = []
        while current <= end:
            date_str = current.strftime("%Y%m%d")
            try:
                df = ak.stock_zt_pool_dtgc_em(date=date_str)
                if df is not None and len(df) > 0:
                    df['日期'] = date_str
                    all_data.append(df)
                    print(f"✓ {date_str} 跌停数据: {len(df)}条")
            except Exception as e:
                print(f"✗ {date_str} 跌停数据获取失败")
            
            current += timedelta(days=1)
            time.sleep(0.2)
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            combined.to_csv(f"{self.data_dir}/limit_down_all.csv", index=False, encoding='utf-8-sig')
            return combined
        return None
    
    def collect_key_dates(self):
        """标记历史关键日期"""
        key_dates = {
            # 2021年
            "20210218": {"type": "高点", "event": "春节后高点", "index": "沪深300见顶", "season": "秋收"},
            "20210309": {"type": "低点", "event": "核心资产抱团瓦解低点", "index": "抱团股暴跌", "season": "春播"},
            "20210914": {"type": "高点", "event": "周期股见顶", "index": "中证500高点", "season": "秋收"},
            "20211213": {"type": "高点", "event": "年底反弹高点", "index": "上证指数3708", "season": "秋收"},
            
            # 2022年
            "20220427": {"type": "低点", "event": "俄乌冲突+上海疫情低点", "index": "政策底2863", "season": "春播"},
            "20220629": {"type": "高点", "event": "汽车板块见顶", "index": "新能源行情高点", "season": "秋收"},
            "20221031": {"type": "低点", "event": "疫情防控政策转向预期", "index": "市场底2885", "season": "春播"},
            
            # 2023年
            "20230130": {"type": "高点", "event": "春节后高开低走", "index": "AI行情前高点", "season": "冬藏"},
            "20230509": {"type": "高点", "event": "中特估见顶", "index": "上证指数3418", "season": "秋收"},
            "20230825": {"type": "低点", "event": "印花税减半政策底", "index": "3053政策底", "season": "春播"},
            
            # 2024年
            "20240205": {"type": "低点", "event": "微盘股流动性危机", "index": "2635低点", "season": "春播"},
            "20240520": {"type": "高点", "event": "地产政策见顶", "index": "3174高点", "season": "秋收"},
            "20240918": {"type": "低点", "event": "美联储降息前低点", "index": "2689低点", "season": "春播"},
            "20241008": {"type": "高点", "event": "国庆后历史天量高开", "index": "3674高点", "season": "秋收"},
        }
        
        with open(f"{self.data_dir}/key_dates.json", "w", encoding='utf-8') as f:
            json.dump(key_dates, f, ensure_ascii=False, indent=2)
        
        return key_dates
    
    def create_sample_daily_data(self):
        """创建模拟的每日市场情绪数据（用于回测）"""
        # 生成2021-2025每个交易日的模拟数据
        dates = pd.date_range(start='2021-01-01', end='2025-02-23', freq='B')  # 工作日
        
        data = []
        for date in dates:
            date_str = date.strftime('%Y%m%d')
            # 使用随机数生成模拟数据（后续可以替换为真实数据）
            import random
            base_panic = random.gauss(50, 20)  # 恐慌度基础值
            
            record = {
                '日期': date_str,
                '涨停家数': int(max(20, random.gauss(60, 40))),
                '跌停家数': int(max(0, random.gauss(15, 15))),
                '炸板率': round(random.uniform(0.2, 0.5), 2),
                '连板高度': int(max(1, random.gauss(4, 2))),
                '昨日涨停溢价': round(random.gauss(1.5, 2), 2),
                '恐慌指数': round(max(0, min(100, base_panic)), 2),
                '市场情绪': random.choice(['极度恐慌', '恐慌', '中性', '乐观', '极度乐观']),
            }
            data.append(record)
        
        df = pd.DataFrame(data)
        df.to_csv(f"{self.data_dir}/daily_market_stats.csv", index=False, encoding='utf-8-sig')
        print(f"✓ 生成每日市场数据: {len(df)}条")
        return df

if __name__ == "__main__":
    collector = DataCollector("zhuangjiaren_backtest/data")
    
    print("="*60)
    print("庄稼人战法 - 数据收集")
    print("="*60)
    
    # 1. 获取指数数据
    print("\n【阶段1】采集指数数据...")
    print("-"*60)
    index_data = collector.get_index_data("20210101", "20250223")
    
    # 2. 获取板块数据
    print("\n【阶段2】采集概念板块数据...")
    print("-"*60)
    sector_data = collector.get_sector_board_data()
    
    # 3. 保存关键日期
    print("\n【阶段3】保存关键日期标记...")
    print("-"*60)
    key_dates = collector.collect_key_dates()
    print(f"✓ 标记了{len(key_dates)}个关键日期")
    
    # 4. 生成每日市场统计（模拟数据，后续可替换为真实数据）
    print("\n【阶段4】生成每日市场统计数据...")
    print("-"*60)
    daily_stats = collector.create_sample_daily_data()
    
    print("\n" + "="*60)
    print("✓ 数据收集完成！")
    print("="*60)
    print(f"数据保存位置: {collector.data_dir}/")
    print(f"- 指数数据: {len(index_data)}个")
    print(f"- 板块数据: {len(sector_data)}个")
    print(f"- 关键日期: {len(key_dates)}个")
    print(f"- 每日统计: {len(daily_stats)}条")
