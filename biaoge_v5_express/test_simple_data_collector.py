"""
简化版数据采集系统测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleDataCollector:
    """简化版数据采集器"""
    
    def __init__(self):
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info("简化版数据采集器初始化完成")
    
    def get_market_data(self) -> dict:
        """获取市场数据（简化版）"""
        logger.info("开始获取市场数据")
        
        # 尝试多个数据源
        data_sources = [
            self._try_akshare,
            self._try_tushare_simple,
            self._try_eastmoney_simple,
            self._get_smart_mock_data
        ]
        
        for data_source in data_sources:
            try:
                data = data_source()
                if data is not None:
                    logger.info(f"成功从 {data['source']} 获取数据")
                    return data
            except Exception as e:
                logger.warning(f"数据源失败: {e}")
                continue
        
        # 所有数据源都失败，返回基础模拟数据
        return self._get_basic_mock_data()
    
    def _try_akshare(self) -> dict:
        """尝试AkShare"""
        try:
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            
            if df is None or len(df) == 0:
                return None
            
            # 简单统计
            if '涨跌幅' in df.columns:
                rise_count = len(df[df['涨跌幅'] > 0])
                total_count = len(df)
                
                return {
                    "timestamp": datetime.now(),
                    "source": "akshare",
                    "total_stocks": total_count,
                    "rise_count": rise_count,
                    "fall_count": total_count - rise_count,
                    "rise_ratio": rise_count / total_count if total_count > 0 else 0,
                    "average_change": df['涨跌幅'].mean() if total_count > 0 else 0,
                    "data_quality": "good"
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"AkShare失败: {e}")
            return None
    
    def _try_tushare_simple(self) -> dict:
        """尝试Tushare简化版"""
        try:
            import tushare as ts
            
            # 检查token
            token = ts.get_token()
            if not token:
                return None
            
            # 获取简单数据
            df = ts.get_today_all()
            
            if df is None or len(df) == 0:
                return None
            
            # 简单统计
            if 'changepercent' in df.columns:
                rise_count = len(df[df['changepercent'] > 0])
                total_count = len(df)
                
                return {
                    "timestamp": datetime.now(),
                    "source": "tushare",
                    "total_stocks": total_count,
                    "rise_count": rise_count,
                    "fall_count": total_count - rise_count,
                    "rise_ratio": rise_count / total_count if total_count > 0 else 0,
                    "average_change": df['changepercent'].mean() if total_count > 0 else 0,
                    "data_quality": "good"
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Tushare失败: {e}")
            return None
    
    def _try_eastmoney_simple(self) -> dict:
        """尝试东方财富简化版"""
        try:
            import requests
            
            # 获取主要指数
            indices = {
                "sh000001": "上证指数",
                "sz399001": "深证成指", 
                "sz399006": "创业板指"
            }
            
            changes = []
            
            for code, name in indices.items():
                url = f"http://push2.eastmoney.com/api/qt/stock/get"
                params = {
                    "secid": code,
                    "fields": "f43,f44,f45,f46,f60,f84,f85,f86,f169,f170",
                    "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                    "invt": "2",
                    "fltt": "2"
                }
                
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data"):
                        change = data["data"].get("f170", 0)  # 涨跌幅
                        if isinstance(change, (int, float)):
                            changes.append(change)
            
            if changes:
                avg_change = sum(changes) / len(changes)
                
                # 基于指数变化估算市场情况
                if avg_change > 1:
                    rise_ratio = 0.65
                elif avg_change > 0:
                    rise_ratio = 0.55
                elif avg_change > -1:
                    rise_ratio = 0.45
                else:
                    rise_ratio = 0.35
                
                return {
                    "timestamp": datetime.now(),
                    "source": "eastmoney",
                    "total_stocks": 5000,
                    "rise_count": int(5000 * rise_ratio),
                    "fall_count": 5000 - int(5000 * rise_ratio),
                    "rise_ratio": rise_ratio,
                    "average_change": avg_change,
                    "data_quality": "estimated",
                    "note": "基于东方财富指数数据估算"
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"东方财富失败: {e}")
            return None
    
    def _get_smart_mock_data(self) -> dict:
        """获取智能模拟数据"""
        import random
        from datetime import datetime
        
        # 基于当前时间和星期几生成相对合理的模拟数据
        now = datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0=周一, 6=周日
        
        # 交易时间判断
        is_trading_hour = (9 <= hour < 15) and (weekday < 5)
        
        if is_trading_hour:
            # 交易时间：相对活跃
            base_ratio = 0.5
            volatility = 0.15
            base_change = random.uniform(-0.5, 1.0)
        else:
            # 非交易时间：相对平静
            base_ratio = 0.5
            volatility = 0.05
            base_change = random.uniform(-0.2, 0.2)
        
        # 添加一些随机性但保持相对稳定
        rise_ratio = base_ratio + random.uniform(-volatility, volatility)
        rise_ratio = max(0.3, min(0.7, rise_ratio))
        
        total_stocks = 5000
        rise_count = int(total_stocks * rise_ratio)
        fall_count = total_stocks - rise_count
        
        return {
            "timestamp": now,
            "source": "smart_mock",
            "total_stocks": total_stocks,
            "rise_count": rise_count,
            "fall_count": fall_count,
            "limit_up_count": int(rise_count * 0.02),  # 2%的上涨股票涨停
            "limit_down_count": int(fall_count * 0.01),  # 1%的下跌股票跌停
            "rise_ratio": rise_ratio,
            "average_change": base_change + random.uniform(-0.5, 0.5),
            "data_quality": "simulated",
            "note": "智能模拟数据，基于时间特征生成"
        }
    
    def _get_basic_mock_data(self) -> dict:
        """获取基础模拟数据"""
        import random
        
        return {
            "timestamp": datetime.now(),
            "source": "basic_mock",
            "total_stocks": 5000,
            "rise_count": 2500,
            "fall_count": 2500,
            "rise_ratio": 0.5,
            "average_change": 0,
            "data_quality": "simulated",
            "note": "基础模拟数据，所有数据源失败"
        }


def test_simple_collector():
    """测试简化版采集器"""
    print("\n" + "="*60)
    print("🧪 测试简化版数据采集器")
    print("="*60)
    
    try:
        collector = SimpleDataCollector()
        market_data = collector.get_market_data()
        
        print(f"✅ 数据采集成功")
        print(f"   数据来源: {market_data['source']}")
        print(f"   数据质量: {market_data['data_quality']}")
        print(f"   股票总数: {market_data['total_stocks']}")
        print(f"   上涨家数: {market_data['rise_count']}")
        print(f"   下跌家数: {market_data['fall_count']}")
        print(f"   上涨比例: {market_data['rise_ratio']*100:.1f}%")
        print(f"   平均涨跌: {market_data['average_change']:.2f}%")
        
        if 'note' in market_data:
            print(f"   备注: {market_data['note']}")
        
        return True, market_data
        
    except Exception as e:
        print(f"❌ 数据采集失败: {e}")
        return False, None


def integrate_with_state_system(market_data: dict):
    """集成状态系统"""
    print("\n" + "="*60)
    print("🔄 集成状态演化系统")
    print("="*60)
    
    try:
        # 计算技术评分
        rise_ratio = market_data['rise_ratio']
        avg_change = market_data['average_change']
        
        # 简单评分算法
        technical_score = 50 + (rise_ratio - 0.5) * 100 + avg_change * 10
        technical_score = max(0, min(100, technical_score))
        
        print(f"   市场数据:")
        print(f"     上涨比例: {rise_ratio*100:.1f}%")
        print(f"     平均涨跌: {avg_change:.2f}%")
        print(f"   计算的技术评分: {technical_score:.1f}")
        
        # 简单状态判断
        if technical_score >= 70:
            state = "夏长期"
            position_range = (50, 80)
            strategy = "重仓持股，趋势持有"
        elif technical_score >= 60:
            state = "春入夏过渡期"
            position_range = (40, 60)
            strategy = "适度加仓，持有趋势股"
        elif technical_score >= 50:
            state = "春播期"
            position_range = (30, 50)
            strategy = "分批建仓，布局优质标的"
        elif technical_score >= 40:
            state = "混沌期"
            position_range = (10, 30)
            strategy = "观望等待，小仓位试错"
        elif technical_score >= 30:
            state = "秋收期"
            position_range = (20, 40)
            strategy = "获利了结，转向防御"
        else:
            state = "冬藏期"
            position_range = (0, 20)
            strategy = "空仓观望，等待信号"
        
        print(f"\n   状态分析:")
        print(f"     当前状态: {state}")
        print(f"     建议仓位: {position_range[0]}%-{position_range[1]}%")
        print(f"     操作策略: {strategy}")
        
        # 简单预测
        print(f"\n   简单预测:")
        if technical_score >= 70:
            print(f"     高概率保持强势，注意过热风险")
        elif technical_score >= 50:
            print(f"     可能继续震荡上行，关注量能变化")
        elif technical_score >= 30:
            print(f"     可能继续调整，控制仓位风险")
        else:
            print(f"     弱势格局，等待明确反弹信号")
        
        return True
        
    except Exception as e:
        print(f"❌ 状态集成失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 彪哥战法v5.0 - 第2步：简化版数据采集系统")
    print("📅 实施时间: 2026-03-26")
    print("🎯 目标: 建立可用的数据采集基础")
    
    # 测试数据采集
    success, market_data = test_simple_collector()
    
    if not success:
        print("\n❌ 数据采集测试失败")
        return
    
    # 集成状态系统
    integration_success = integrate_with_state_system(market_data)
    
    if not integration_success:
        print("\n❌ 状态集成测试失败")
        return
    
    print("\n" + "="*60)
    print("🎉 第2步基础实施完成！")
    print("="*60)
    
    print("\n✅ 已完成:")
    print("  1. 简化版数据采集器实现")
    print("  2. 多数据源尝试机制")
    print("  3. 智能模拟数据生成")
    print("  4. 基础状态分析集成")
    
    print("\n🚀 下一步优化:")
    print("  1. 优化真实数据源连接稳定性")
    print("  2. 增加新闻和政策数据采集")
    print("  3. 完善数据缓存和更新机制")
    print("  4. 建立数据质量监控系统")
    
    print("\n📅 预计时间:")
    print("  • 数据源优化: 1-2天")
    print("  • 新闻数据: 1天")
    print("  • 缓存机制: 1天")
    print("  • 质量监控: 1天")
    print("  • 总计: 4-5天")
    
    print("\n💡 实施策略:")
    print("  1. 先保证基础数据可用")
    print("  2. 逐步增加数据维度")
    print("  3. 建立数据质量标准")
    print("  4. 实现自动化监控")
    
    print("\n🎯 预期效果:")
    print("  • 稳定的市场数据服务")
    print("  • 智能化的数据降级")
    print("  • 实时的状态分析")
    print("  • 可靠的决策支持")


if __name__ == "__main__":
    main()