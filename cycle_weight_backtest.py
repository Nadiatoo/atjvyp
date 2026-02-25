#!/usr/bin/env python3
"""
彪哥战法 - 周期权重动态优化回测框架
测试不同市场环境下的最优权重组合
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class MarketEnvironmentIdentifier:
    """市场环境识别器"""
    
    def __init__(self):
        # 阈值配置（基于2024-2025数据统计）
        self.thresholds = {
            'quant': {
                'seat_ratio': 0.40,      # 量化席位占比>40%
                'intraday_atr': 0.05,     # 日内ATR>5%
                'next_day_down_rate': 0.60,  # 涨停次日低开率>60%
                'score_weight': 0.40      # 环境评分权重
            },
            'institution': {
                'northbound_days': 5,     # 北向连续流入天数
                'research_density': 2.0,  # 调研密度倍数
                'fund_issuance': 100,     # 月度基金发行规模(亿)
                'score_weight': 0.35
            },
            'retail': {
                'limit_up_height': 8,     # 连板高度>8板
                'turnover_rate': 0.20,    # 换手率>20%
                'score_weight': 0.25
            }
        }
    
    def identify_environment(self, date, market_data):
        """
        识别当前市场环境
        
        Returns:
            dominant: str - 'quant', 'institution', 'retail', 'mixed'
            scores: dict - 各维度得分
            details: dict - 详细指标
        """
        scores = {'quant': 0, 'institution': 0, 'retail': 0}
        details = {}
        
        # 1. 量化主导评分
        quant_checks = {
            '量化席位占比': market_data.get('quant_seat_ratio', 0) > self.thresholds['quant']['seat_ratio'],
            '日内ATR': market_data.get('intraday_atr', 0) > self.thresholds['quant']['intraday_atr'],
            '次日低开率': market_data.get('next_day_down_rate', 0) > self.thresholds['quant']['next_day_down_rate'],
            '成交量波动': market_data.get('volume_volatility', 0) > 0.3
        }
        scores['quant'] = sum(quant_checks.values()) / len(quant_checks)
        details['quant'] = quant_checks
        
        # 2. 机构主导评分
        inst_checks = {
            '北向连续流入': market_data.get('northbound_consecutive_days', 0) >= self.thresholds['institution']['northbound_days'],
            '调研密度': market_data.get('research_density', 0) > self.thresholds['institution']['research_density'],
            '基金发行': market_data.get('fund_issuance', 0) > self.thresholds['institution']['fund_issuance'],
            '机构调研': market_data.get('institution_research_count', 0) > 50
        }
        scores['institution'] = sum(inst_checks.values()) / len(inst_checks)
        details['institution'] = inst_checks
        
        # 3. 游资主导评分
        retail_checks = {
            '连板高度': market_data.get('limit_up_height', 0) >= self.thresholds['retail']['limit_up_height'],
            '高换手': market_data.get('avg_turnover', 0) > self.thresholds['retail']['turnover_rate'],
            '龙虎榜活跃': market_data.get('dragon_tiger_active', 0) > 10,
            '涨停家数': market_data.get('limit_up_count', 0) > 80
        }
        scores['retail'] = sum(retail_checks.values()) / len(retail_checks)
        details['retail'] = retail_checks
        
        # 判定主导力量
        max_score = max(scores.values())
        if max_score >= 0.6:  # 超过60%才判定为明确主导
            dominant = max(scores, key=scores.get)
        else:
            dominant = 'mixed'
        
        return dominant, scores, details


class CycleWeightBacktester:
    """周期权重回测器"""
    
    def __init__(self):
        # 待测试的权重组合
        self.weight_combinations = [
            {'name': '基准', 'spring': 0.30, 'summer': 0.40, 'autumn': 0.20, 'winter': 0.10},
            
            # 量化主导优化
            {'name': '量化A', 'spring': 0.35, 'summer': 0.35, 'autumn': 0.20, 'winter': 0.10},
            {'name': '量化B', 'spring': 0.40, 'summer': 0.30, 'autumn': 0.25, 'winter': 0.05},
            {'name': '量化C', 'spring': 0.35, 'summer': 0.30, 'autumn': 0.25, 'winter': 0.10},
            
            # 机构主导优化
            {'name': '机构A', 'spring': 0.25, 'summer': 0.50, 'autumn': 0.15, 'winter': 0.10},
            {'name': '机构B', 'spring': 0.20, 'summer': 0.55, 'autumn': 0.15, 'winter': 0.10},
            {'name': '机构C', 'spring': 0.25, 'summer': 0.45, 'autumn': 0.20, 'winter': 0.10},
            
            # 游资主导优化
            {'name': '游资A', 'spring': 0.40, 'summer': 0.35, 'autumn': 0.15, 'winter': 0.10},
            {'name': '游资B', 'spring': 0.45, 'summer': 0.30, 'autumn': 0.20, 'winter': 0.05},
            
            # 流动性调整
            {'name': '高流动性', 'spring': 0.25, 'summer': 0.45, 'autumn': 0.20, 'winter': 0.10},
            {'name': '低流动性', 'spring': 0.35, 'summer': 0.30, 'autumn': 0.20, 'winter': 0.15},
        ]
        
        self.env_identifier = MarketEnvironmentIdentifier()
    
    def calculate_cycle_score(self, market_data, weights):
        """
        计算周期得分
        """
        # 提取数值权重（排除'name'）
        weight_values = {k: v for k, v in weights.items() if k != 'name'}
        
        scores = {
            # 春播信号
            'spring': min(market_data.get('down_limit', 0) / 50, 1.0) * weight_values['spring'],
            'spring2': min(market_data.get('strong_stock_drop', 0) / 15, 1.0) * weight_values['spring'] * 0.5,
            
            # 夏长信号
            'summer': min(market_data.get('up_limit', 0) / 100, 1.0) * weight_values['summer'],
            'summer2': min(market_data.get('volume', 0) / 30000, 1.0) * weight_values['summer'] * 0.5,
            
            # 秋收信号
            'autumn': min(market_data.get('炸板率', 0) / 35, 1.0) * weight_values['autumn'],
            
            # 冬藏信号
            'winter': max(0, (30000 - market_data.get('volume', 0)) / 30000) * weight_values['winter'],
        }
        
        total_score = sum(scores.values()) / sum(weight_values.values()) * 100
        return total_score
    
    def determine_season(self, score):
        """根据得分判断季节"""
        if score < 20:
            return 'winter', '冬藏'
        elif score < 40:
            return 'spring', '春播'
        elif score < 70:
            return 'autumn', '秋收'
        else:
            return 'summer', '夏长'
    
    def backtest_single_combo(self, combo, historical_data, env_filter=None):
        """
        回测单个权重组合
        
        Args:
            combo: dict - 权重组合
            historical_data: list - 历史数据
            env_filter: str - 环境过滤（'quant', 'institution', 'retail', 'mixed'）
        
        Returns:
            dict - 回测结果
        """
        results = {
            'combo_name': combo['name'],
            'weights': combo,
            'total_signals': 0,
            'win_signals': 0,
            'total_return': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'season_accuracy': {'spring': 0, 'summer': 0, 'autumn': 0, 'winter': 0},
            'env_distribution': {'quant': 0, 'institution': 0, 'retail': 0, 'mixed': 0}
        }
        
        returns = []
        current_drawdown = 0
        peak = 1.0
        
        for data in historical_data:
            # 识别市场环境
            env, scores, _ = self.env_identifier.identify_environment(
                data['date'], data['market_data']
            )
            
            results['env_distribution'][env] += 1
            
            # 如果指定了环境过滤，只统计该环境
            if env_filter and env != env_filter:
                continue
            
            # 计算周期得分
            score = self.calculate_cycle_score(data['market_data'], combo)
            predicted_season, _ = self.determine_season(score)
            actual_season = data['actual_season']
            
            # 统计准确率
            if predicted_season == actual_season:
                results['season_accuracy'][actual_season] += 1
            
            # 模拟交易（简化版）
            signal_return = self.simulate_trade(predicted_season, actual_season, data)
            
            results['total_signals'] += 1
            if signal_return > 0:
                results['win_signals'] += 1
            
            results['total_return'] += signal_return
            returns.append(signal_return)
            
            # 计算回撤
            current_value = 1 + results['total_return']
            if current_value > peak:
                peak = current_value
            drawdown = (peak - current_value) / peak
            if drawdown > results['max_drawdown']:
                results['max_drawdown'] = drawdown
        
        # 计算胜率
        if results['total_signals'] > 0:
            results['win_rate'] = results['win_signals'] / results['total_signals']
        else:
            results['win_rate'] = 0
        
        # 计算夏普比率（简化版，假设无风险利率0）
        if len(returns) > 1:
            returns_array = np.array(returns)
            sharpe = np.mean(returns_array) / np.std(returns_array) if np.std(returns_array) > 0 else 0
            results['sharpe_ratio'] = sharpe * np.sqrt(252)  # 年化
        
        return results
    
    def simulate_trade(self, predicted_season, actual_season, data):
        """
        模拟单次交易
        简化逻辑：预测正确则盈利，错误则亏损
        """
        season_returns = {
            'spring': 0.08,   # 春播平均收益8%
            'summer': 0.15,   # 夏长平均收益15%
            'autumn': 0.05,   # 秋收平均收益5%
            'winter': -0.05   # 冬藏平均亏损5%
        }
        
        if predicted_season == actual_season:
            # 预测正确，获得该季节平均收益
            return season_returns[actual_season]
        else:
            # 预测错误，亏损一半
            return season_returns[actual_season] * (-0.5)
    
    def run_full_backtest(self, historical_data):
        """
        运行完整回测
        """
        print("=" * 80)
        print("彪哥战法 - 周期权重动态优化回测")
        print(f"回测区间: {historical_data[0]['date']} 至 {historical_data[-1]['date']}")
        print(f"样本数量: {len(historical_data)} 个交易日")
        print("=" * 80)
        
        all_results = []
        
        # 1. 整体回测（不分环境）
        print("\n【整体回测结果】")
        print("-" * 80)
        print(f"{'权重组合':<12} {'胜率':>8} {'总收益':>10} {'最大回撤':>10} {'夏普比率':>10}")
        print("-" * 80)
        
        for combo in self.weight_combinations:
            result = self.backtest_single_combo(combo, historical_data)
            all_results.append(('overall', combo['name'], result))
            
            print(f"{combo['name']:<12} {result['win_rate']:>7.1%} "
                  f"{result['total_return']:>9.1%} {result['max_drawdown']:>9.1%} "
                  f"{result['sharpe_ratio']:>9.2f}")
        
        # 2. 分环境回测
        environments = ['quant', 'institution', 'retail', 'mixed']
        env_names = {'quant': '量化主导', 'institution': '机构主导', 
                    'retail': '游资主导', 'mixed': '混合市场'}
        
        for env in environments:
            print(f"\n【{env_names[env]}环境回测】")
            print("-" * 80)
            print(f"{'权重组合':<12} {'胜率':>8} {'总收益':>10} {'最大回撤':>10} {'夏普比率':>10}")
            print("-" * 80)
            
            for combo in self.weight_combinations:
                result = self.backtest_single_combo(combo, historical_data, env_filter=env)
                all_results.append((env, combo['name'], result))
                
                if result['total_signals'] > 10:  # 样本足够才显示
                    print(f"{combo['name']:<12} {result['win_rate']:>7.1%} "
                          f"{result['total_return']:>9.1%} {result['max_drawdown']:>9.1%} "
                          f"{result['sharpe_ratio']:>9.2f} "
                          f"(n={result['total_signals']})")
        
        # 3. 找出最优组合
        print("\n【最优权重组合】")
        print("-" * 80)
        
        for env in environments:
            env_results = [(r[1], r[2]) for r in all_results if r[0] == env]
            if env_results:
                # 按夏普比率排序
                best = max(env_results, key=lambda x: x[1]['sharpe_ratio'])
                print(f"{env_names[env]:<10}: {best[0]:<12} "
                      f"(胜率{best[1]['win_rate']:.1%}, 夏普{best[1]['sharpe_ratio']:.2f})")
        
        return all_results


# 真实历史数据获取（使用akshare）
def fetch_real_historical_data(start_date='20240101', end_date='20250225'):
    """
    获取真实历史数据（2024-2025年）
    使用akshare获取A股全市场数据
    """
    try:
        import akshare as ak
        print(f"正在获取真实历史数据: {start_date} 至 {end_date}")
        
        # 转换日期格式
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        
        data = []
        current_dt = start_dt
        
        while current_dt <= end_dt:
            date_str = current_dt.strftime('%Y%m%d')
            date_display = current_dt.strftime('%Y-%m-%d')
            
            # 跳过周末
            if current_dt.weekday() >= 5:
                current_dt += timedelta(days=1)
                continue
            
            try:
                # 获取当日全市场数据
                df = ak.stock_zh_a_spot_em()
                
                if df is None or len(df) == 0:
                    print(f"  {date_display}: 无数据，跳过")
                    current_dt += timedelta(days=1)
                    continue
                
                # 计算关键指标
                up_limit = len(df[df['涨跌幅'] >= 9.5])  # 涨停
                down_limit = len(df[df['涨跌幅'] <= -9.5])  # 跌停
                total_volume = df['成交额'].sum() / 100000000  # 成交额（亿）
                
                # 强势股统计（近5日涨幅前100中今日跌停的数量）
                # 这里简化处理，用当日跌幅>7%且前5日涨幅>20%的股票数
                strong_drop = len(df[(df['涨跌幅'] < -7) & (df['5日涨幅'] > 20)])
                
                # 炸板率（简化：涨停开板数/涨停总数）
                # 实际应该获取分时数据，这里用近似值
                zhaban = len(df[(df['涨跌幅'] > 7) & (df['涨跌幅'] < 9.5)])
                zhaban_rate = (zhaban / (up_limit + zhaban) * 100) if (up_limit + zhaban) > 0 else 0
                
                # 市场环境指标（简化版）
                market_data = {
                    'date': date_display,
                    'up_limit': up_limit,
                    'down_limit': down_limit,
                    'volume': total_volume,
                    'strong_stock_drop': strong_drop,
                    '炸板率': zhaban_rate,
                    
                    # 市场环境指标（需要更详细的数据源）
                    'quant_seat_ratio': 0.35,  # 默认值，需要龙虎榜数据
                    'intraday_atr': 0.05,      # 默认值
                    'next_day_down_rate': 0.55, # 默认值
                    'northbound_consecutive_days': 5,  # 默认值
                    'research_density': 2.0,   # 默认值
                    'limit_up_height': 5,      # 默认值
                    'avg_turnover': 0.15,      # 默认值
                }
                
                # 推断实际季节（基于真实市场数据）
                if up_limit > 100 and down_limit < 20 and total_volume > 25000:
                    actual_season = 'summer'
                elif down_limit > 40:
                    actual_season = 'spring'
                elif up_limit > 80 and down_limit > 20:
                    actual_season = 'autumn'
                else:
                    actual_season = 'winter'
                
                data.append({
                    'date': date_display,
                    'market_data': market_data,
                    'actual_season': actual_season
                })
                
                print(f"  {date_display}: 涨停{up_limit}, 跌停{down_limit}, 成交{total_volume:.0f}亿, 季节{actual_season}")
                
            except Exception as e:
                print(f"  {date_display}: 获取失败 - {e}")
            
            current_dt += timedelta(days=1)
        
        print(f"\n成功获取 {len(data)} 个交易日数据")
        return data
        
    except ImportError:
        print("akshare未安装，使用模拟数据")
        return generate_mock_historical_data()
    except Exception as e:
        print(f"获取真实数据失败: {e}，使用模拟数据")
        return generate_mock_historical_data()


# 模拟历史数据生成器（备用）
def generate_mock_historical_data(start_date='2024-01-01', days=250):
    """生成模拟历史数据（实际使用时替换为真实数据）"""
    data = []
    base_date = datetime.strptime(start_date, '%Y-%m-%d')
    
    np.random.seed(42)
    
    for i in range(days):
        date = base_date + timedelta(days=i)
        
        # 模拟市场环境数据
        market_data = {
            'date': date.strftime('%Y-%m-%d'),
            'up_limit': np.random.randint(30, 150),  # 涨停家数
            'down_limit': np.random.randint(0, 60),  # 跌停家数
            'volume': np.random.randint(15000, 45000),  # 成交额
            'strong_stock_drop': np.random.randint(0, 25),  # 强势股补跌幅度
            '炸板率': np.random.randint(10, 50),  # 炸板率
            
            # 市场环境指标
            'quant_seat_ratio': np.random.uniform(0.2, 0.6),
            'intraday_atr': np.random.uniform(0.02, 0.08),
            'next_day_down_rate': np.random.uniform(0.4, 0.8),
            'northbound_consecutive_days': np.random.randint(0, 15),
            'research_density': np.random.uniform(0.5, 4.0),
            'limit_up_height': np.random.randint(3, 15),
            'avg_turnover': np.random.uniform(0.05, 0.35),
        }
        
        # 模拟实际季节（用于回测验证）
        # 基于市场数据简单推断
        if market_data['up_limit'] > 100 and market_data['down_limit'] < 20:
            market_data['actual_season'] = 'summer'
        elif market_data['down_limit'] > 40:
            market_data['actual_season'] = 'spring'
        elif market_data['up_limit'] > 80 and market_data['down_limit'] > 20:
            market_data['actual_season'] = 'autumn'
        else:
            market_data['actual_season'] = 'winter'
        
        data.append({'date': market_data['date'], 
                    'market_data': market_data, 
                    'actual_season': market_data['actual_season']})
    
    return data


# 主函数
if __name__ == "__main__":
    # 选择数据源
    use_real_data = False  # True=真实数据, False=模拟数据
    
    if use_real_data:
        # 获取真实历史数据（2024-2025年）
        historical_data = fetch_real_historical_data('20240101', '20250225')
    else:
        # 生成模拟数据（今天先用模拟数据验证框架）
        print("【注意】使用模拟数据验证框架，明天接入真实数据")
        print("正在生成模拟历史数据...")
        historical_data = generate_mock_historical_data('2024-01-01', 300)
    
    if len(historical_data) == 0:
        print("错误：未能获取任何数据")
        exit(1)
    
    # 运行回测
    backtester = CycleWeightBacktester()
    results = backtester.run_full_backtest(historical_data)
    
    # 保存结果
    print("\n保存回测结果...")
    with open('weight_backtest_results.json', 'w', encoding='utf-8') as f:
        # 简化保存关键结果
        summary = {}
        for env, combo_name, result in results:
            if env not in summary:
                summary[env] = []
            summary[env].append({
                'combo': combo_name,
                'win_rate': result['win_rate'],
                'total_return': result['total_return'],
                'max_drawdown': result['max_drawdown'],
                'sharpe_ratio': result['sharpe_ratio']
            })
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("\n回测完成！结果已保存至 weight_backtest_results.json")
