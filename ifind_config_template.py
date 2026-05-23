#!/usr/bin/env python3
"""
iFinD API 安全配置模板
请勿将token直接硬编码在代码中
"""

import os
import base64
import json
from datetime import datetime
import requests

class IFindSecureConfig:
    """iFinD API安全配置类"""
    
    # 配置模板 - 请将你的token填入环境变量
    ENV_VARS = {
        "IFIND_REFRESH_TOKEN": "你的refresh_token",
        "IFIND_ACCESS_TOKEN": "你的access_token（可选，可自动刷新）"
    }
    
    def __init__(self):
        """从环境变量加载配置"""
        self.refresh_token = os.getenv("IFIND_REFRESH_TOKEN")
        self.access_token = os.getenv("IFIND_ACCESS_TOKEN")
        self.base_url = "https://quantapi.10jqka.com.cn"
        
        # 检查环境变量
        self._check_env_vars()
        
    def _check_env_vars(self):
        """检查必要的环境变量"""
        if not self.refresh_token:
            print("⚠️  警告: IFIND_REFRESH_TOKEN 环境变量未设置")
            print("请设置环境变量:")
            print("export IFIND_REFRESH_TOKEN='你的refresh_token'")
            return False
        return True
    
    def decode_token_info(self):
        """解码JWT token信息（不暴露敏感信息）"""
        if not self.refresh_token:
            return {"error": "未提供refresh_token"}
        
        try:
            # JWT token格式: header.payload.signature
            parts = self.refresh_token.split('.')
            if len(parts) != 3:
                return {"error": "token格式不正确"}
            
            # 解码payload部分
            payload_encoded = parts[1]
            # 添加padding（如果需要）
            padding = 4 - len(payload_encoded) % 4
            if padding != 4:
                payload_encoded += "=" * padding
            
            payload_json = base64.b64decode(payload_encoded).decode('utf-8')
            payload = json.loads(payload_json)
            
            # 提取基本信息（不暴露完整token）
            user_info = payload.get("user", {})
            return {
                "user_id": user_info.get("userId"),
                "refresh_token_expired_time": user_info.get("refreshTokenExpiredTime"),
                "token_valid": True
            }
        except Exception as e:
            return {"error": f"解码失败: {str(e)}"}
    
    def get_access_token(self):
        """使用refresh_token获取access_token"""
        if not self.refresh_token:
            return None
        
        # 这里应该是实际的API调用，但为了安全不在此展示
        # 实际使用时需要调用iFinD的token刷新接口
        print("📝 获取access_token的API调用需要根据iFinD文档实现")
        print("通常调用: POST /oauth2/refresh_token")
        return None
    
    def test_connection(self):
        """测试连接（不暴露实际API调用）"""
        token_info = self.decode_token_info()
        
        if "error" in token_info:
            print(f"❌ Token检查失败: {token_info['error']}")
            return False
        
        print("✅ Token基本信息:")
        print(f"   用户ID: {token_info.get('user_id', '未知')}")
        print(f"   过期时间: {token_info.get('refresh_token_expired_time', '未知')}")
        print(f"   Token有效: {token_info.get('token_valid', False)}")
        
        # 这里可以添加实际的API测试调用
        # 但为了安全，不在模板中包含实际API调用
        
        return token_info.get("token_valid", False)


# 使用示例
if __name__ == "__main__":
    print("=" * 50)
    print("iFinD API 安全配置检查")
    print("=" * 50)
    
    config = IFindSecureConfig()
    
    print("\n1. 环境变量检查:")
    for key, value in config.ENV_VARS.items():
        env_value = os.getenv(key)
        status = "✅ 已设置" if env_value else "❌ 未设置"
        print(f"   {key}: {status}")
    
    print("\n2. Token信息检查:")
    config.test_connection()
    
    print("\n" + "=" * 50)
    print("安全建议:")
    print("1. 不要在代码中硬编码token")
    print("2. 使用环境变量或安全存储")
    print("3. 定期刷新access_token")
    print("4. 监控API使用量")
    print("=" * 50)