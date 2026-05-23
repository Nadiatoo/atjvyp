#!/usr/bin/env python3
# 简单实时数据测试

import sqlite3
from datetime import datetime
from fix_sina_api import get_sina_stock_data
from a_stock_realtime_test import get_from_tencent

def test_simple_realtime():
    """简单实时数据测试"""
    
    print("=== 简单实时数据测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 测试关键股票
    key_stocks = [
        {"code": "002675", "name": "东诚药业", "market": "sz"},
        {"code": "600893", "name": "航发动力", "market": "sh"},
        {"code": "000881", "name": "中广核技", "market": "sz"},
        {"code": "300114", "name": "中航电测", "market": "sz"},
        {"code": "600391", "name": "航发科技", "market": "sh"},
    ]
    
    results = []
    
    for stock in key_stocks:
        print(f"\n📊 {stock['name']}({stock['code']}):")
        
        # 从新浪获取
        sina_data = get_sina_stock_data(stock['code'], stock['market'])
        
        if sina_data:
            print(f"  新浪: {sina_data['price']}元 ({sina_data['change_percent']:+.2f}%)")
            print(f"      成交量: {sina_data['volume']:,.0f}手")
            
            # 保存到数据库
            save_to_database(sina_data)
            results.append(sina_data)
        else:
            print(f"  新浪: 获取失败")
        
        # 从腾讯获取（对比）
        tencent_data = get_from_tencent(stock['code'], stock['market'])
        if tencent_data:
            print(f"  腾讯: {tencent_data['price']}元 ({tencent_data['change_percent']:+.2f}%)")
    
    # 显示数据库中的最新数据
    print("\n" + "=" * 50)
    print("📈 数据库最新数据:")
    
    show_database_data()

def save_to_database(data):
    """保存数据到数据库"""
    try:
        db_path = "/Users/tuqibiao/.openclaw/workspace/a_stock_data.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 计算涨跌幅
        prev_close = data.get("prev_close", data.get("pre_close", 0))
        price = data["price"]
        
        if prev_close > 0:
            change = price - prev_close
            change_percent = change / prev_close * 100
        else:
            change = 0
            change_percent = 0
        
        # 插入数据
        cursor.execute('''
            INSERT INTO stock_realtime 
            (code, price, change, change_percent, volume, amount, high, low, open, pre_close, time, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["code"],
            price,
            change,
            change_percent,
            data.get("volume", 0),
            data.get("amount", 0),
            data.get("high", price),
            data.get("low", price),
            data.get("open", price),
            prev_close,
            current_time,
            data.get("source", "sina")
        ))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"  保存到数据库失败: {e}")
        return False

def show_database_data():
    """显示数据库中的数据"""
    try:
        db_path = "/Users/tuqibiao/.openclaw/workspace/a_stock_data.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取最新数据
        cursor.execute('''
            SELECT code, price, change_percent, volume, time, source 
            FROM stock_realtime 
            WHERE time = (SELECT MAX(time) FROM stock_realtime WHERE code = r.code)
            ORDER BY time DESC 
            LIMIT 10
        ''')
        
        results = cursor.fetchall()
        
        if results:
            for code, price, change_percent, volume, update_time, source in results:
                print(f"{code}: {price}元 ({change_percent:+.2f}%), 成交量: {volume:,.0f}手")
                print(f"  更新时间: {update_time}, 数据源: {source}")
        else:
            print("数据库中没有数据")
        
        conn.close()
        
    except Exception as e:
        print(f"显示数据库数据失败: {e}")

def check_database_tables():
    """检查数据库表"""
    print("\n🔍 检查数据库表...")
    
    try:
        db_path = "/Users/tuqibiao/.openclaw/workspace/a_stock_data.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("现有表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查stock_basic表数据
        cursor.execute("SELECT COUNT(*) FROM stock_basic")
        stock_count = cursor.fetchone()[0]
        print(f"\nstock_basic表记录数: {stock_count}")
        
        # 检查stock_realtime表数据
        cursor.execute("SELECT COUNT(*) FROM stock_realtime")
        realtime_count = cursor.fetchone()[0]
        print(f"stock_realtime表记录数: {realtime_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库失败: {e}")

if __name__ == "__main__":
    # 检查数据库
    check_database_tables()
    
    # 运行测试
    test_simple_realtime()
    
    print("\n" + "=" * 50)
    print("✅ 实时数据系统测试完成")
    print("\n💡 下一步:")
    print("1. 获取真实的5000+ A股列表")
    print("2. 建立定时更新机制")
    print("3. 开发数据准确性监控")