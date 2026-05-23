#!/usr/bin/env python3
"""
检查行业分析返回的数据结构
"""

import sys
import os
import pandas as pd
import json

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_structure():
    """检查数据结构"""
    print("🔍 检查行业分析返回的数据结构...")
    
    try:
        from industry_analysis import IndustryAnalyzer
        
        # 创建分析器
        analyzer = IndustryAnalyzer()
        
        # 创建测试数据
        test_data = {
            '股票代码': ['000001', '600036', '000858'],
            '股票名称': ['平安银行', '招商银行', '五粮液'],
            '持仓数量': [1000, 800, 500],
            '成本价': [15.2, 32.5, 180.3],
            '持仓市值': [15200.0, 26000.0, 90150.0],
            '行业分类': ['银行', '银行', '食品饮料']
        }
        
        df = pd.DataFrame(test_data)
        
        # 执行分析
        result = analyzer.analyze_portfolio_structure(df)
        
        print(f"返回结果类型: {type(result)}")
        print(f"返回结果键: {list(result.keys())}")
        
        print("\n详细结构:")
        for key, value in result.items():
            print(f"\n{key}:")
            print(f"  类型: {type(value)}")
            
            if isinstance(value, dict):
                print(f"  字典键: {list(value.keys())}")
                if value:
                    first_key = list(value.keys())[0]
                    print(f"  示例值[{first_key}]: {value[first_key]}")
            elif isinstance(value, list):
                print(f"  列表长度: {len(value)}")
                if value:
                    print(f"  第一个元素: {value[0]}")
                    if isinstance(value[0], dict):
                        print(f"    元素类型: dict, 键: {list(value[0].keys())}")
            elif isinstance(value, (int, float, str, bool)):
                print(f"  值: {value}")
            else:
                print(f"  值: {value}")
        
        # 保存为JSON查看
        output_file = os.path.join(os.path.dirname(__file__), 'outputs', 'industry_structure.json')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # 转换不可JSON序列化的对象
        def convert_for_json(obj):
            if isinstance(obj, (pd.Timestamp, pd.Timedelta)):
                return str(obj)
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(item) for item in obj]
            else:
                return obj
        
        import numpy as np
        json_result = convert_for_json(result)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 数据结构已保存到: {output_file}")
        
        # 显示关键信息
        print("\n📊 关键分析指标:")
        if 'portfolio_summary' in result and isinstance(result['portfolio_summary'], dict):
            summary = result['portfolio_summary']
            print(f"  总市值: {summary.get('total_market_value', 0):.2f}")
            print(f"  总股票数: {summary.get('total_stocks', 0)}")
        
        if 'industry_distribution' in result and isinstance(result['industry_distribution'], list):
            distribution = result['industry_distribution']
            print(f"  行业数量: {len(distribution)}")
            if distribution:
                print(f"  前3个行业:")
                for i, industry in enumerate(distribution[:3]):
                    if isinstance(industry, dict):
                        print(f"    {i+1}. {industry.get('行业名称', '未知')}: "
                              f"{industry.get('持仓市值', 0):.2f} ({industry.get('持仓占比', 0):.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 70)
    print("行业分析数据结构检查")
    print("=" * 70)
    
    success = check_structure()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 数据结构检查完成")
        print("\n分析模块返回的是包含多个分析维度的字典，包括:")
        print("1. portfolio_summary - 组合摘要")
        print("2. industry_distribution - 行业分布列表")
        print("3. concentration_analysis - 集中度分析")
        print("4. industry_deviation - 行业偏离度")
        print("5. top_holdings - 前十大持仓")
        print("6. industry_exposure - 行业暴露")
        print("7. analysis_time - 分析时间")
    else:
        print("❌ 数据结构检查失败")
    
    print(f"\n工作目录: {os.getcwd()}")

if __name__ == "__main__":
    main()