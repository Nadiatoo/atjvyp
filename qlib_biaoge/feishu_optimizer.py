#!/usr/bin/env python3
"""
飞书消息发送优化工具
- 合并多条消息
- 减少 API 调用次数
- Token 使用监控
"""

import logging
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MessageBuffer:
    """消息缓冲区"""
    text_parts: List[str]
    images: List[str]
    
    def __init__(self):
        self.text_parts = []
        self.images = []
    
    def add_text(self, text: str):
        """添加文字内容"""
        self.text_parts.append(text)
    
    def add_image(self, image_path: str):
        """添加图片路径"""
        self.images.append(image_path)
    
    def is_empty(self) -> bool:
        """检查是否为空"""
        return len(self.text_parts) == 0 and len(self.images) == 0
    
    def flush(self) -> tuple:
        """清空并返回累积的内容"""
        combined_text = "\n\n".join(self.text_parts) if self.text_parts else ""
        images = self.images.copy()
        
        # 清空
        self.text_parts = []
        self.images = []
        
        return combined_text, images


class FeishuMessageOptimizer:
    """飞书消息发送优化器"""
    
    def __init__(self):
        self.buffer = MessageBuffer()
        self.api_call_count = 0
        self.daily_limit = 10  # 每日 API 调用上限
    
    def add_to_buffer(self, text: str = None, image: str = None):
        """添加到缓冲区（不立即发送）"""
        if text:
            self.buffer.add_text(text)
        if image:
            self.buffer.add_image(image)
    
    def send_buffered(self, target: str = None) -> bool:
        """发送缓冲区内容（合并为一次调用）"""
        if self.buffer.is_empty():
            return True
        
        # 检查 API 调用次数
        if self.api_call_count >= self.daily_limit:
            logger.warning(f"API 调用次数已达上限: {self.daily_limit}")
            return False
        
        combined_text, images = self.buffer.flush()
        
        try:
            # 合并为一次发送
            if images:
                # 如果有图片，只发第一张，其他放云盘链接
                from message_tool import send_message
                
                # 文字 + 第一张图片
                result = send_message(
                    target=target,
                    text=combined_text[:2000],  # 限制长度
                    media=images[0] if images else None
                )
                
                # 多余图片提示用户去桌面查看
                if len(images) > 1:
                    logger.info(f"还有 {len(images)-1} 张图片保存在桌面")
            else:
                # 纯文字
                result = send_message(
                    target=target,
                    text=combined_text[:3000]  # 限制长度
                )
            
            self.api_call_count += 1
            logger.info(f"API 调用次数: {self.api_call_count}/{self.daily_limit}")
            return True
            
        except Exception as e:
            logger.error(f"发送失败: {e}")
            return False
    
    def get_status(self) -> dict:
        """获取当前状态"""
        return {
            "api_calls_today": self.api_call_count,
            "api_limit": self.daily_limit,
            "buffer_size": len(self.buffer.text_parts),
            "remaining_calls": self.daily_limit - self.api_call_count
        }


# 全局实例
optimizer = FeishuMessageOptimizer()


def send_optimized(text: str = None, image: str = None, target: str = None, flush: bool = False):
    """
    优化的发送函数
    
    Args:
        text: 文字内容
        image: 图片路径
        target: 发送目标
        flush: 是否立即发送（False则加入缓冲区）
    
    用法:
        # 批量添加
        send_optimized("第一部分")
        send_optimized("第二部分")
        send_optimized("第三部分")
        
        # 最后一次性发送
        send_optimized(flush=True)
    """
    if text or image:
        optimizer.add_to_buffer(text, image)
    
    if flush:
        return optimizer.send_buffered(target)
    
    return True


def show_token_usage():
    """显示 Token 使用情况"""
    try:
        from session_status_tool import session_status
        status = session_status()
        
        logger.info("=" * 50)
        logger.info("Token 使用情况")
        logger.info("=" * 50)
        logger.info(f"Input:  {status.tokens.in} tokens")
        logger.info(f"Output: {status.tokens.out} tokens")
        logger.info(f"Total:  {status.tokens.in + status.tokens.out} tokens")
        logger.info(f"Context: {status.context.percent}%")
        logger.info("=" * 50)
        
        # 如果超过 80% 提醒清理
        if status.context.percent > 80:
            logger.warning("⚠️ 上下文接近上限，建议开始新会话")
        
        return status
    except Exception as e:
        logger.error(f"获取 Token 使用情况失败: {e}")
        return None


# 测试
if __name__ == "__main__":
    # 测试批量发送
    send_optimized("【测试】第一部分")
    send_optimized("【测试】第二部分")
    send_optimized("【测试】第三部分")
    
    # 显示状态
    print(optimizer.get_status())
    
    # 实际发送时取消注释
    # send_optimized(flush=True, target="your_target_id")
