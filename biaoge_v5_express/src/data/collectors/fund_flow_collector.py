"""
资金流向数据采集器
"""

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import time
from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class FundFlowCollector(BaseCollector):
    """资金流向数据采集器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("fund_flow_collector", config)
        
        # 配置监控的股票列表
        self.monitor_stocks = config.get("monitor_stocks", [
            "000001",  # 平安银行
            "000002",  # 万科A
            "000858",  # 五粮液
            "600519",  # 贵州茅台
            "300750",  # 宁德时代
            "002594",  # 比亚迪
        ])
        
        # 量化特征配置
        self.quant_config = config.get("quant_config", {
            "seat_threshold": 0.25,  # 量化席位占比阈值
            "volume_ratio_threshold": 2.0,  # 成交量比阈值
            "price_impact_threshold": 0.02  # 价格冲击阈值
        })
    
    def collect(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        采集资金流向数据
        
        Args:
            date: 采集日期，None表示最新
            
        Returns:
            资金流向数据字典
        """
        if not self.enabled:
            logger.warning("资金流向采集器已禁用")
            return {}
        
        logger.info(f"开始采集资金流向数据，日期: {date}")
        
        results = {
            "timestamp": datetime.now(),
            "date": date if date else self.get_trading_date(),
            "northbound": {},
            "institutional": {},
            "retail": {},
            "quant_features": {},
            "sector_flow": {}
        }
        
        try:
            # 1. 采集北向资金数据
            northbound_data = self._collect_northbound(date)
            results["northbound"] = northbound_data
            
            # 2. 采集机构资金数据
            institutional_data = self._collect_institutional(date)
            results["institutional"] = institutional_data
            
            # 3. 采集散户资金数据（通过计算）
            retail_data = self._calculate_retail_flow(date)
            results["retail"] = retail_data
            
            # 4. 分析量化特征
            quant_features = self._analyze_quant_features(date)
            results["quant_features"] = quant_features
            
            # 5. 分析板块资金流向
            sector_flow = self._analyze_sector_flow(date)
            results["sector_flow"] = sector_flow
            
            # 6. 计算资金面综合指标
            comprehensive_indicators = self._calculate_comprehensive_indicators(
                northbound_data, institutional_data, retail_data, quant_features
            )
            results["comprehensive_indicators"] = comprehensive_indicators
            
            self.log_collection(True, data_count=len(self.monitor_stocks))
            return results
            
        except Exception as e:
            error_msg = f"资金流向数据采集失败: {e}"
            self.log_collection(False, error_msg=error_msg)
            return {}
    
    def _collect_northbound(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """采集北向资金数据"""
        northbound_data = {}
        
        try:
            if date:
                # 获取历史北向资金数据
                date_str = self.format_date(date, "%Y%m%d")
                
                # 沪股通
                sh_df = ak.stock_hsgt_north_net_flow_in_em(symbol="沪股通")
                # 深股通
                sz_df = ak.stock_hsgt_north_net_flow_in_em(symbol="深股通")
                
                if not sh_df.empty and not sz_df.empty:
                    # 查找指定日期的数据
                    sh_data = sh_df[sh_df["日期"] == date_str]
                    sz_data = sz_df[sz_df["日期"] == date_str]
                    
                    sh_net = sh_data["当日成交净买额"].iloc[0] if not sh_data.empty else 0
                    sz_net = sz_data["当日成交净买额"].iloc[0] if not sz_data.empty else 0
                    
                    northbound_data = {
                        "shanghai_net": float(sh_net),
                        "shenzhen_net": float(sz_net),
                        "total_net": float(sh_net + sz_net),
                        "date": date_str
                    }
            else:
                # 获取实时北向资金数据
                df = ak.stock_hsgt_hold_stock_em(market="北向")
                
                if not df.empty:
                    # 计算总净流入
                    total_net = df["今日持股总数"].sum() - df["上日持股总数"].sum()
                    
                    # 按行业分类
                    industry_flow = df.groupby("所属行业")["今日持股总数"].sum().to_dict()
                    
                    # 前十大持仓
                    top_10 = df.nlargest(10, "今日持股总数")[["股票名称", "股票代码", "今日持股总数", "占流通股比例"]].to_dict("records")
                    
                    northbound_data = {
                        "total_net": float(total_net),
                        "industry_flow": industry_flow,
                        "top_10_holdings": top_10,
                        "timestamp": datetime.now()
                    }
            
            logger.info(f"采集到北向资金数据: 净流入 {northbound_data.get('total_net', 0):.2f} 亿元")
            return northbound_data
            
        except Exception as e:
            logger.error(f"采集北向资金数据失败: {e}")
            return {"total_net": 0, "shanghai_net": 0, "shenzhen_net": 0}
    
    def _collect_institutional(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """采集机构资金数据"""
        institutional_data = {}
        
        try:
            if date:
                # 获取龙虎榜数据作为机构资金参考
                date_str = self.format_date(date, "%Y%m%d")
                dragon_df = ak.stock_lhb_detail_em(date=date_str)
                
                if not dragon_df.empty:
                    # 分析机构席位
                    institutional_seats = dragon_df[dragon_df["营业部名称"].str.contains("机构专用|机构席位")]
                    
                    buy_amount = institutional_seats["买入额"].sum()
                    sell_amount = institutional_seats["卖出额"].sum()
                    net_amount = buy_amount - sell_amount
                    
                    institutional_data = {
                        "buy_amount": float(buy_amount),
                        "sell_amount": float(sell_amount),
                        "net_amount": float(net_amount),
                        "seat_count": len(institutional_seats),
                        "stocks": institutional_seats["股票代码"].tolist()[:10]
                    }
            else:
                # 获取实时龙虎榜数据
                dragon_df = ak.stock_lhb_detail_em(date="")
                
                if not dragon_df.empty:
                    # 分析机构席位
                    institutional_seats = dragon_df[dragon_df["营业部名称"].str.contains("机构专用|机构席位")]
                    
                    buy_amount = institutional_seats["买入额"].sum()
                    sell_amount = institutional_seats["卖出额"].sum()
                    net_amount = buy_amount - sell_amount
                    
                    # 分析游资动向
                    hot_money_seats = dragon_df[~dragon_df["营业部名称"].str.contains("机构专用|机构席位")]
                    hot_money_buy = hot_money_seats["买入额"].sum()
                    hot_money_sell = hot_money_seats["卖出额"].sum()
                    hot_money_net = hot_money_buy - hot_money_sell
                    
                    institutional_data = {
                        "institutional_buy": float(buy_amount),
                        "institutional_sell": float(sell_amount),
                        "institutional_net": float(net_amount),
                        "hot_money_buy": float(hot_money_buy),
                        "hot_money_sell": float(hot_money_sell),
                        "hot_money_net": float(hot_money_net),
                        "total_net": float(net_amount + hot_money_net),
                        "timestamp": datetime.now()
                    }
            
            logger.info(f"采集到机构资金数据: 机构净流入 {institutional_data.get('institutional_net', 0):.2f} 万元")
            return institutional_data
            
        except Exception as e:
            logger.error(f"采集机构资金数据失败: {e}")
            return {
                "institutional_buy": 0,
                "institutional_sell": 0,
                "institutional_net": 0,
                "hot_money_net": 0,
                "total_net": 0
            }
    
    def _calculate_retail_flow(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """计算散户资金流向（通过融资融券数据）"""
        retail_data = {}
        
        try:
            if date:
                # 获取历史融资融券数据
                date_str = self.format_date(date, "%Y%m%d")
                margin_df = ak.stock_margin_sse(date=date_str)
                
                if not margin_df.empty:
                    # 融资余额变化
                    financing_balance = margin_df["融资余额"].iloc[0] if "融资余额" in margin_df.columns else 0
                    financing_buy = margin_df["融资买入额"].iloc[0] if "融资买入额" in margin_df.columns else 0
                    
                    # 融券余额变化
                    securities_balance = margin_df["融券余额"].iloc[0] if "融券余额" in margin_df.columns else 0
                    securities_sell = margin_df["融券卖出量"].iloc[0] if "融券卖出量" in margin_df.columns else 0
                    
                    retail_data = {
                        "financing_balance": float(financing_balance),
                        "financing_buy": float(financing_buy),
                        "securities_balance": float(securities_balance),
                        "securities_sell": float(securities_sell),
                        "net_financing": float(financing_buy - securities_sell),
                        "date": date_str
                    }
            else:
                # 获取最新融资融券数据
                margin_df = ak.stock_margin_sse(date="")
                
                if not margin_df.empty:
                    latest = margin_df.iloc[-1]
                    
                    financing_balance = latest.get("融资余额", 0)
                    financing_buy = latest.get("融资买入额", 0)
                    securities_balance = latest.get("融券余额", 0)
                    securities_sell = latest.get("融券卖出量", 0)
                    
                    # 计算变化率
                    if len(margin_df) > 1:
                        prev = margin_df.iloc[-2]
                        financing_change = (financing_balance - prev.get("融资余额", 0)) / prev.get("融资余额", 1) * 100
                        securities_change = (securities_balance - prev.get("融券余额", 0)) / prev.get("融券余额", 1) * 100
                    else:
                        financing_change = 0
                        securities_change = 0
                    
                    retail_data = {
                        "financing_balance": float(financing_balance),
                        "financing_buy": float(financing_buy),
                        "securities_balance": float(securities_balance),
                        "securities_sell": float(securities_sell),
                        "net_financing": float(financing_buy - securities_sell),
                        "financing_change_pct": float(financing_change),
                        "securities_change_pct": float(securities_change),
                        "timestamp": datetime.now()
                    }
            
            logger.info(f"计算散户资金数据: 融资余额 {retail_data.get('financing_balance', 0):.2f} 亿元")
            return retail_data
            
        except Exception as e:
            logger.error(f"计算散户资金数据失败: {e}")
            return {
                "financing_balance": 0,
                "financing_buy": 0,
                "securities_balance": 0,
                "securities_sell": 0,
                "net_financing": 0
            }
    
    def _analyze_quant_features(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """分析量化特征"""
        quant_features = {}
        
        try:
            # 这里简化处理，实际需要更复杂的量化特征识别
            # 1. 程序化交易特征（通过订单流分析）
            programmatic_score = self._calculate_programmatic_score(date)
            
            # 2. 策略拥挤度（通过相似股票表现）
            crowding_degree = self._calculate_crowding_degree(date)
            
            # 3. 量化席位占比（通过龙虎榜分析）
            quant_seat_ratio = self._calculate_quant_seat_ratio(date)
            
            quant_features = {
                "programmatic_score": programmatic_score,  # 0-100，越高表示程序化特征越明显
                "crowding_degree": crowding_degree,  # 0-100，越高表示策略越拥挤
                "quant_seat_ratio": quant_seat_ratio,  # 0-1，量化席位占比
                "quant_dominant": quant_seat_ratio > self.quant_config["seat_threshold"],
                "timestamp": datetime.now()
            }
            
            logger.info(f"分析量化特征: 程序化评分 {programmatic_score:.1f}, 拥挤度 {crowding_degree:.1f}")
            return quant_features
            
        except Exception as e:
            logger.error(f"分析量化特征失败: {e}")
            return {
                "programmatic_score": 0,
                "crowding_degree": 0,
                "quant_seat_ratio": 0,
                "quant_dominant": False
            }
    
    def _calculate_programmatic_score(self, date: Optional[datetime] = None) -> float:
        """计算程序化交易特征评分"""
        # 简化版：基于订单流特征
        # 实际需要分析：订单大小分布、时间间隔、价格冲击等
        try:
            # 获取实时行情数据
            if not date:
                df = ak.stock_zh_a_spot_em()
                if not df.empty:
                    # 分析成交量分布
                    volume_series = df["成交量"]
                    volume_std = volume_series.std()
                    volume_mean = volume_series.mean()
                    
                    # 标准差/均值比越高，程序化特征可能越明显
                    if volume_mean > 0:
                        cv = volume_std / volume_mean
                        # 归一化到0-100
                        score = min(cv * 50, 100)
                        return float(score)
            
            return 50.0  # 默认中等评分
            
        except Exception as e:
            logger.warning(f"计算程序化评分失败: {e}")
            return 50.0
    
    def _calculate_crowding_degree(self, date: Optional[datetime] = None) -> float:
        """计算策略拥挤度"""
        # 简化版：基于股票相关性
        try:
            # 获取重点股票数据
            correlations = []
            
            for symbol in self.monitor_stocks[:5]:  # 只分析前5只
                try:
                    # 获取历史数据
                    df = ak.stock_zh_a_hist(
                        symbol=symbol,
                        period="daily",
                        start_date=self.format_date(datetime.now() - timedelta(days=20)),
                        end_date=self.format_date(datetime.now()),
                        adjust="qfq"
                    )
                    
                    if len(df) > 5:
                        returns = df["涨跌幅"].pct_change().dropna()
                        # 这里简化处理，实际需要计算多股票相关性
                        correlations.append(returns.std())
                    
                    time.sleep(0.2)
                    
                except Exception as e:
                    logger.warning(f"计算股票 {symbol} 波动率失败: {e}")
                    continue
            
            if correlations:
                avg_volatility = np.mean(correlations)
                # 波动率越高，拥挤度可能越高
                crowding = min(avg_volatility * 1000, 100)
                return float(crowding)
            
            return 50.0
            
        except Exception as e:
            logger.warning(f"计算拥挤度失败: {e}")
            return 50.0
    
    def _calculate_quant_seat_ratio(self, date: Optional[datetime] = None) -> float:
        """计算量化席位占比"""
        try:
            if not date:
                # 获取龙虎榜数据
                dragon_df = ak.stock_lhb_detail_em(date="")
                
                if not dragon_df.empty:
                    # 识别量化席位（简化：包含"量化"、"算法"等关键词）
                    quant_keywords = ["量化", "算法", "程序", "系统", "自动"]
                    
                    def is_quant_seat(name):
                        if not isinstance(name, str):
                            return False
                        return any(keyword in name for keyword in quant_keywords)
                    
                    quant_seats = dragon_df[dragon_df["营业部名称"].apply(is_quant_seat)]
                    total_seats = len(dragon_df)
                    
                    if total_seats > 0:
                        ratio = len(quant_seats) / total_seats
                        return float(ratio)
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"计算量化席位占比失败: {e}")
            return 0.0
    
    def _analyze_sector_flow(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """分析板块资金流向"""
        sector_flow = {}
        
        try:
            # 获取板块资金流向