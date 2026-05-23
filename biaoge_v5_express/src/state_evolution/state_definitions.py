"""
动态状态演化系统 - 状态定义
"""

from enum import Enum
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


class MarketState(str, Enum):
    """市场状态枚举"""
    WINTER = "winter"                      # 冬藏期
    WINTER_SPRING_TRANSITION = "winter_spring_transition"  # 冬末春初过渡期
    SPRING = "spring"                      # 春播期
    SPRING_SUMMER_TRANSITION = "spring_summer_transition"  # 春入夏过渡期
    SUMMER = "summer"                      # 夏长期
    SUMMER_AUTUMN_TRANSITION = "summer_autumn_transition"  # 夏末秋初过渡期
    AUTUMN = "autumn"                      # 秋收期
    AUTUMN_WINTER_TRANSITION = "autumn_winter_transition"  # 秋入冬过渡期
    CHAOS = "chaos"                        # 混沌期


@dataclass
class StateDefinition:
    """状态定义"""
    state: MarketState
    chinese_name: str
    description: str
    technical_characteristics: List[str]
    fund_characteristics: List[str]
    sentiment_characteristics: List[str]
    macro_characteristics: List[str]
    position_range: Tuple[float, float]  # 仓位范围 (最小, 最大)
    operation_strategy: str
    risk_level: str
    typical_duration_days: Tuple[int, int]  # 典型持续时间范围


# 状态定义库
STATE_DEFINITIONS: Dict[MarketState, StateDefinition] = {
    MarketState.WINTER: StateDefinition(
        state=MarketState.WINTER,
        chinese_name="冬藏期",
        description="市场处于明确下跌趋势，恐慌情绪蔓延，建议空仓观望等待春播信号",
        technical_characteristics=[
            "下跌股票比例>70%",
            "技术评分<30",
            "连续下跌趋势",
            "关键支撑位被突破"
        ],
        fund_characteristics=[
            "资金持续流出",
            "主力资金撤离",
            "散户恐慌抛售",
            "外资流出明显"
        ],
        sentiment_characteristics=[
            "恐慌情绪主导",
            "负面新闻频发",
            "投资者信心低迷",
            "市场预期悲观"
        ],
        macro_characteristics=[
            "宏观经济下行",
            "政策收紧或观望",
            "地缘政治紧张",
            "流动性紧张"
        ],
        position_range=(0, 20),  # 0-20%
        operation_strategy="空仓观望，等待明确春播信号，不轻易抄底",
        risk_level="高",
        typical_duration_days=(20, 60)
    ),
    
    MarketState.WINTER_SPRING_TRANSITION: StateDefinition(
        state=MarketState.WINTER_SPRING_TRANSITION,
        chinese_name="冬末春初过渡期",
        description="下跌趋势趋缓，出现试探性反弹，可轻仓试错布局优质标的",
        technical_characteristics=[
            "下跌股票比例50-70%",
            "技术评分30-45",
            "下跌速度放缓",
            "出现技术性反弹"
        ],
        fund_characteristics=[
            "资金流出减缓",
            "试探性资金流入",
            "主力开始建仓",
            "外资流出减少"
        ],
        sentiment_characteristics=[
            "恐慌情绪缓解",
            "谨慎乐观出现",
            "负面新闻减少",
            "预期开始分化"
        ],
        macro_characteristics=[
            "宏观政策微调",
            "经济数据企稳",
            "地缘紧张缓解",
            "流动性改善"
        ],
        position_range=(10, 30),  # 10-30%
        operation_strategy="轻仓试错，分批建仓，关注率先反弹的优质标的",
        risk_level="中高",
        typical_duration_days=(10, 30)
    ),
    
    MarketState.SPRING: StateDefinition(
        state=MarketState.SPRING,
        chinese_name="春播期",
        description="反弹确认，市场情绪回暖，适合分批建仓布局政策受益和业绩预增板块",
        technical_characteristics=[
            "上涨股票比例>55%",
            "技术评分45-60",
            "反弹趋势确认",
            "关键技术位突破"
        ],
        fund_characteristics=[
            "资金开始流入",
            "主力持续建仓",
            "散户情绪回暖",
            "外资开始回流"
        ],
        sentiment_characteristics=[
            "乐观情绪上升",
            "正面新闻增多",
            "投资者信心恢复",
            "市场预期改善"
        ],
        macro_characteristics=[
            "宏观政策支持",
            "经济数据好转",
            "地缘环境稳定",
            "流动性充裕"
        ],
        position_range=(30, 50),  # 30-50%
        operation_strategy="分批建仓，重点布局政策受益和业绩预增板块，控制节奏",
        risk_level="中",
        typical_duration_days=(20, 40)
    ),
    
    MarketState.SPRING_SUMMER_TRANSITION: StateDefinition(
        state=MarketState.SPRING_SUMMER_TRANSITION,
        chinese_name="春入夏过渡期",
        description="反弹趋势强化，赚钱效应显现，可适度加仓持有趋势明确的龙头个股",
        technical_characteristics=[
            "上涨股票比例>60%",
            "技术评分55-70",
            "趋势明显强化",
            "量价配合良好"
        ],
        fund_characteristics=[
            "资金加速流入",
            "主力积极做多",
            "散户跟风进场",
            "外资持续流入"
        ],
        sentiment_characteristics=[
            "积极情绪主导",
            "赚钱效应明显",
            "投资者热情高涨",
            "市场预期乐观"
        ],
        macro_characteristics=[
            "宏观政策持续利好",
            "经济复苏确认",
            "地缘环境良好",
            "流动性非常充裕"
        ],
        position_range=(40, 60),  # 40-60%
        operation_strategy="适度加仓，持有趋势明确的龙头个股，关注板块轮动",
        risk_level="中低",
        typical_duration_days=(15, 30)
    ),
    
    MarketState.SUMMER: StateDefinition(
        state=MarketState.SUMMER,
        chinese_name="夏长期",
        description="明确上涨趋势，市场情绪狂热，适合重仓持股享受趋势红利",
        technical_characteristics=[
            "上涨股票比例>70%",
            "技术评分>65",
            "强势上涨趋势",
            "连续突破新高"
        ],
        fund_characteristics=[
            "资金大幅流入",
            "主力强势做多",
            "散户疯狂追涨",
            "外资大幅流入"
        ],
        sentiment_characteristics=[
            "狂热情绪主导",
            "赚钱效应爆棚",
            "投资者极度乐观",
            "市场预期极度乐观"
        ],
        macro_characteristics=[
            "宏观政策极度宽松",
            "经济繁荣期",
            "地缘环境极佳",
            "流动性泛滥"
        ],
        position_range=(50, 80),  # 50-80%
        operation_strategy="重仓持股，趋势持有为主，适度做T，享受趋势红利",
        risk_level="低",
        typical_duration_days=(30, 90)
    ),
    
    MarketState.SUMMER_AUTUMN_TRANSITION: StateDefinition(
        state=MarketState.SUMMER_AUTUMN_TRANSITION,
        chinese_name="夏末秋初过渡期",
        description="上涨乏力，高位震荡，应分批减仓锁定利润，控制风险",
        technical_characteristics=[
            "上涨股票比例50-65%",
            "技术评分55-65",
            "上涨动能减弱",
            "高位震荡整理"
        ],
        fund_characteristics=[
            "资金流入放缓",
            "主力开始减仓",
            "散户犹豫不决",
            "外资流入减缓"
        ],
        sentiment_characteristics=[
            "犹豫情绪出现",
            "赚钱效应减弱",
            "投资者开始谨慎",
            "市场预期分化"
        ],
        macro_characteristics=[
            "宏观政策微调",
            "经济过热迹象",
            "地缘环境变化",
            "流动性开始收紧"
        ],
        position_range=(30, 50),  # 30-50%
        operation_strategy="分批减仓，锁定利润，控制风险，转向防御",
        risk_level="中",
        typical_duration_days=(15, 30)
    ),
    
    MarketState.AUTUMN: StateDefinition(
        state=MarketState.AUTUMN,
        chinese_name="秋收期",
        description="调整确认，市场情绪担忧，建议获利了结转向防御板块",
        technical_characteristics=[
            "下跌股票比例>55%",
            "技术评分40-55",
            "调整趋势确认",
            "关键技术位失守"
        ],
        fund_characteristics=[
            "资金开始流出",
            "主力持续减仓",
            "散户恐慌抛售",
            "外资开始流出"
        ],
        sentiment_characteristics=[
            "担忧情绪主导",
            "负面新闻增多",
            "投资者信心下降",
            "市场预期转弱"
        ],
        macro_characteristics=[
            "宏观政策收紧",
            "经济增速放缓",
            "地缘紧张加剧",
            "流动性收紧"
        ],
        position_range=(20, 40),  # 20-40%
        operation_strategy="获利了结，转向防御板块，保留现金，控制仓位",
        risk_level="中高",
        typical_duration_days=(20, 40)
    ),
    
    MarketState.AUTUMN_WINTER_TRANSITION: StateDefinition(
        state=MarketState.AUTUMN_WINTER_TRANSITION,
        chinese_name="秋入冬过渡期",
        description="调整加速，风险加大，应大幅减仓空仓为主等待冬藏结束",
        technical_characteristics=[
            "下跌股票比例>65%",
            "技术评分30-45",
            "调整加速",
            "连续破位下跌"
        ],
        fund_characteristics=[
            "资金加速流出",
            "主力大幅减仓",
            "散户恐慌抛售",
            "外资大幅流出"
        ],
        sentiment_characteristics=[
            "悲观情绪蔓延",
            "负面新闻频发",
            "投资者极度悲观",
            "市场预期极度悲观"
        ],
        macro_characteristics=[
            "宏观政策紧缩",
            "经济衰退迹象",
            "地缘危机爆发",
            "流动性极度紧张"
        ],
        position_range=(10, 30),  # 10-30%
        operation_strategy="大幅减仓，空仓为主，等待冬藏结束，不轻易抄底",
        risk_level="高",
        typical_duration_days=(10, 30)
    ),
    
    MarketState.CHAOS: StateDefinition(
        state=MarketState.CHAOS,
        chinese_name="混沌期",
        description="市场无明显趋势，多空博弈激烈，建议观望等待明确方向",
        technical_characteristics=[
            "涨跌股票比例接近",
            "技术评分40-60",
            "震荡无序",
            "无明显趋势"
        ],
        fund_characteristics=[
            "资金博弈激烈",
            "主力观望",
            "散户迷茫",
            "外资观望"
        ],
        sentiment_characteristics=[
            "迷茫情绪主导",
            "多空消息交织",
            "投资者方向不明",
            "市场预期混乱"
        ],
        macro_characteristics=[
            "宏观政策不明朗",
            "经济数据矛盾",
            "地缘环境复杂",
            "流动性中性"
        ],
        position_range=(10, 30),  # 10-30%
        operation_strategy="观望等待，小仓位试错，不追高不杀跌，等待明确信号",
        risk_level="中",
        typical_duration_days=(10, 40)
    )
}


def get_state_definition(state: MarketState) -> StateDefinition:
    """获取状态定义"""
    return STATE_DEFINITIONS.get(state)


def get_all_states() -> List[MarketState]:
    """获取所有状态"""
    return list(MarketState)


def get_state_description(state: MarketState) -> str:
    """获取状态描述"""
    definition = get_state_definition(state)
    return f"{definition.chinese_name}：{definition.description}" if definition else "未知状态"


def get_position_range(state: MarketState) -> Tuple[float, float]:
    """获取状态对应的仓位范围"""
    definition = get_state_definition(state)
    return definition.position_range if definition else (20, 40)


def get_operation_strategy(state: MarketState) -> str:
    """获取状态对应的操作策略"""
    definition = get_state_definition(state)
    return definition.operation_strategy if definition else "谨慎操作，控制风险"


def get_risk_level(state: MarketState) -> str:
    """获取状态对应的风险等级"""
    definition = get_state_definition(state)
    return definition.risk_level if definition else "中"


if __name__ == "__main__":
    # 测试状态定义
    print("动态状态演化系统 - 状态定义测试")
    print("=" * 60)
    
    for state in get_all_states():
        definition = get_state_definition(state)
        print(f"\n{definition.chinese_name} ({state.value}):")
        print(f"  描述: {definition.description}")
        print(f"  仓位范围: {definition.position_range[0]}%-{definition.position_range[1]}%")
        print(f"  操作策略: {definition.operation_strategy}")
        print(f"  风险等级: {definition.risk_level}")
        print(f"  典型持续时间: {definition.typical_duration_days[0]}-{definition.typical_duration_days[1]}天")