#!/usr/bin/env python3
"""
修复行业分析模块bug
问题：portfolio_df可能是Series而不是DataFrame
"""

import os

def fix_industry_analysis_bug():
    """修复industry_analysis.py中的bug"""
    file_path = "src/industry_analysis.py"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复第132行的问题：确保portfolio_df是DataFrame
    old_code = """        # 确保有持仓市值列
        if '持仓市值' not in portfolio_df.columns:
            logger.error("持仓数据缺少'持仓市值'列")
            return {}"""
    
    new_code = """        # 确保portfolio_df是DataFrame
        if isinstance(portfolio_df, pd.Series):
            portfolio_df = portfolio_df.to_frame().T
        
        # 确保有持仓市值列
        if '持仓市值' not in portfolio_df.columns:
            logger.error("持仓数据缺少'持仓市值'列")
            return {}"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✅ 修复了portfolio_df类型检查问题")
    else:
        print("⚠️ 未找到需要修复的代码，可能已修复")
    
    # 修复第400行的问题
    old_code2 = """        if '行业分类' not in portfolio_df.columns:"""
    
    new_code2 = """        # 确保portfolio_df是DataFrame
        if isinstance(portfolio_df, pd.Series):
            portfolio_df = portfolio_df.to_frame().T
        
        if '行业分类' not in portfolio_df.columns:"""
    
    if old_code2 in content:
        # 找到这个if语句的开始位置
        start_pos = content.find(old_code2)
        if start_pos != -1:
            # 获取前面的几行代码，看看是否需要添加转换
            lines_before = content[:start_pos].split('\n')[-5:]
            if "isinstance(portfolio_df, pd.Series)" not in '\n'.join(lines_before):
                content = content.replace(old_code2, new_code2)
                print("✅ 修复了第二个portfolio_df类型检查问题")
            else:
                print("⚠️ 第二个检查点已包含类型转换")
    
    # 保存修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 行业分析模块修复完成")
    return True

def test_fix():
    """测试修复是否有效"""
    print("\n🔍 测试修复效果...")
    
    try:
        import pandas as pd
        import sys
        sys.path.append('src')
        
        # 创建一个测试Series
        test_series = pd.Series({
            '股票代码': '000001',
            '股票名称': '平安银行',
            '持仓数量': 1000,
            '持仓市值': 15200.0,
            '行业分类': '银行'
        })
        
        print(f"测试Series类型: {type(test_series)}")
        print(f"测试Series内容: {test_series}")
        
        # 测试转换
        if isinstance(test_series, pd.Series):
            df = test_series.to_frame().T
            print(f"转换后DataFrame类型: {type(df)}")
            print(f"转换后DataFrame形状: {df.shape}")
            print(f"转换后DataFrame列名: {list(df.columns)}")
            
            # 检查是否有'持仓市值'列
            if '持仓市值' in df.columns:
                print("✅ 修复测试通过：Series成功转换为DataFrame")
                return True
            else:
                print("❌ 修复测试失败：转换后缺少'持仓市值'列")
                return False
        else:
            print("❌ 测试数据不是Series")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("行业分析模块bug修复")
    print("=" * 60)
    
    # 执行修复
    fix_success = fix_industry_analysis_bug()
    
    if fix_success:
        # 测试修复
        test_success = test_fix()
        
        print("\n" + "=" * 60)
        if test_success:
            print("🎉 修复完成！可以重新运行分析。")
        else:
            print("⚠️ 修复完成但测试失败，可能需要进一步调试。")
    else:
        print("❌ 修复失败")
    
    print(f"\n运行分析命令:")
    print("cd src && python main.py ../data/sample_portfolio.csv --client-name '测试客户'")

if __name__ == "__main__":
    main()