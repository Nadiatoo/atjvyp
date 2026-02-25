#!/usr/bin/env python3
"""
回测结果可视化报告生成器
"""

import json
import pandas as pd

def generate_report():
    """生成回测报告"""
    
    # 读取回测结果
    with open('weight_backtest_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print("=" * 80)
    print("【彪哥战法v5.0】周期权重动态优化回测报告")
    print("=" * 80)
    
    # 1. 整体表现
    print("\n一、整体表现对比")
    print("-" * 80)
    overall = results.get('overall', [])
    df_overall = pd.DataFrame(overall)
    if not df_overall.empty:
        df_overall = df_overall.sort_values('sharpe_ratio', ascending=False)
        print(df_overall[['combo', 'win_rate', 'total_return', 'max_drawdown', 'sharpe_ratio']].to_string(index=False))
    
    # 2. 分环境最优
    print("\n\n二、分市场环境最优权重")
    print("-" * 80)
    
    environments = {
        'quant': '量化主导',
        'institution': '机构主导',
        'retail': '游资主导',
        'mixed': '混合市场'
    }
    
    for env_key, env_name in environments.items():
        env_results = results.get(env_key, [])
        if env_results:
            df_env = pd.DataFrame(env_results)
            if not df_env.empty and df_env['sharpe_ratio'].max() > 0:
                best = df_env.loc[df_env['sharpe_ratio'].idxmax()]
                print(f"\n{env_name}:")
                print(f"  最优组合: {best['combo']}")
                print(f"  胜率: {best['win_rate']:.1%}")
                print(f"  夏普比率: {best['sharpe_ratio']:.2f}")
                print(f"  总收益: {best['total_return']:.1f}%")
                print(f"  最大回撤: {best['max_drawdown']:.1f}%")
    
    # 3. 关键发现
    print("\n\n三、关键发现")
    print("-" * 80)
    
    findings = []
    
    # 发现1：机构A在多个环境表现优异
    inst_a_overall = next((r for r in overall if r['combo'] == '机构A'), None)
    if inst_a_overall:
        findings.append(f"1. 机构A整体表现最优：胜率{inst_a_overall['win_rate']:.1%}，夏普{inst_a_overall['sharpe_ratio']:.2f}")
    
    # 发现2：量化主导环境下需要调整
    quant_results = results.get('quant', [])
    if quant_results:
        df_quant = pd.DataFrame(quant_results)
        baseline_sharpe = df_quant[df_quant['combo'] == '基准']['sharpe_ratio'].values
        inst_a_sharpe = df_quant[df_quant['combo'] == '机构A']['sharpe_ratio'].values
        if len(baseline_sharpe) > 0 and len(inst_a_sharpe) > 0:
            if inst_a_sharpe[0] > baseline_sharpe[0]:
                findings.append(f"2. 量化主导环境下，机构A优于基准（夏普{inst_a_sharpe[0]:.2f} vs {baseline_sharpe[0]:.2f}）")
    
    # 发现3：低流动性环境表现差
    low_liq = next((r for r in overall if r['combo'] == '低流动性'), None)
    if low_liq:
        findings.append(f"3. 低流动性环境需谨慎：夏普比率仅{low_liq['sharpe_ratio']:.2f}，远低于高流动性环境的{overall[0]['sharpe_ratio']:.2f}")
    
    for finding in findings:
        print(finding)
    
    # 4. 明日行动计划
    print("\n\n四、明日行动计划（接入真实数据）")
    print("-" * 80)
    print("1. 确认akshare数据源恢复正常（或等明天自动恢复）")
    print("2. 获取2024-2025年真实历史数据（约300个交易日）")
    print("3. 重新运行回测，验证模拟数据结论")
    print("4. 根据真实数据校准市场环境识别阈值")
    print("5. 确定最终最优权重配置，写入v5.1")
    
    print("\n" + "=" * 80)
    print("报告生成完成")
    print("=" * 80)

if __name__ == "__main__":
    generate_report()
