#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓数据导入与清洗模块
基础层：数据导入、验证、标准化处理
"""

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PortfolioDataImporter:
    """持仓数据导入器"""
    
    def __init__(self):
        """初始化导入器"""
        self.required_columns = ['股票代码', '股票名称', '持仓数量', '成本价']
        self.optional_columns = ['行业分类', '买入日期', '备注']
        self.portfolio_data = None
        self.validation_errors = []
        
    def import_from_excel(self, file_path):
        """
        从Excel文件导入持仓数据
        
        Args:
            file_path (str): Excel文件路径
            
        Returns:
            pandas.DataFrame: 处理后的持仓数据
        """
        try:
            logger.info(f"开始导入Excel文件: {file_path}")
            
            # 读取Excel文件
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            else:
                raise ValueError("不支持的文件格式，请使用.xlsx、.xls或.csv格式")
            
            # 验证数据
            self._validate_data(df)
            
            # 数据清洗
            df_cleaned = self._clean_data(df)
            
            # 数据标准化
            df_standardized = self._standardize_data(df_cleaned)
            
            self.portfolio_data = df_standardized
            logger.info(f"成功导入 {len(df_standardized)} 条持仓记录")
            
            return df_standardized
            
        except Exception as e:
            logger.error(f"导入Excel文件失败: {str(e)}")
            raise
    
    def import_manual_entry(self, entries):
        """
        手动录入持仓数据
        
        Args:
            entries (list): 持仓记录列表，每条记录为字典格式
            
        Returns:
            pandas.DataFrame: 处理后的持仓数据
        """
        try:
            logger.info(f"开始手动导入 {len(entries)} 条持仓记录")
            
            # 转换为DataFrame
            df = pd.DataFrame(entries)
            
            # 验证数据
            self._validate_data(df)
            
            # 数据清洗
            df_cleaned = self._clean_data(df)
            
            # 数据标准化
            df_standardized = self._standardize_data(df_cleaned)
            
            self.portfolio_data = df_standardized
            logger.info(f"成功导入 {len(df_standardized)} 条持仓记录")
            
            return df_standardized
            
        except Exception as e:
            logger.error(f"手动导入失败: {str(e)}")
            raise
    
    def _validate_data(self, df):
        """
        验证数据完整性
        
        Args:
            df (pandas.DataFrame): 原始数据
            
        Raises:
            ValueError: 数据验证失败
        """
        logger.info("开始数据验证...")
        self.validation_errors = []
        
        # 检查必需列
        missing_columns = []
        for col in self.required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            error_msg = f"缺少必需列: {', '.join(missing_columns)}"
            logger.error(error_msg)
            self.validation_errors.append(error_msg)
            raise ValueError(error_msg)
        
        # 检查数据行数
        if len(df) == 0:
            error_msg = "数据文件为空"
            logger.error(error_msg)
            self.validation_errors.append(error_msg)
            raise ValueError(error_msg)
        
        # 检查股票代码格式
        for idx, row in df.iterrows():
            stock_code = str(row['股票代码']).strip()
            if not re.match(r'^\d{6}$', stock_code):
                error_msg = f"第{idx+1}行股票代码格式错误: {stock_code} (应为6位数字)"
                logger.warning(error_msg)
                self.validation_errors.append(error_msg)
        
        # 检查持仓数量是否为数值
        for idx, row in df.iterrows():
            try:
                quantity = float(row['持仓数量'])
                if quantity <= 0:
                    error_msg = f"第{idx+1}行持仓数量必须大于0: {quantity}"
                    logger.warning(error_msg)
                    self.validation_errors.append(error_msg)
            except:
                error_msg = f"第{idx+1}行持仓数量不是有效数值: {row['持仓数量']}"
                logger.warning(error_msg)
                self.validation_errors.append(error_msg)
        
        # 检查成本价是否为数值
        for idx, row in df.iterrows():
            try:
                cost = float(row['成本价'])
                if cost <= 0:
                    error_msg = f"第{idx+1}行成本价必须大于0: {cost}"
                    logger.warning(error_msg)
                    self.validation_errors.append(error_msg)
            except:
                error_msg = f"第{idx+1}行成本价不是有效数值: {row['成本价']}"
                logger.warning(error_msg)
                self.validation_errors.append(error_msg)
        
        if self.validation_errors:
            logger.warning(f"数据验证发现 {len(self.validation_errors)} 个问题")
        else:
            logger.info("数据验证通过")
    
    def _clean_data(self, df):
        """
        数据清洗
        
        Args:
            df (pandas.DataFrame): 原始数据
            
        Returns:
            pandas.DataFrame: 清洗后的数据
        """
        logger.info("开始数据清洗...")
        
        # 创建副本
        df_clean = df.copy()
        
        # 处理股票代码：去除空格，补全6位
        df_clean['股票代码'] = df_clean['股票代码'].astype(str).str.strip()
        df_clean['股票代码'] = df_clean['股票代码'].apply(lambda x: x.zfill(6))
        
        # 处理股票名称：去除空格
        df_clean['股票名称'] = df_clean['股票名称'].astype(str).str.strip()
        
        # 处理持仓数量：转换为整数
        df_clean['持仓数量'] = pd.to_numeric(df_clean['持仓数量'], errors='coerce').fillna(0).astype(int)
        
        # 处理成本价：转换为浮点数
        df_clean['成本价'] = pd.to_numeric(df_clean['成本价'], errors='coerce').fillna(0)
        
        # 处理行业分类：如果有缺失，留空后续自动匹配
        if '行业分类' in df_clean.columns:
            df_clean['行业分类'] = df_clean['行业分类'].astype(str).str.strip()
            df_clean['行业分类'] = df_clean['行业分类'].replace(['nan', 'None', 'null', ''], np.nan)
        
        # 处理买入日期：转换为日期格式
        if '买入日期' in df_clean.columns:
            try:
                df_clean['买入日期'] = pd.to_datetime(df_clean['买入日期'], errors='coerce')
            except:
                logger.warning("买入日期格式转换失败，将保留原始格式")
        
        # 处理备注：去除空格
        if '备注' in df_clean.columns:
            df_clean['备注'] = df_clean['备注'].astype(str).str.strip()
        
        logger.info(f"数据清洗完成，共处理 {len(df_clean)} 条记录")
        return df_clean
    
    def _standardize_data(self, df):
        """
        数据标准化
        
        Args:
            df (pandas.DataFrame): 清洗后的数据
            
        Returns:
            pandas.DataFrame: 标准化后的数据
        """
        logger.info("开始数据标准化...")
        
        # 创建副本
        df_std = df.copy()
        
        # 添加计算列
        df_std['持仓市值'] = df_std['持仓数量'] * df_std['成本价']
        
        # 添加唯一标识
        df_std['记录ID'] = range(1, len(df_std) + 1)
        
        # 添加导入时间
        df_std['导入时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 重新排列列顺序
        columns_order = ['记录ID', '股票代码', '股票名称', '行业分类', '持仓数量', '成本价', '持仓市值']
        
        # 添加其他可选列
        for col in ['买入日期', '备注', '导入时间']:
            if col in df_std.columns:
                columns_order.append(col)
        
        # 只保留存在的列
        columns_order = [col for col in columns_order if col in df_std.columns]
        
        df_std = df_std[columns_order]
        
        logger.info("数据标准化完成")
        return df_std
    
    def get_validation_report(self):
        """
        获取数据验证报告
        
        Returns:
            dict: 验证报告
        """
        report = {
            'total_records': len(self.portfolio_data) if self.portfolio_data is not None else 0,
            'validation_errors': self.validation_errors,
            'error_count': len(self.validation_errors),
            'has_errors': len(self.validation_errors) > 0,
            'portfolio_summary': self._get_portfolio_summary()
        }
        return report
    
    def _get_portfolio_summary(self):
        """
        获取持仓数据摘要
        
        Returns:
            dict: 持仓摘要
        """
        if self.portfolio_data is None or len(self.portfolio_data) == 0:
            return {}
        
        df = self.portfolio_data
        summary = {
            'total_stocks': len(df),
            'total_quantity': int(df['持仓数量'].sum()),
            'total_market_value': float(df['持仓市值'].sum()),
            'avg_cost_price': float(df['成本价'].mean()),
            'max_position_stock': df.loc[df['持仓市值'].idxmax(), '股票名称'] if '持仓市值' in df.columns else None,
            'max_position_value': float(df['持仓市值'].max()) if '持仓市值' in df.columns else None,
            'unique_industries': len(df['行业分类'].unique()) if '行业分类' in df.columns else 0
        }
        return summary
    
    def save_cleaned_data(self, output_path):
        """
        保存清洗后的数据
        
        Args:
            output_path (str): 输出文件路径
            
        Returns:
            bool: 是否保存成功
        """
        if self.portfolio_data is None:
            logger.error("没有可保存的数据，请先导入数据")
            return False
        
        try:
            # 根据文件后缀选择保存格式
            if output_path.endswith('.csv'):
                self.portfolio_data.to_csv(output_path, index=False, encoding='utf-8-sig')
            elif output_path.endswith('.xlsx'):
                self.portfolio_data.to_excel(output_path, index=False)
            else:
                # 默认保存为CSV
                output_path = output_path + '.csv'
                self.portfolio_data.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            logger.info(f"数据已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存数据失败: {str(e)}")
            return False


# 示例使用
if __name__ == "__main__":
    # 示例：导入数据
    importer = PortfolioDataImporter()
    
    # 从CSV文件导入
    sample_file = "../data/sample_portfolio.csv"
    if os.path.exists(sample_file):
        portfolio_df = importer.import_from_excel(sample_file)
        
        # 打印摘要
        summary = importer.get_validation_report()
        print("数据验证报告:")
        print(f"总记录数: {summary['total_records']}")
        print(f"验证错误数: {summary['error_count']}")
        print(f"持仓摘要: {summary['portfolio_summary']}")
        
        # 保存清洗后的数据
        importer.save_cleaned_data("../outputs/cleaned_portfolio.csv")
    else:
        print(f"示例文件不存在: {sample_file}")
        print("请先创建示例数据文件")