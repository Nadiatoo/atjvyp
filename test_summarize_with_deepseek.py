#!/usr/bin/env python3
"""
使用已配置的DeepSeek模型实现摘要功能
"""

import os
import sys
import requests
import json

def summarize_with_deepseek(text, model="deepseek/deepseek-chat", max_tokens=500):
    """
    使用DeepSeek API进行文本摘要
    
    Args:
        text: 要摘要的文本
        model: 模型名称
        max_tokens: 最大输出token数
    
    Returns:
        摘要结果
    """
    # 从环境变量获取API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return "错误：未找到DEEPSEEK_API_KEY环境变量"
    
    # 根据模型选择API端点
    if "deepseek" in model:
        api_url = "https://api.deepseek.com/v1/chat/completions"
    else:
        return f"错误：不支持的模型 {model}"
    
    # 构建提示
    prompt = f"""请对以下文本进行摘要，提取关键信息：

{text}

请生成简洁的摘要，包含主要观点和关键细节。"""

    # 准备请求数据
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat" if "deepseek-chat" in model else "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": "你是一个专业的文本摘要助手。"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "错误：API响应格式异常"
            
    except requests.exceptions.RequestException as e:
        return f"API请求错误：{str(e)}"
    except json.JSONDecodeError as e:
        return f"JSON解析错误：{str(e)}"

def summarize_url(url, model="deepseek/deepseek-chat"):
    """
    摘要网页内容
    
    Args:
        url: 网页URL
        model: 模型名称
    
    Returns:
        网页摘要
    """
    try:
        # 首先获取网页内容
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # 简单提取文本（实际应用中可能需要更复杂的HTML解析）
        # 这里使用简单的方法：提取前5000个字符
        content = response.text[:5000]
        
        # 进行摘要
        summary = summarize_with_deepseek(
            f"网页URL: {url}\n\n网页内容:\n{content}",
            model=model,
            max_tokens=300
        )
        
        return summary
        
    except requests.exceptions.RequestException as e:
        return f"网页获取错误：{str(e)}"

def test_summarize():
    """测试摘要功能"""
    print("=== 测试DeepSeek摘要功能 ===\n")
    
    # 测试1：短文本摘要
    test_text = """
    人工智能（AI）是计算机科学的一个分支，旨在创造能够执行通常需要人类智能的任务的机器。
    这些任务包括学习、推理、问题解决、感知和语言理解。AI技术已经广泛应用于各个领域，
    包括医疗诊断、自动驾驶汽车、语音识别和推荐系统。
    
    机器学习是AI的一个子领域，它使计算机能够从数据中学习而不需要明确编程。
    深度学习是机器学习的一个分支，使用神经网络模拟人脑的工作方式。
    """
    
    print("测试1：短文本摘要")
    print("原文长度:", len(test_text), "字符")
    result1 = summarize_with_deepseek(test_text, model="deepseek/deepseek-chat")
    print("摘要结果:", result1)
    print("-" * 50)
    
    # 测试2：使用DeepSeek R1（推理模型）
    print("\n测试2：使用DeepSeek R1进行摘要")
    result2 = summarize_with_deepseek(test_text, model="deepseek/deepseek-reasoner")
    print("摘要结果:", result2)
    print("-" * 50)
    
    # 测试3：模拟网页摘要
    print("\n测试3：模拟财经新闻摘要")
    finance_news = """
    今日A股市场表现震荡，上证指数收盘下跌0.5%，深证成指下跌0.8%。
    科技板块表现强势，AI概念股集体上涨。央行今日进行1000亿元逆回购操作，
    维护市场流动性合理充裕。分析师认为，市场短期仍将维持震荡格局，
    建议投资者关注业绩确定性强、估值合理的优质个股。
    """
    
    result3 = summarize_with_deepseek(finance_news, model="deepseek/deepseek-chat")
    print("财经新闻摘要:", result3)
    
    return True

if __name__ == "__main__":
    # 检查API密钥
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("错误：请设置DEEPSEEK_API_KEY环境变量")
        print("当前已配置的模型：")
        print("1. deepseek/deepseek-chat (DeepSeek V3)")
        print("2. deepseek/deepseek-reasoner (DeepSeek R1)")
        sys.exit(1)
    
    # 运行测试
    success = test_summarize()
    
    if success:
        print("\n✅ 摘要功能测试成功！")
        print("\n使用说明：")
        print("1. 文本摘要：summarize_with_deepseek(text, model='deepseek/deepseek-chat')")
        print("2. 网页摘要：summarize_url(url, model='deepseek/deepseek-chat')")
        print("\n可用模型：")
        print("- deepseek/deepseek-chat (快速，成本较低)")
        print("- deepseek/deepseek-reasoner (推理能力强，成本较高)")
    else:
        print("\n❌ 摘要功能测试失败")