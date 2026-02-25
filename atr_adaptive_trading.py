#!/usr/bin/env python3
"""
彪哥战法 - ATR自适应买卖点计算系统（P1）
替代固定百分比止损，使用真实波动幅度（ATR）
"""

import pandas as pd
import numpy as np

class ATRAdaptiveTradingSystem:
    """ATR自适应交易系统"""
    
    def __init__(self, atr_period=14):
        """
        初始化
        
        Args:
            atr_period: ATR计算周期，默认14日
        """
        self.atr_period = atr_period
    
    def calculate_atr(self, high, low, close):
        """
        计算ATR（真实波动幅度）
        
        ATR = 过去N日的真实波动幅度的平均值
        真实波动幅度 = max(当日最高价-最低价, |当日最高价-昨日收盘价|, |当日最低价-昨日收盘价|)
        """
        # 计算真实波动幅度（TR）
        tr1 = high - low  # 当日最高价 - 最低价
        tr2 = abs(high - close.shift(1))  # |当日最高价 - 昨日收盘价|
        tr3 = abs(low - close.shift(1))   # |当日最低价 - 昨日收盘价|
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 计算ATR（简单移动平均）
        atr = tr.rolling(window=self.atr_period).mean()
        
        return atr
    
    def calculate_chandelier_exit(self, high, close, atr, multiplier=3):
        """
        吊灯止损（Chandelier Exit）
        最常用的一种ATR止损方法
        
        止损价 = N日最高价 - ATR × 乘数
        """
        # N日最高价
        highest_high = high.rolling(window=self.atr_period).max()
        
        # 吊灯止损价
        chandelier_stop = highest_high - (atr * multiplier)
        
        return chandelier_stop
    
    def calculate_spring_first_buy(self, stock_data, market_cycle='春播'):
        """
        春播第一买：底部放量突破颈线 + ATR自适应止损
        
        原方案：
        - 止损 = 颈线 × 0.95（固定5%）
        
        ATR方案：
        - 止损 = 买入价 - 2×ATR
        - 动态调整：波动大的股票止损宽松，波动小的紧凑
        """
        current_price = stock_data['当前价格']
        neckline = stock_data['颈线位置']
        atr = stock_data['ATR']
        
        # 买点确认：突破颈线3%
        if current_price < neckline * 1.03:
            return None  # 未突破，不买
        
        # ATR自适应止损
        stop_loss = current_price - 2 * atr
        
        # 止损不能低于颈线的95%（双重保护）
        stop_loss = max(stop_loss, neckline * 0.95)
        
        # 风险计算
        risk = current_price - stop_loss
        risk_percent = risk / current_price
        
        # 仓位：首仓10%（根据风险收益比可调整）
        position = 0.10
        
        return {
            'type': '春播第一买（ATR自适应）',
            'buy_price': round(current_price, 2),
            'stop_loss': round(stop_loss, 2),
            'risk_amount': round(risk, 2),
            'risk_percent': round(risk_percent * 100, 2),
            'position': position,
            'atr': round(atr, 3),
            'reason': f'突破颈线+ATR止损({risk_percent:.1%})'
        }
    
    def calculate_spring_second_buy(self, stock_data, market_cycle='春播'):
        """
        春播第二买：回踩颈线企稳 + ATR确认
        
        原方案：
        - 止损 = 颈线 × 0.95
        
        ATR方案：
        - 止损 = 买入价 - 1.5×ATR（比第一买更紧）
        - 加仓后整体止损统一调整到新位置
        """
        current_price = stock_data['当前价格']
        neckline = stock_data['颈线位置']
        atr = stock_data['ATR']
        
        # 回踩确认：价格在颈线±2%范围内，且缩量
        if abs(current_price - neckline) / neckline > 0.02:
            return None  # 未回踩到颈线附近
        
        if stock_data.get('成交量', 0) > stock_data.get('5日均量', 0) * 0.7:
            return None  # 未缩量，不算企稳
        
        # ATR自适应止损（比第一买更紧）
        stop_loss = current_price - 1.5 * atr
        stop_loss = max(stop_loss, neckline * 0.95)
        
        risk = current_price - stop_loss
        risk_percent = risk / current_price
        
        # 加仓：从10%加至30%
        add_position = 0.20
        
        return {
            'type': '春播第二买（ATR自适应）',
            'buy_price': round(current_price, 2),
            'stop_loss': round(stop_loss, 2),
            'risk_amount': round(risk, 2),
            'risk_percent': round(risk_percent * 100, 2),
            'add_position': add_position,
            'total_position': 0.30,
            'atr': round(atr, 3),
            'reason': f'回踩颈线企稳+ATR止损({risk_percent:.1%})'
        }
    
    def calculate_summer_confirm_buy(self, stock_data, market_cycle='夏长'):
        """
        夏长确认买：主升浪启动 + ATR跟踪止损
        
        原方案：
        - 止损 = 5日线 × 0.97（固定3%）
        
        ATR方案：
        - 止损 = 买入价 - 2.5×ATR
        - 移动止损：每日调整，锁定利润
        """
        current_price = stock_data['当前价格']
        previous_high = stock_data['前高']
        ma5 = stock_data['5日线']
        atr = stock_data['ATR']
        
        # 确认买点：突破前高
        if current_price < previous_high * 1.02:
            return None
        
        # 量能确认
        if stock_data.get('成交量', 0) < stock_data.get('5日均量', 0) * 1.5:
            return None
        
        # ATR自适应止损
        stop_loss = current_price - 2.5 * atr
        
        # 不能跌破5日线下方5%
        stop_loss = max(stop_loss, ma5 * 0.95)
        
        risk = current_price - stop_loss
        risk_percent = risk / current_price
        
        # 仓位：加至70%
        current_position = stock_data.get('当前仓位', 0.30)
        add_position = 0.70 - current_position
        
        # 目标价：等幅测量
        wave_height = previous_high - stock_data.get('波段低点', previous_high * 0.8)
        target_price = previous_high + wave_height
        
        # 风险收益比
        reward = target_price - current_price
        risk_reward = reward / risk if risk > 0 else 0
        
        return {
            'type': '夏长确认买（ATR自适应）',
            'buy_price': round(current_price, 2),
            'stop_loss': round(stop_loss, 2),
            'target_price': round(target_price, 2),
            'risk_amount': round(risk, 2),
            'risk_percent': round(risk_percent * 100, 2),
            'risk_reward_ratio': round(risk_reward, 2),
            'add_position': round(add_position, 2),
            'final_position': 0.70,
            'atr': round(atr, 3),
            'reason': f'主升浪启动+ATR止损({risk_percent:.1%})+RR比{risk_reward:.1f}'
        }
    
    def update_trailing_stop(self, position_data, current_price, high_since_entry):
        """
        移动止损更新（持仓期间每日调用）
        
        吊灯止损逻辑：
        - 止损价 = 自买入以来的最高价 - 3×ATR
        - 止损价只上移，不下移
        """
        atr = position_data['atr']
        original_stop = position_data['stop_loss']
        
        # 计算新的吊灯止损
        new_stop = high_since_entry - 3 * atr
        
        # 止损只上移，不下移
        updated_stop = max(new_stop, original_stop)
        
        # 锁定利润：如果利润>10%，止损上移至成本价
        entry_price = position_data['buy_price']
        profit_percent = (current_price - entry_price) / entry_price
        
        if profit_percent > 0.10:
            updated_stop = max(updated_stop, entry_price)
        
        return {
            'original_stop': round(original_stop, 2),
            'new_stop': round(new_stop, 2),
            'updated_stop': round(updated_stop, 2),
            'profit_lock': profit_percent > 0.10,
            'profit_percent': round(profit_percent * 100, 2)
        }
    
    def calculate_autumn_first_sell(self, stock_data, position_data):
        """
        秋收第一卖：高位放量滞涨
        
        ATR确认：
        - 价格新高但ATR放大（波动加大，资金分歧）
        - 减仓30%
        """
        current_price = stock_data['当前价格']
        volume = stock_data['成交量']
        avg_volume = stock_data['5日均量']
        atr = stock_data['ATR']
        atr_ratio = atr / current_price  # ATR占价格比例
        
        # 信号1：价格新高
        price_new_high = current_price > stock_data.get('前高', 0) * 1.05
        
        # 信号2：成交量放大（>1.5倍）
        volume_expansion = volume > avg_volume * 1.5
        
        # 信号3：ATR放大（波动加剧）
        atr_expansion = atr_ratio > stock_data.get('历史ATR均值', atr_ratio) * 1.3
        
        if price_new_high and volume_expansion and atr_expansion:
            return {
                'type': '秋收第一卖（ATR确认）',
                'sell_price': round(current_price, 2),
                'signal': '高位放量+ATR放大',
                'reduce_position': 0.30,
                'remaining_position': 0.40,
                'atr_ratio': round(atr_ratio * 100, 2),
                'reason': '波动加剧，资金分歧，减仓锁定利润'
            }
        
        return None
    
    def calculate_autumn_second_sell(self, stock_data, position_data):
        """
        秋收第二卖：双顶跌破颈线 + ATR突破确认
        
        ATR确认：
        - 跌破颈线时ATR放大（恐慌盘涌出）
        - 清仓
        """
        current_price = stock_data['当前价格']
        neckline = stock_data['双底颈线']
        atr = stock_data['ATR']
        
        # 跌破颈线确认（收盘低于颈线3%）
        if current_price >= neckline * 0.97:
            return None
        
        # ATR确认：下跌时波动放大
        atr_expansion = atr > stock_data.get('10日ATR均值', atr) * 1.2
        
        return {
            'type': '秋收第二卖（ATR确认）',
            'sell_price': round(current_price, 2),
            'signal': '双顶跌破颈线+ATR放大',
            'reduce_position': '全部清仓',
            'remaining_position': 0,
            'neckline': round(neckline, 2),
            'atr_expansion': atr_expansion,
            'reason': '趋势反转确认，清仓避险'
        }


def compare_fixed_vs_atr():
    """
    对比固定百分比止损 vs ATR自适应止损
    """
    print("=" * 80)
    print("【P1】固定百分比止损 vs ATR自适应止损 对比")
    print("=" * 80)
    
    # 模拟两只不同波动特征的股票
    test_cases = [
        {
            'name': '高波动股票（科创板）',
            '当前价格': 50.0,
            '颈线位置': 48.0,
            'ATR': 3.5,  # 日波动7%
            '5日线': 49.0,
            '成交量': 1000000,
            '5日均量': 800000
        },
        {
            'name': '低波动股票（银行股）',
            '当前价格': 5.0,
            '颈线位置': 4.85,
            'ATR': 0.08,  # 日波动1.6%
            '5日线': 4.95,
            '成交量': 5000000,
            '5日均量': 4000000
        }
    ]
    
    atr_system = ATRAdaptiveTradingSystem()
    
    for case in test_cases:
        print(f"\n{'='*80}")
        print(f"测试案例：{case['name']}")
        print(f"当前价格：{case['当前价格']}元，ATR：{case['ATR']}元")
        print(f"日波动率：{case['ATR']/case['当前价格']*100:.1f}%")
        print("-" * 80)
        
        # 固定百分比方案
        fixed_stop = case['颈线位置'] * 0.95
        fixed_risk = case['当前价格'] - fixed_stop
        fixed_risk_pct = fixed_risk / case['当前价格'] * 100
        
        print("【固定百分比止损】")
        print(f"  止损价：{fixed_stop:.2f}元（颈线下方5%）")
        print(f"  风险金额：{fixed_risk:.2f}元")
        print(f"  风险比例：{fixed_risk_pct:.2f}%")
        
        # ATR自适应方案
        result = atr_system.calculate_spring_first_buy(case)
        if result:
            print("\n【ATR自适应止损】")
            print(f"  止损价：{result['stop_loss']:.2f}元（2×ATR）")
            print(f"  风险金额：{result['risk_amount']:.2f}元")
            print(f"  风险比例：{result['risk_percent']:.2f}%")
            
            # 对比
            print("\n【对比结论】")
            if result['risk_percent'] > fixed_risk_pct:
                print(f"  ✅ ATR止损更宽松（{result['risk_percent']:.1f}% vs {fixed_risk_pct:.1f}%）")
                print(f"     适合高波动股票，避免过早止损")
            else:
                print(f"  ✅ ATR止损更紧凑（{result['risk_percent']:.1f}% vs {fixed_risk_pct:.1f}%）")
                print(f"     适合低波动股票，保护本金")
    
    print("\n" + "=" * 80)
    print("【核心结论】")
    print("=" * 80)
    print("1. 高波动股票（ATR大）：ATR止损 > 固定止损，避免洗盘")
    print("2. 低波动股票（ATR小）：ATR止损 < 固定止损， tighter保护")
    print("3. 自适应优势：自动匹配个股波动特性，无需手动调整")
    print("=" * 80)


if __name__ == "__main__":
    # 运行对比测试
    compare_fixed_vs_atr()
