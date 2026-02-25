#!/usr/bin/env python3
"""
庄稼人战法 - 东方财富数据采集模块
使用akshare库获取A股市场历史数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class DataCollector:
    """数据采集器"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
    def get_index_data(self, start_date="20210101", end_date="20251231"):
        """获取主要指数数据"""
        indices = {
            "上证指数": "sh000001",
            "深证成指": "sz399001",
            "创业板指": "sz399006",
            "沪深300": "sh000300",
            "中证1000": "sh000852"
        }
        
        result = {}
        for name, code in indices.items():
            try:
                df = ak.index_zh_a_hist(symbol=code, period="daily", 
                                        start_date=start_date, end_date=end_date)
                df['日期'] = pd.to_datetime(df['日期'])
                result[name] = df
                print(f"✓ 获取{name}数据: {len(df)}条")
            except Exception as e:
                print(f"✗ 获取{name}失败: {e}")
                
        return result
    
    def get_limit_up_data(self, date_str):
        """获取某日涨停数据"""
        try:
            df = ak.stock_zt_pool_em(date=date_str)
            return df
        except Exception as e:
            print(f"获取{date_str}涨停数据失败: {e}")
            return None
    
    def get_limit_down_data(self, date_str):
        """获取某日跌停数据"""
        try:
            df = ak.stock_zt_pool_dtgc_em(date=date_str)
            return df
        except Exception as e:
            print(f"获取{date_str}跌停数据失败: {e}")
            return None
    
    def get_sector_data(self, start_date="20210101", end_date="20251231"):
        """获取申万行业指数数据"""
        # 申万一级行业
        sectors = [
            "801010", "801020", "801030", "801040", "801050",  # 农林牧渔、采掘、化工、钢铁、有色
            "801060", "801070", "801080", "801090", "801100",  # 建筑、建材、军工、汽车、家电
            "801110", "801120", "801130", "801140", "801150",  # 纺织服装、轻工、医药、公用事业、交运
            "801160", "801170", "801180", "801190", "801200",  # 房地产、商贸、餐饮旅游、银行、非银金融
            "801210", "801220", "801230", "801710", "801720",  # 综合、建筑建材、信息服务、机械设备、国防军工
            "801730", "801740", "801750", "801760", "801770",  # 电气设备、计算机、传媒、通信、银行
            "801780", "801790", "801880", "801890"              # 非银、房地产、汽车、电子
        ]
        
        result = {}
        for sector in sectors[:10]:  # 先取前10个测试
            try:
                df = ak.index_zh_a_hist(symbol=sector, period="daily",
                                        start_date=start_date, end_date=end_date)
                result[sector] = df
            except Exception as e:
                print(f"获取行业{sector}失败: {e}")
                
        return result
    
    def get_daily_market_stats(self, date_str):
        """获取每日市场统计"""
        try:
            df = ak.stock_zt_pool_zbgc_em(date=date_str)
            return df
        except Exception as e:
            return None
    
    def collect_key_dates(self):
        """标记历史关键日期"""
        key_dates = {
            # 2021年
            "20210218": {"type": "高点", "event": "春节后高点", "index": "沪深300见顶"},
            "20210309": {"type": "低点", "event": "核心资产抱团瓦解低点", "index": "抱团股暴跌"},
            "20210914": {"type": "高点", "event": "周期股见顶", "index": "中证500高点"},
            "20211213": {"type": "高点", "event": "年底反弹高点", "index": "上证指数3708"},
            
            # 2022年
            "20220427": {"type": "低点", "event": "俄乌冲突+上海疫情低点", "index": "政策底2863"},
            "20220629": {"type": "高点", "event": "汽车板块见顶", "index": "新能源行情高点"},
            "20221031": {"type": "低点", "event": "疫情防控政策转向预期", "index": "市场底2885"},
            
            # 2023年
            "20230130": {"type": "高点", "event": "春节后高开低走", "index": "AI行情前高点"},
            "20230509": {"type": "高点", "event": "中特估见顶", "index": "上证指数3418"},
            "20230825": {"type": "低点", "event": "印花税减半政策底", "index": "3053政策底"},
            
            # 2024年
            "20240205": {"type": "低点", "event": "微盘股流动性危机", "index": "2635低点"},
            "20240520": {"type": "高点", "event": "地产政策见顶", "index": "3174高点"},
            "20240918": {"type": "低点", "event": "美联储降息前低点", "index": "2689低点"},
            "20241008": {"type": "高点", "event": "国庆后历史天量高开", "index": "3674高点"},
        }
        return key_dates

if __name__ == "__main__":
    collector = DataCollector("zhuangjiaren_backtest/data")
    
    # 获取指数数据
    print("="*50)
    print("开始采集指数数据...")
    print("="*50)
    index_data = collector.get_index_data("20210101", "20251231")
    
    # 保存数据
    for name, df in index_data.items():
        df.to_csv(f"zhuangjiaren_backtest/data/index_{name}.csv", index=False, encoding='utf-8-sig')
    
    # 保存关键日期
    key_dates = collector.collect_key_dates()
    with open("zhuangjiaren_backtest/data/key_dates.json", "w", encoding='utf-8') as f:
        json.dump(key_dates, f, ensure_ascii=False, indent=2)
    
    print("\n✓ 数据收集完成！")
