#!/usr/bin/env python3
"""
分析客户持仓明细
跳过风险评估模块，专注核心功能
"""

import sys
import os
import pandas as pd
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def analyze_client_portfolio():
    """分析客户持仓"""
    print("=" * 70)
    print("客户持仓分析报告")
    print("=" * 70)
    
    try:
        # 导入核心模块
        from import_data import PortfolioDataImporter
        from market_data import MarketDataFetcher
        from industry_analysis import IndustryAnalyzer
        from report_generator import ReportGenerator
        
        print("✅ 模块导入成功")
        
        # 1. 加载数据
        print("\n📊 步骤1: 加载持仓数据...")
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'analysis_portfolio.csv')
        
        # 直接读取CSV
        df = pd.read_csv(data_path)
        print(f"原始持仓记录: {len(df)} 只股票")
        print(f"持仓明细:")
        for idx, row in df.iterrows():
            print(f"  {row['股票代码']} {row['股票名称']}: {row['持仓数量']}股 @ {row['成本价']}元")
        
        # 2. 获取实时行情
        print("\n📈 步骤2: 获取实时行情...")
        fetcher = MarketDataFetcher()
        
        stock_codes = df['股票代码'].tolist()
        print(f"获取 {len(stock_codes)} 只股票的实时行情...")
        
        market_data = fetcher.get_realtime_quotes(stock_codes)
        
        if market_data is not None and not market_data.empty:
            print(f"✅ 成功获取实时行情")
            
            # 合并行情数据
            market_df = market_data[['股票代码', '最新价', '涨跌幅', '成交量', '成交额']]
            df = pd.merge(df, market_df, on='股票代码', how='left')
            
            # 计算实时市值和盈亏
            df['最新市值'] = df['持仓数量'] * df['最新价']
            df['持仓成本'] = df['持仓数量'] * df['成本价']
            df['浮动盈亏'] = df['最新市值'] - df['持仓成本']
            df['盈亏比例'] = (df['浮动盈亏'] / df['持仓成本'] * 100).round(2)
            
            print(f"\n📊 实时持仓价值:")
            total_cost = df['持仓成本'].sum()
            total_value = df['最新市值'].sum()
            total_profit = df['浮动盈亏'].sum()
            profit_rate = (total_profit / total_cost * 100) if total_cost > 0 else 0
            
            print(f"  总持仓成本: {total_cost:,.2f}元")
            print(f"  总实时市值: {total_value:,.2f}元")
            print(f"  浮动盈亏: {total_profit:,.2f}元 ({profit_rate:.2f}%)")
            
            # 显示个股表现
            print(f"\n📈 个股表现:")
            for idx, row in df.iterrows():
                profit_color = "🟢" if row['浮动盈亏'] >= 0 else "🔴"
                print(f"  {row['股票代码']} {row['股票名称']}:")
                print(f"    成本价: {row['成本价']}元 → 最新价: {row['最新价']}元 ({row['涨跌幅']}%)")
                print(f"    持仓: {row['持仓数量']}股, 市值: {row['最新市值']:,.2f}元")
                print(f"    盈亏: {profit_color} {row['浮动盈亏']:,.2f}元 ({row['盈亏比例']}%)")
        else:
            print("⚠️ 实时行情获取失败，使用成本价计算")
            df['最新价'] = df['成本价']
            df['涨跌幅'] = 0
            df['最新市值'] = df['持仓数量'] * df['成本价']
            df['持仓成本'] = df['最新市值']
            df['浮动盈亏'] = 0
            df['盈亏比例'] = 0
        
        # 3. 行业分析
        print("\n🔍 步骤3: 执行行业分析...")
        analyzer = IndustryAnalyzer()
        industry_result = analyzer.analyze_portfolio_structure(df)
        
        if industry_result:
            print("✅ 行业分析完成")
            
            # 显示行业分布
            if 'industry_distribution' in industry_result:
                distribution = industry_result['industry_distribution']
                if distribution:
                    print(f"\n📊 行业分布 ({len(distribution)} 个行业):")
                    
                    # 按市值排序
                    sorted_industries = sorted(distribution, key=lambda x: x.get('持仓市值', 0), reverse=True)
                    
                    total_industry_value = sum(industry.get('持仓市值', 0) for industry in sorted_industries)
                    
                    for i, industry in enumerate(sorted_industries):
                        industry_name = industry.get('行业名称', '未知')
                        industry_value = industry.get('持仓市值', 0)
                        industry_percent = industry.get('持仓占比', 0)
                        stock_count = industry.get('股票数量', 0)
                        
                        if total_industry_value > 0:
                            actual_percent = (industry_value / total_industry_value * 100)
                        else:
                            actual_percent = 0
                        
                        print(f"  {i+1}. {industry_name}:")
                        print(f"     市值: {industry_value:,.2f}元 ({actual_percent:.1f}%)")
                        print(f"     股票数量: {stock_count}只")
                        
                        # 显示该行业下的股票
                        stocks = industry.get('股票明细', [])
                        if stocks:
                            for stock in stocks[:3]:  # 最多显示3只
                                print(f"       • {stock.get('股票代码', '')} {stock.get('股票名称', '')}: "
                                      f"{stock.get('持仓市值', 0):,.2f}元")
                            if len(stocks) > 3:
                                print(f"       • ... 还有 {len(stocks)-3} 只")
            
            # 显示组合摘要
            if 'portfolio_summary' in industry_result:
                summary = industry_result['portfolio_summary']
                print(f"\n📋 组合摘要:")
                print(f"  总股票数: {summary.get('total_stocks', 0)}只")
                print(f"  总市值: {summary.get('total_market_value', 0):,.2f}元")
                print(f"  平均持仓: {summary.get('avg_position_size', 0):,.2f}元")
                print(f"  最大持仓: {summary.get('max_position', 0):,.2f}元")
                print(f"  最小持仓: {summary.get('min_position', 0):,.2f}元")
        
        # 4. 生成报告
        print("\n📄 步骤4: 生成分析报告...")
        output_dir = os.path.join(os.path.dirname(__file__), 'outputs', 'client_reports')
        os.makedirs(output_dir, exist_ok=True)
        
        report_generator = ReportGenerator()
        
        # 准备报告数据
        report_data = {
            'portfolio_data': df.to_dict('records'),
            'industry_analysis': industry_result if industry_result else {},
            'market_data_available': market_data is not None and not market_data.empty,
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 生成报告
        client_info = {'name': '客户持仓分析', 'analyst': '智能投顾系统'}
        md_report = report_generator.generate_markdown_report(report_data, client_info)
        
        # 保存报告
        report_file = os.path.join(output_dir, f"客户持仓分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(md_report)
        
        print(f"✅ 报告已生成: {report_file}")
        print(f"   文件大小: {os.path.getsize(report_file)} bytes")
        
        # 显示报告摘要
        print(f"\n📋 报告摘要:")
        lines = md_report.split('\n')
        for line in lines[:30]:  # 显示前30行
            if line.strip():
                print(f"  {line}")
        
        if len(lines) > 30:
            print("  ... (完整报告请查看文件)")
        
        # 5. 保存分析结果
        print("\n💾 步骤5: 保存完整分析结果...")
        result_file = os.path.join(output_dir, f"分析结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        import json
        def convert_for_json(obj):
            if isinstance(obj, (pd.Timestamp, pd.Timedelta, datetime)):
                return str(obj)
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict('records')
            elif isinstance(obj, pd.Series):
                return obj.to_dict()
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_json(item) for item in obj]
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return str(obj)
        
        full_results = {
            'client_info': client_info,
            'portfolio_data': convert_for_json(df),
            'industry_analysis': convert_for_json(industry_result),
            'market_data': convert_for_json(market_data) if market_data is not None else None,
            'analysis_metadata': {
                'analysis_time': datetime.now().isoformat(),
                'stock_count': len(df),
                'total_value': float(df['最新市值'].sum()),
                'total_cost': float(df['持仓成本'].sum()),
                'total_profit': float(df['浮动盈亏'].sum())
            }
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(full_results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 完整结果已保存: {result_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 分析过程出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("📊 开始分析客户持仓明细...")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = analyze_client_portfolio()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 客户持仓分析完成！")
        print("\n📁 输出文件位置:")
        print(f"  /Users/tuqibiao/.openclaw/workspace/position_analysis/outputs/client_reports/")
        print("\n📋 分析内容包括:")
        print("  1. 实时持仓价值计算")
        print("  2. 个股盈亏分析")
        print("  3. 行业分布分析")
        print("  4. 完整分析报告")
        print("  5. JSON格式完整结果")
    else:
        print("⚠️ 分析过程中出现错误")
        print("\n建议:")
        print("  1. 检查数据文件格式")
        print("  2. 检查网络连接")
        print("  3. 查看详细错误信息")
    
    print(f"\n分析完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()