#!/usr/bin/env python3
"""
多维度数据采集系统 - 基于老涂的认知升级
数据采集 = 所有可能产生预期差的信息
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import re

class MultiDimensionDataCollector:
    """多维度数据采集系统"""
    
    def __init__(self):
        self.today = datetime.now()
        self.data_dir = "/Users/tuqibiao/.openclaw/workspace/data/multi_dimension"
        
        # 创建目录
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 监控关键词（可根据需要扩展）
        self.monitor_keywords = {
            "技术突破": [
                "突破", "创新", "研发成功", "专利授权", "技术领先",
                "首台套", "国产化", "自主可控", "填补空白", "国际先进"
            ],
            "政策发布": [
                "政策", "规划", "方案", "意见", "通知",
                "支持", "鼓励", "发展", "促进", "试点"
            ],
            "重大事件": [
                "签约", "合同", "订单", "合作", "并购",
                "重组", "投资", "扩产", "投产", "上市"
            ],
            "逻辑变化": [
                "商业模式", "产业链", "竞争格局", "用户习惯",
                "技术路线", "行业生态", "价值重估", "认知改变"
            ],
            "情绪转折": [
                "超预期", "大超预期", "拐点", "反转", "复苏",
                "改善", "好转", "乐观", "看好", "推荐"
            ]
        }
    
    def collect_event_data(self) -> List[Dict]:
        """采集事件维度数据（技术突破、政策发布等）"""
        print("📡 采集事件维度数据...")
        
        # 这里可以集成真实数据源：新闻API、社交媒体、公告等
        # 模拟数据示例
        events = [
            {
                "type": "技术突破",
                "title": "某公司宣布在量子计算芯片领域取得重大突破",
                "content": "实现100量子比特芯片的稳定运行，性能达到国际领先水平",
                "source": "科技新闻",
                "date": self.today.strftime("%Y-%m-%d"),
                "impact_score": 85,  # 影响力评分
                "expected_gap": "市场尚未充分认识其技术突破的价值",
                "related_industries": ["半导体", "人工智能", "量子计算"]
            },
            {
                "type": "政策发布",
                "title": "国家发布《人工智能产业发展行动计划（2026-2030）》",
                "content": "提出到2030年人工智能核心产业规模超过2万亿元",
                "source": "政府网站",
                "date": self.today.strftime("%Y-%m-%d"),
                "impact_score": 90,
                "expected_gap": "政策支持力度超市场预期",
                "related_industries": ["人工智能", "算力", "算法"]
            },
            {
                "type": "重大事件",
                "title": "某航运公司签订100亿美元长期运输合同",
                "content": "与全球主要矿商签订10年长期运输协议，保障运价稳定",
                "source": "公司公告",
                "date": self.today.strftime("%Y-%m-%d"),
                "impact_score": 75,
                "expected_gap": "长期合同锁定利润，降低周期波动风险",
                "related_industries": ["航运", "物流"]
            },
            {
                "type": "逻辑变化",
                "title": "新能源汽车充电桩商业模式创新",
                "content": "从单纯设备销售转向"设备+运营+服务"一体化模式",
                "source": "行业研究",
                "date": self.today.strftime("%Y-%m-%d"),
                "impact_score": 70,
                "expected_gap": "商业模式变化带来估值体系重构",
                "related_industries": ["新能源", "充电桩", "电力设备"]
            },
            {
                "type": "情绪转折",
                "title": "多家机构同时上调半导体设备行业评级",
                "content": "从"谨慎"上调至"推荐"，认为国产替代进入加速期",
                "source": "机构研报",
                "date": self.today.strftime("%Y-%m-%d"),
                "impact_score": 65,
                "expected_gap": "机构观点集体转向，市场情绪可能跟随",
                "related_industries": ["半导体", "设备"]
            }
        ]
        
        # 保存事件数据
        event_file = f"{self.data_dir}/events_{self.today.strftime('%Y%m%d')}.json"
        with open(event_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 采集到 {len(events)} 个重要事件")
        return events
    
    def collect_logic_data(self) -> List[Dict]:
        """采集逻辑维度数据（商业模式、产业链等变化）"""
        print("🧠 采集逻辑维度数据...")
        
        logic_changes = [
            {
                "industry": "教育",
                "change_type": "政策逻辑变化",
                "old_logic": "双减政策限制，行业萎缩",
                "new_logic": "职业教育政策支持，AI教育兴起",
                "evidence": [
                    "职业教育法修订实施",
                    "AI教育产品用户增长300%",
                    "职业教育市场规模年增20%"
                ],
                "expected_gap": "市场仍停留在旧逻辑，未认识新逻辑",
                "impact_level": "高"  # 高、中、低
            },
            {
                "industry": "电力",
                "change_type": "商业模式变化",
                "old_logic": "公用事业，稳定但无增长",
                "new_logic": "虚拟电厂、电力市场化带来新增长",
                "evidence": [
                    "虚拟电厂试点项目盈利超预期",
                    "电力市场化交易规模扩大",
                    "储能政策支持力度加大"
                ],
                "expected_gap": "新商业模式价值未被充分定价",
                "impact_level": "中"
            },
            {
                "industry": "农业",
                "change_type": "技术逻辑变化",
                "old_logic": "传统农业，靠天吃饭",
                "new_logic": "生物育种、智慧农业技术驱动",
                "evidence": [
                    "转基因玉米商业化种植面积扩大",
                    "智慧农业设备渗透率提升",
                    "农业科技公司融资活跃"
                ],
                "expected_gap": "技术突破带来的产业变革被低估",
                "impact_level": "中高"
            }
        ]
        
        logic_file = f"{self.data_dir}/logic_changes_{self.today.strftime('%Y%m%d')}.json"
        with open(logic_file, 'w', encoding='utf-8') as f:
            json.dump(logic_changes, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 采集到 {len(logic_changes)} 个逻辑变化")
        return logic_changes
    
    def collect_sentiment_data(self) -> Dict:
        """采集情绪维度数据"""
        print("😊 采集情绪维度数据...")
        
        # 模拟情绪数据
        sentiment_data = {
            "market_sentiment": {
                "overall": "谨慎乐观",  # 乐观、谨慎乐观、中性、谨慎、悲观
                "change_trend": "改善",  # 改善、恶化、持平
                "volatility": "中等",    # 高、中、低
                "risk_appetite": "提升"  # 提升、下降、持平
            },
            "industry_sentiment": {
                "半导体": {"score": 65, "trend": "上升", "reason": "国产替代逻辑强化"},
                "人工智能": {"score": 75, "trend": "上升", "reason": "技术突破频现"},
                "新能源": {"score": 60, "trend": "持平", "reason": "政策支持但竞争激烈"},
                "医药": {"score": 55, "trend": "改善", "reason": "估值修复进行中"},
                "航运": {"score": 70, "trend": "上升", "reason": "运价上涨超预期"}
            },
            "sentiment_indicators": {
                "fear_greed_index": 65,  # 恐惧贪婪指数（0-100）
                "put_call_ratio": 0.8,   # 看跌看涨比率
                "advance_decline_ratio": 1.2,  # 涨跌家数比
                "volume_concentration": 0.3    # 成交量集中度
            }
        }
        
        sentiment_file = f"{self.data_dir}/sentiment_{self.today.strftime('%Y%m%d')}.json"
        with open(sentiment_file, 'w', encoding='utf-8') as f:
            json.dump(sentiment_data, f, ensure_ascii=False, indent=2)
        
        print("   ✅ 情绪数据采集完成")
        return sentiment_data
    
    def collect_fund_flow_data(self) -> Dict:
        """采集资金维度数据"""
        print("💰 采集资金维度数据...")
        
        fund_flow_data = {
            "northbound_flow": {
                "total": 15.2,  # 亿元，净流入
                "by_industry": {
                    "电子": 3.2,
                    "医药": 2.8,
                    "电力设备": 2.5,
                    "计算机": 2.1,
                    "机械设备": 1.8
                },
                "trend": "持续流入",
                "concentration": "中等"
            },
            "margin_balance": {
                "total": 15800,  # 亿元
                "change": 120,   # 亿元，变化
                "change_rate": 0.76,  # 变化率
                "by_industry": {
                    "非银金融": 1800,
                    "电子": 1650,
                    "医药生物": 1420,
                    "计算机": 1350,
                    "电力设备": 1280
                }
            },
            "institutional_behavior": {
                "research_frequency": {
                    "半导体": 85,  # 调研次数
                    "医药": 72,
                    "新能源": 68,
                    "计算机": 65,
                    "机械设备": 58
                },
                "position_change": {
                    "加仓": ["半导体", "计算机", "通信"],
                    "减仓": ["房地产", "建材", "家电"],
                    "持平": ["银行", "非银金融", "食品饮料"]
                }
            },
            "unusual_flow": [
                {
                    "stock": "中远海控",
                    "flow_type": "大宗交易",
                    "amount": 2.5,  # 亿元
                    "price": "溢价5%",
                    "possible_reason": "机构建仓"
                },
                {
                    "stock": "北方华创",
                    "flow_type": "龙虎榜",
                    "amount": 1.8,
                    "price": "涨停",
                    "possible_reason": "游资炒作"
                }
            ]
        }
        
        fund_file = f"{self.data_dir}/fund_flow_{self.today.strftime('%Y%m%d')}.json"
        with open(fund_file, 'w', encoding='utf-8') as f:
            json.dump(fund_flow_data, f, ensure_ascii=False, indent=2)
        
        print("   ✅ 资金流向数据采集完成")
        return fund_flow_data
    
    def collect_traditional_data(self) -> Dict:
        """采集传统数据维度"""
        print("📊 采集传统数据维度...")
        
        traditional_data = {
            "financial_data": {
                "revenue_growth": {
                    "半导体": 25.3,
                    "新能源": 32.8,
                    "医药": 18.5,
                    "计算机": 22.1,
                    "机械设备": 15.6
                },
                "profit_growth": {
                    "半导体": 45.2,
                    "新能源": 38.7,
                    "医药": 22.3,
                    "计算机": 28.9,
                    "机械设备": 18.4
                }
            },
            "operational_data": {
                "order_growth": {
                    "半导体设备": 85.3,
                    "新能源设备": 62.8,
                    "医疗器械": 35.6,
                    "工业软件": 48.2,
                    "工程机械": 22.7
                },
                "capacity_utilization": {
                    "半导体": 85.2,
                    "新能源": 82.7,
                    "医药": 78.5,
                    "汽车": 76.3,
                    "化工": 72.8
                }
            },
            "valuation_data": {
                "pe_ratio": {
                    "半导体": 45.2,
                    "新能源": 32.8,
                    "医药": 28.5,
                    "计算机": 40.3,
                    "机械设备": 25.6
                },
                "pb_ratio": {
                    "半导体": 4.2,
                    "新能源": 3.8,
                    "医药": 3.2,
                    "计算机": 4.5,
                    "机械设备": 2.8
                }
            }
        }
        
        traditional_file = f"{self.data_dir}/traditional_{self.today.strftime('%Y%m%d')}.json"
        with open(traditional_file, 'w', encoding='utf-8') as f:
            json.dump(traditional_data, f, ensure_ascii=False, indent=2)
        
        print("   ✅ 传统数据采集完成")
        return traditional_data
    
    def integrate_all_data(self) -> Dict:
        """整合所有维度数据"""
        print("\n🔗 整合所有维度数据...")
        
        all_data = {
            "date": self.today.strftime("%Y-%m-%d"),
            "event_data": self.collect_event_data(),
            "logic_data": self.collect_logic_data(),
            "sentiment_data": self.collect_sentiment_data(),
            "fund_flow_data": self.collect_fund_flow_data(),
            "traditional_data": self.collect_traditional_data(),
            "integration_summary": self.generate_integration_summary()
        }
        
        # 保存整合数据
        integrated_file = f"{self.data_dir}/integrated_{self.today.strftime('%Y%m%d')}.json"
        with open(integrated_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ 数据整合完成，保存至: {integrated_file}")
        return all_data
    
    def generate_integration_summary(self) -> Dict:
        """生成数据整合摘要"""
        summary = {
            "total_events": 5,
            "logic_changes": 3,
            "sentiment_trend": "改善",
            "fund_flow_trend": "流入",
            "data_quality": "良好",
            "key_insights": [
                "事件驱动：技术突破和政策发布可能带来新机会",
                "逻辑变化：教育、电力等行业逻辑正在重构",
                "情绪改善：市场风险偏好有所提升",
                "资金流入：北向资金持续流入科技板块"
            ]
        }
        
        return summary
    
    def analyze_expected_gap(self, integrated_data: Dict) -> List[Dict]:
        """基于多维度数据分析预期差"""
        print("\n🎯 基于多维度数据分析预期差...")
        
        expected_gaps = []
        
        # 分析事件驱动的预期差
        for event in integrated_data["event_data"]:
            gap = {
                "source": "事件驱动",
                "type": event["type"],
                "content": event["title"],
                "expected_gap": event["expected_gap"],
                "impact_score": event["impact_score"],
                "related_industries": event["related_industries"],
                "data_support": event["content"]
            }
            expected_gaps.append(gap)
        
        # 分析逻辑变化的预期差
        for logic in integrated_data["logic_data"]:
            gap = {
                "source": "逻辑变化",
                "type": logic["change_type"],
                "content": f"{logic['industry']}: {logic['old_logic']} → {logic['new_logic']}",
                "expected_gap": logic["expected_gap"],
                "impact_score": 80 if logic["impact_level"] == "高" else 60,
                "related_industries": [logic["industry"]],
                "data_support": ", ".join(logic["evidence"][:2])
            }
            expected_gaps.append(gap)
        
        # 分析情绪转折的预期差
        sentiment = integrated_data["sentiment_data"]
        for industry, data in sentiment["industry_sentiment"].items():
            if data["trend"] == "上升" and data["score"] > 60:
                gap = {
                    "source": "情绪转折",
                    "type": "情绪改善",
                    "content": f"{industry}情绪评分{data['score']}，趋势{data['trend']}",
                    "expected_gap": f"市场情绪改善可能领先基本面改善",
                    "impact_score": data["score"],
                    "related_industries": [industry],
                    "data_support": data["reason"]
                }
                expected_gaps.append(gap)
        
        # 分析资金异动的预期差
        fund_flow = integrated_data["fund_flow_data"]
        for unusual in fund_flow.get("unusual_flow", []):
            gap = {
                "source": "资金异动",
                "type": unusual["flow_type"],
                "content": f"{unusual['stock']}发生{unusual['flow_type']}，金额{unusual['amount']}亿",
                "expected_gap": f"大资金行为可能预示基本面变化",
                "impact_score": 70,
                "related_industries": ["