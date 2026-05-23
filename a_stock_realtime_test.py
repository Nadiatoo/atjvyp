#!/usr/bin/env python3
# A股实时数据测试脚本

import requests
import json
from datetime import datetime

def test_stock_realtime():
    """测试A股实时数据获取"""
    
    print("=== A股实时数据测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 测试股票列表
    test_stocks = [
        {"code": "002675", "name": "东诚药业", "market": "sz"},
        {"code": "600893", "name": "航发动力", "market": "sh"},
        {"code": "000881", "name": "中广核技", "market": "sz"},
        {"code": "300114", "name": "中航电测", "market": "sz"},
        {"code": "600391", "name": "航发科技", "market": "sh"},
    ]
    
    results = []
    
    for stock in test_stocks:
        print(f"\n📊 测试: {stock['name']}({stock['code']})")
        
        # 尝试从新浪财经获取
        sina_data = get_from_sina(stock['code'], stock['market'])
        if sina_data:
            print(f"  新浪数据: {sina_data['price']}元, 涨跌: {sina_data['change_percent']:.2f}%")
            results.append({
                "stock": stock['name'],
                "code": stock['code'],
                "sina_price": sina_data['price'],
                "sina_change": sina_data['change_percent']
            })
        else:
            print(f"  新浪数据: 获取失败")
        
        # 尝试从腾讯财经获取
        tencent_data = get_from_tencent(stock['code'], stock['market'])
        if tencent_data:
            print(f"  腾讯数据: {tencent_data['price']}元, 涨跌: {tencent_data['change_percent']:.2f}%")
            if 'sina_price' in locals():
                # 计算差异
                diff = abs(sina_data['price'] - tencent_data['price'])
                diff_percent = diff / sina_data['price'] * 100
                print(f"  数据差异: {diff:.3f}元 ({diff_percent:.2f}%)")
        else:
            print(f"  腾讯数据: 获取失败")
    
    print("\n" + "=" * 50)
    print("📈 测试结果汇总:")
    
    for result in results:
        print(f"{result['stock']}({result['code']}): {result.get('sina_price', 'N/A')}元")
    
    print("\n💡 建议:")
    print("1. 新浪财经数据相对稳定")
    print("2. 需要建立数据验证机制")
    print("3. 建议使用多个数据源交叉验证")
    print("4. 需要定时更新数据")

def get_from_sina(code, market):
    """从新浪财经获取实时数据"""
    symbol = f"{market}{code}"
    url = f"http://hq.sinajs.cn/list={symbol}"
    
    try:
        response = requests.get(url, timeout=5)
        response.encoding = 'gbk'
        
        if response.status_code == 200:
            content = response.text
            # 解析数据格式: var hq_str_sz002675="东诚药业,14.480,14.480,...";
            if '="' in content:
                data_str = content.split('="')[1].split('"')[0]
                fields = data_str.split(',')
                
                if len(fields) >= 30:
                    current_price = float(fields[3])  # 当前价
                    prev_close = float(fields[2])     # 昨收
                    change_percent = (current_price - prev_close) / prev_close * 100
                    
                    return {
                        "code": code,
                        "name": fields[0],
                        "price": current_price,
                        "open": float(fields[1]),
                        "high": float(fields[4]),
                        "low": float(fields[5]),
                        "volume": float(fields[8]),  # 成交量(手)
                        "amount": float(fields[9]),  # 成交额(万)
                        "change": current_price - prev_close,
                        "change_percent": change_percent,
                        "source": "sina",
                        "time": datetime.now().strftime("%H:%M:%S")
                    }
    
    except Exception as e:
        print(f"新浪数据获取错误 {code}: {e}")
    
    return None

def get_from_tencent(code, market):
    """从腾讯财经获取实时数据"""
    symbol = f"{market}{code}"
    url = f"http://qt.gtimg.cn/q={symbol}"
    
    try:
        response = requests.get(url, timeout=5)
        response.encoding = 'gbk'
        
        if response.status_code == 200:
            content = response.text
            # 解析数据格式: v_sz002675="51~东诚药业~002675~14.48~...";
            if '="' in content:
                data_str = content.split('="')[1].split('"')[0]
                fields = data_str.split('~')
                
                if len(fields) >= 40:
                    current_price = float(fields[3])  # 当前价
                    prev_close = float(fields[4])     # 昨收
                    change_percent = (current_price - prev_close) / prev_close * 100
                    
                    return {
                        "code": code,
                        "name": fields[1],
                        "price": current_price,
                        "open": float(fields[5]),
                        "high": float(fields[33]),
                        "low": float(fields[34]),
                        "volume": float(fields[6]),   # 成交量(手)
                        "amount": float(fields[37]),  # 成交额(万)
                        "change": current_price - prev_close,
                        "change_percent": change_percent,
                        "source": "tencent",
                        "time": datetime.now().strftime("%H:%M:%S")
                    }
    
    except Exception as e:
        print(f"腾讯数据获取错误 {code}: {e}")
    
    return None

if __name__ == "__main__":
    test_stock_realtime()