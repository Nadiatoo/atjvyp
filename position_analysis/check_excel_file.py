#!/usr/bin/env python3
"""
检查持仓明细Excel文件
"""

import pandas as pd
import os

def check_excel_file(file_path):
    """检查Excel文件内容"""
    print("🔍 检查Excel文件...")
    print(f"文件路径: {file_path}")
    print(f"文件大小: {os.path.getsize(file_path)} bytes")
    
    try:
        # 读取Excel文件
        print("\n📊 读取Excel文件...")
        
        # 获取所有工作表名称
        xl = pd.ExcelFile(file_path)
        sheet_names = xl.sheet_names
        print(f"工作表数量: {len(sheet_names)}")
        print(f"工作表名称: {sheet_names}")
        
        # 读取第一个工作表
        df = pd.read_excel(file_path, sheet_name=0)
        print(f"\n第一个工作表数据:")
        print(f"  行数: {df.shape[0]}")
        print(f"  列数: {df.shape[1]}")
        print(f"  列名: {list(df.columns)}")
        
        # 显示前几行数据
        print(f"\n前5行数据:")
        print(df.head())
        
        # 检查数据质量
        print(f"\n🔍 数据质量检查:")
        print(f"  总记录数: {len(df)}")
        print(f"  空值统计:")
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                print(f"    {col}: {null_count} 个空值")
        
        # 检查必需字段
        required_fields = ['股票代码', '股票名称', '持仓数量', '成本价']
        missing_fields = []
        for field in required_fields:
            if field not in df.columns:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"⚠️ 缺少必需字段: {missing_fields}")
            print(f"  现有字段: {list(df.columns)}")
            
            # 尝试匹配可能的字段名
            print(f"\n🔍 尝试匹配字段名:")
            for field in missing_fields:
                possible_matches = []
                for col in df.columns:
                    if field in str(col) or str(col) in field:
                        possible_matches.append(col)
                if possible_matches:
                    print(f"  '{field}' 可能对应: {possible_matches}")
        else:
            print(f"✅ 所有必需字段都存在")
        
        # 检查股票代码格式
        if '股票代码' in df.columns:
            print(f"\n📈 股票代码分析:")
            # 显示前几个股票代码
            sample_codes = df['股票代码'].head(5).tolist()
            print(f"  示例股票代码: {sample_codes}")
            
            # 检查格式
            code_lengths = df['股票代码'].astype(str).str.len()
            unique_lengths = code_lengths.unique()
            print(f"  股票代码长度分布: {sorted(unique_lengths)}")
            
            # 标准化建议
            if 6 not in unique_lengths:
                print(f"⚠️ 建议: 股票代码应补足6位")
        
        # 检查数值字段
        numeric_fields = ['持仓数量', '成本价']
        for field in numeric_fields:
            if field in df.columns:
                print(f"\n💰 {field}分析:")
                print(f"  最小值: {df[field].min()}")
                print(f"  最大值: {df[field].max()}")
                print(f"  平均值: {df[field].mean():.2f}")
                print(f"  中位数: {df[field].median():.2f}")
        
        return df
        
    except Exception as e:
        print(f"❌ 读取Excel文件失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def prepare_for_analysis(df):
    """准备数据用于分析"""
    print("\n🛠️ 准备分析数据...")
    
    if df is None:
        print("❌ 数据为空")
        return None
    
    # 创建副本
    analysis_df = df.copy()
    
    # 标准化股票代码
    if '股票代码' in analysis_df.columns:
        print("标准化股票代码...")
        analysis_df['股票代码'] = analysis_df['股票代码'].astype(str).str.zfill(6)
        print(f"标准化后示例: {analysis_df['股票代码'].head(3).tolist()}")
    
    # 检查并添加缺失字段
    if '行业分类' not in analysis_df.columns:
        print("添加行业分类字段...")
        analysis_df['行业分类'] = ''  # 空字段，系统会自动匹配
    
    # 确保数值字段类型正确
    numeric_fields = ['持仓数量', '成本价']
    for field in numeric_fields:
        if field in analysis_df.columns:
            analysis_df[field] = pd.to_numeric(analysis_df[field], errors='coerce')
    
    print(f"准备后的数据形状: {analysis_df.shape}")
    print(f"准备后的列名: {list(analysis_df.columns)}")
    
    return analysis_df

def save_for_analysis(df, output_path):
    """保存为分析用文件"""
    print(f"\n💾 保存分析数据...")
    
    try:
        # 保存为CSV格式（更稳定）
        csv_path = output_path.replace('.xlsx', '.csv')
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"✅ 保存为CSV: {csv_path}")
        print(f"   文件大小: {os.path.getsize(csv_path)} bytes")
        
        # 也保存为Excel格式
        df.to_excel(output_path, index=False)
        print(f"✅ 保存为Excel: {output_path}")
        print(f"   文件大小: {os.path.getsize(output_path)} bytes")
        
        return csv_path, output_path
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return None, None

def main():
    print("=" * 70)
    print("持仓明细文件检查")
    print("=" * 70)
    
    # 文件路径
    source_file = "/Users/tuqibiao/.openclaw/workspace/position_analysis/data/client_portfolio.xlsx"
    analysis_file = "/Users/tuqibiao/.openclaw/workspace/position_analysis/data/analysis_portfolio.xlsx"
    
    # 检查原始文件
    df = check_excel_file(source_file)
    
    if df is not None:
        # 准备分析数据
        analysis_df = prepare_for_analysis(df)
        
        if analysis_df is not None:
            # 保存分析数据
            csv_path, excel_path = save_for_analysis(analysis_df, analysis_file)
            
            print("\n" + "=" * 70)
            print("文件检查完成")
            print("=" * 70)
            
            if csv_path and excel_path:
                print("✅ 文件准备就绪，可以开始分析")
                print(f"\n📁 可用文件:")
                print(f"  1. 原始文件: {source_file}")
                print(f"  2. 分析用CSV: {csv_path}")
                print(f"  3. 分析用Excel: {excel_path}")
                
                print(f"\n🚀 运行分析命令:")
                print(f"cd /Users/tuqibiao/.openclaw/workspace/position_analysis/src")
                print(f"python main.py ../data/analysis_portfolio.csv --client-name \"客户\"")
            else:
                print("⚠️ 文件保存失败")
        else:
            print("❌ 数据准备失败")
    else:
        print("❌ 文件读取失败")
    
    print(f"\n工作目录: {os.getcwd()}")

if __name__ == "__main__":
    main()