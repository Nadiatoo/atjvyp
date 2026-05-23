#!/usr/bin/env python3
# 修复新浪财经API问题

import requests
import re
from datetime import datetime

def test_sina_api_fix():
    """测试修复后的新浪API"""
    
    print("=== 新浪财经API修复测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 测试股票
    test_cases = [
        {"code": "002675", "name": "东诚药业", "market": "sz"},
        {"code": "600893", "name": "航发动力", "market": "sh"},
        {"code": "000881", "name": "中广核技", "market": "sz"},
        {"code": "300114", "name": "中航电测", "market": "sz"},
        {"code": "600391", "name": "航发科技", "market": "sh"},
    ]
    
    success_count = 0
    
    for stock in test_cases:
        print(f"\n📊 测试: {stock['name']}({stock['code']})")
        
        data = get_sina_stock_data(stock['code'], stock['market'])
        
        if data:
            success_count += 1
            print(f"  ✅ 成功获取")
            print(f"     价格: {data['price']}元")
            print(f"     涨跌: {data['change_percent']:.2f}%")
            print(f"     成交量: {data['volume']:,}手")
            print(f"     时间: {data['time']}")
        else:
            print(f"  ❌ 获取失败")
    
    print("\n" + "=" * 50)
    print(f"📈 测试结果: {success_count}/{len(test_cases)} 成功")
    
    if success_count == len(test_cases):
        print("✅ 新浪财经API修复成功")
    else:
        print("⚠️  部分股票数据获取失败，需要进一步调试")

def get_sina_stock_data(code, market="sz"):
    """获取新浪财经股票数据（修复版）"""
    
    # 新浪财经的股票代码格式
    if market == "sz":
        symbol = f"sz{code}"
    elif market == "sh":
        symbol = f"sh{code}"
    else:
        symbol = code
    
    url = f"http://hq.sinajs.cn/list={symbol}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer': 'http://finance.sina.com.cn',
    }
    
    try:
        # 设置超时和重试
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 尝试多种编码
            for encoding in ['gbk', 'gb2312', 'utf-8']:
                try:
                    response.encoding = encoding
                    content = response.text
                    
                    # 解析数据
                    # 格式: var hq_str_sz002675="东诚药业,14.480,14.480,0.000,0.000,0.000,14.480,14.480,...";
                    
                    # 使用正则表达式提取数据
                    pattern = r'var hq_str_' + symbol + r'="([^"]+)"'
                    match = re.search(pattern, content)
                    
                    if match:
                        data_str = match.group(1)
                        fields = data_str.split(',')
                        
                        if len(fields) >= 30:
                            # 解析关键字段
                            name = fields[0]
                            open_price = float(fields[1])  # 开盘
                            prev_close = float(fields[2])  # 昨收
                            current_price = float(fields[3])  # 当前
                            high = float(fields[4])  # 最高
                            low = float(fields[5])  # 最低
                            volume = float(fields[8])  # 成交量(手)
                            amount = float(fields[9])  # 成交额(万)
                            
                            # 计算涨跌幅
                            change = current_price - prev_close
                            change_percent = change / prev_close * 100 if prev_close > 0 else 0
                            
                            return {
                                "code": code,
                                "name": name,
                                "price": current_price,
                                "open": open_price,
                                "prev_close": prev_close,
                                "high": high,
                                "low": low,
                                "volume": volume,
                                "amount": amount,
                                "change": change,
                                "change_percent": change_percent,
                                "source": "sina",
                                "time": datetime.now().strftime("%H:%M:%S"),
                                "raw_fields_count": len(fields)
                            }
                        
                        else:
                            print(f"  字段数量不足: {len(fields)}")
                            continue
                    
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"  解析错误: {e}")
                    continue
        
        else:
            print(f"  HTTP状态码: {response.status_code}")
    
    except requests.exceptions.Timeout:
        print(f"  请求超时")
    except requests.exceptions.ConnectionError:
        print(f"  连接错误")
    except Exception as e:
        print(f"  未知错误: {e}")
    
    return None

def compare_sina_tencent():
    """对比新浪和腾讯数据"""
    
    print("\n=== 数据源对比测试 ===")
    
    test_stocks = [
        {"code": "002675", "name": "东诚药业", "market": "sz"},
        {"code": "600893", "name": "航发动力", "market": "sh"},
    ]
    
    for stock in test_stocks:
        print(f"\n📊 {stock['name']}({stock['code']}):")
        
        sina_data = get_sina_stock_data(stock['code'], stock['market'])
        tencent_data = get_tencent_stock_data(stock['code'], stock['market'])
        
        if sina_data and tencent_data:
            price_diff = abs(sina_data['price'] - tencent_data['price'])
            price_diff_percent = price_diff / sina_data['price'] * 100
            
            print(f"  新浪: {sina_data['price']}元")
            print(f"  腾讯: {tencent_data['price']}元")
            print(f"  差异: {price_diff:.3f}元 ({price_diff_percent:.2f}%)")
            
            if price_diff_percent < 0.1:  # 差异小于0.1%
                print(f"  ✅ 数据一致性: 优秀")
            elif price_diff_percent < 0.5:
                print(f"  ⚠️  数据一致性: 良好")
            else:
                print(f"  ❌ 数据一致性: 需要检查")
        else:
            print(f"  数据获取不完整")

def get_tencent_stock_data(code, market="sz"):
    """获取腾讯财经股票数据"""
    symbol = f"{market}{code}"
    url = f"http://qt.gtimg.cn/q={symbol}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://gu.qq.com',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'gbk'
        
        if response.status_code == 200:
            content = response.text
            # 格式: v_sz002675="51~东诚药业~002675~14.48~...";
            
            if '="' in content:
                data_str = content.split('="')[1].split('"')[0]
                fields = data_str.split('~')
                
                if len(fields) >= 40:
                    current_price = float(fields[3])
                    prev_close = float(fields[4])
                    change_percent = (current_price - prev_close) / prev_close * 100
                    
                    return {
                        "code": code,
                        "name": fields[1],
                        "price": current_price,
                        "prev_close": prev_close,
                        "change_percent": change_percent,
                        "source": "tencent",
                        "time": datetime.now().strftime("%H:%M:%S")
                    }
    
    except Exception as e:
        print(f"腾讯数据获取错误: {e}")
    
    return None

if __name__ == "__main__":
    # 运行修复测试
    test_sina_api_fix()
    
    # 运行数据源对比
    compare_sina_tencent()
    
    print("\n" + "=" * 50)
    print("💡 下一步建议:")
    print("1. 如果新浪API修复成功，建立双数据源验证")
    print("2. 获取全市场股票列表")
    print("3. 建立实时数据更新系统")