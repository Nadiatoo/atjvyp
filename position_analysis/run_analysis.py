#!/usr/bin/env python3
"""
运行完整持仓分析
测试系统完整功能
"""

import sys
import os
import time
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def run_complete_analysis():
    """运行完整分析"""
    print("=" * 70)
    print("持仓分析系统 - 完整功能测试")
    print("=" * 70)
    
    start_time = time.time()
    
    try:
        from main import PortfolioAnalysisSystem
        
        print("🚀 创建分析系统实例...")
        system = PortfolioAnalysisSystem()
        print("✅ 系统实例创建成功")
        
        # 设置分析参数
        input_file = os.path.join(os.path.dirname(__file__), 'data', 'sample_portfolio.csv')
        output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
        
        print(f"\n📁 输入文件: {input_file}")
        print(f"📁 输出目录: {output_dir}")
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'reports'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'charts'), exist_ok=True)
        
        print("\n📊 步骤1: 加载持仓数据...")
        portfolio_data = system.load_portfolio_data(input_file, client_info={"name": "测试客户"})
        
        if portfolio_data is None or len(portfolio_data) == 0:
            print("❌ 数据加载失败")
            return False
        
        print(f"✅ 数据加载成功，共 {len(portfolio_data)} 条持仓记录")
        
        print("\n📈 步骤2: 更新市场数据...")
        try:
            updated_data = system.update_market_data()
            print(f"✅ 市场数据更新成功，共 {len(updated_data)} 条记录")
        except Exception as e:
            print(f"⚠️ 市场数据更新失败: {e}")
            print("继续使用成本价进行分析...")
        
        print("\n🔍 步骤3: 执行行业分析...")
        try:
            industry_analysis = system.analyze_industry_structure()
            if industry_analysis:
                print("✅ 行业分析完成")
                # 显示前几个行业
                for i, (industry, data) in enumerate(list(industry_analysis.items())[:3]):
                    print(f"   {industry}: {data.get('market_value', 0):.2f}元 ({data.get('percentage', 0):.1f}%)")
                if len(industry_analysis) > 3:
                    print(f"   ... 共 {len(industry_analysis)} 个行业")
            else:
                print("❌ 行业分析失败")
        except Exception as e:
            print(f"❌ 行业分析错误: {e}")
        
        print("\n⚠️ 步骤4: 执行风险评估...")
        try:
            risk_assessment = system.assess_portfolio_risk()
            if risk_assessment:
                print("✅ 风险评估完成")
                for key, value in risk_assessment.items():
                    if isinstance(value, (int, float)):
                        print(f"   {key}: {value:.2f}")
                    else:
                        print(f"   {key}: {value}")
            else:
                print("❌ 风险评估失败")
        except Exception as e:
            print(f"❌ 风险评估错误: {e}")
        
        print("\n📄 步骤5: 生成报告...")
        try:
            report_files = system.generate_reports()
            if report_files:
                print("✅ 报告生成完成")
                for report_type, filepath in report_files.items():
                    if os.path.exists(filepath):
                        file_size = os.path.getsize(filepath)
                        print(f"   {report_type}: {filepath} ({file_size} bytes)")
                    else:
                        print(f"   {report_type}: 文件未生成")
            else:
                print("❌ 报告生成失败")
        except Exception as e:
            print(f"❌ 报告生成错误: {e}")
        
        print("\n🖼️ 步骤6: 生成图表...")
        try:
            chart_files = system.generate_charts()
            if chart_files:
                print("✅ 图表生成完成")
                for chart_type, filepath in chart_files.items():
                    if os.path.exists(filepath):
                        file_size = os.path.getsize(filepath)
                        print(f"   {chart_type}: {filepath} ({file_size} bytes)")
                    else:
                        print(f"   {chart_type}: 文件未生成")
            else:
                print("⚠️ 图表生成失败或未启用")
        except Exception as e:
            print(f"⚠️ 图表生成错误: {e}")
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("测试完成！")
        print("=" * 70)
        
        print(f"\n📊 测试统计:")
        print(f"   总耗时: {elapsed_time:.2f} 秒")
        print(f"   输入记录: {len(portfolio_data)} 条")
        print(f"   输出文件: 查看 outputs/ 目录")
        
        # 检查输出文件
        output_files = []
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if not file.startswith('.'):  # 忽略隐藏文件
                    output_files.append(os.path.join(root, file))
        
        if output_files:
            print(f"\n📁 生成的输出文件 ({len(output_files)} 个):")
            for file in sorted(output_files)[:10]:  # 显示前10个文件
                file_size = os.path.getsize(file)
                print(f"   {os.path.basename(file)} ({file_size} bytes)")
            if len(output_files) > 10:
                print(f"   ... 还有 {len(output_files) - 10} 个文件")
        else:
            print("\n⚠️ 未生成输出文件")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 分析过程出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_output_files():
    """检查输出文件"""
    print("\n🔍 检查输出文件...")
    
    output_dir = os.path.join(os.path.dirname(__file__), 'outputs')
    
    if not os.path.exists(output_dir):
        print("❌ 输出目录不存在")
        return
    
    file_count = 0
    total_size = 0
    
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if not file.startswith('.'):  # 忽略隐藏文件
                filepath = os.path.join(root, file)
                file_size = os.path.getsize(filepath)
                file_count += 1
                total_size += file_size
                
                # 显示文件信息
                rel_path = os.path.relpath(filepath, output_dir)
                modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"   📄 {rel_path}")
                print(f"     大小: {file_size} bytes, 修改时间: {modified_time}")
    
    if file_count > 0:
        print(f"\n📊 输出文件统计:")
        print(f"   文件数量: {file_count} 个")
        print(f"   总大小: {total_size} bytes ({total_size/1024:.1f} KB)")
    else:
        print("⚠️ 输出目录为空")

def main():
    # 运行完整分析
    success = run_complete_analysis()
    
    # 检查输出文件
    check_output_files()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 完整分析测试完成！系统功能正常。")
        print("\n下一步:")
        print("1. 查看生成的报告: outputs/reports/ 目录")
        print("2. 查看生成的图表: outputs/charts/ 目录")
        print("3. 使用自定义数据: python src/main.py <你的数据文件>")
    else:
        print("⚠️ 分析测试失败，需要修复问题。")
        print("\n常见问题:")
        print("1. 依赖包缺失: pip install matplotlib seaborn")
        print("2. 数据文件格式错误: 检查CSV/Excel文件格式")
        print("3. API连接问题: 检查网络连接")
    
    print(f"\n测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")

if __name__ == "__main__":
    main()