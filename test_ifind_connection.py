#!/usr/bin/env python3
"""
iFinD API连接测试脚本
安全版本：不暴露敏感信息
"""

import os
import sys
import json
import base64
import requests
from datetime import datetime

class IFindConnectionTester:
    """iFinD API连接测试器"""
    
    def __init__(self):
        self.refresh_token = os.getenv("IFIND_REFRESH_TOKEN")
        self.base_url = "https://quantapi.10jqka.com.cn"
        
    def safe_token_info(self):
        """安全地显示token信息（不暴露完整token）"""
        if not self.refresh_token:
            return {"error": "未设置IFIND_REFRESH_TOKEN环境变量"}
        
        try:
            # 只显示token的前10位和最后5位
            token_len = len(self.refresh_token)
            masked_token = f"{self.refresh_token[:10]}...{self.refresh_token[-5:]}"
            
            # 尝试解析JWT token（仅基本信息）
            parts = self.refresh_token.split('.')
            if len(parts) == 3:
                try:
                    # 解码payload
                    payload_b64 = parts[1]
                    # 添加padding
                    missing_padding = len(payload_b64) % 4
                    if missing_padding:
                        payload_b64 += '=' * (4 - missing_padding)
                    
                    payload_json = base64.b64decode(payload_b64).decode('utf-8')
                    payload = json.loads(payload_json)
                    
                    user_info = payload.get('user', {})
                    return {
                        "token_masked": masked_token,
                        "token_length": token_len,
                        "user_id": user_info.get('userId'),
                        "refresh_expiry": user_info.get('refreshTokenExpiredTime'),
                        "is_valid_jwt": True
                    }
                except:
                    return {
                        "token_masked": masked_token,
                        "token_length": token_len,
                        "is_valid_jwt": False
                    }
            else:
                return {
                    "token_masked": masked_token,
                    "token_length": token_len,
                    "is_valid_jwt": False
                }
        except Exception as e:
            return {"error": f"解析失败: {str(e)}"}
    
    def refresh_access_token(self):
        """刷新access_token（根据iFinD文档）"""
        if not self.refresh_token:
            return None
        
        # iFinD API文档中的token刷新示例
        # 实际URL可能需要根据文档调整
        refresh_url = f"{self.base_url}/oauth2/refresh_token"
        
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "refresh_token": self.refresh_token,
                "grant_type": "refresh_token"
            }
            
            print(f"🔄 正在刷新access_token...")
            response = requests.post(refresh_url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                access_token = result.get("access_token")
                expires_in = result.get("expires_in", 7200)  # 默认2小时
                
                if access_token:
                    print(f"✅ Access Token获取成功")
                    print(f"   有效期: {expires_in}秒 ({expires_in/3600:.1f}小时)")
                    return access_token
                else:
                    print(f"❌ 响应中未找到access_token")
                    print(f"   响应: {result}")
            else:
                print(f"❌ 刷新失败，状态码: {response.status_code}")
                print(f"   响应: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求失败: {str(e)}")
        except Exception as e:
            print(f"❌ 刷新失败: {str(e)}")
        
        return None
    
    def test_basic_api(self, access_token=None):
        """测试基础API调用"""
        if not access_token:
            print("⚠️  未提供access_token，跳过API测试")
            return False
        
        # 简单的API测试 - 获取基础信息
        test_url = f"{self.base_url}/api/v1/user/info"
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            print(f"🔍 测试API连接...")
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API连接成功")
                
                # 显示部分信息
                if 'data' in result:
                    data = result['data']
                    print(f"   用户信息: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                return True
            else:
                print(f"❌ API测试失败，状态码: {response.status_code}")
                print(f"   响应: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ API测试异常: {str(e)}")
        
        return False
    
    def get_stock_data_example(self, access_token, symbol="000001"):
        """获取股票数据示例"""
        if not access_token:
            return None
        
        # 股票数据API示例
        # 实际API端点需要根据iFinD文档确定
        stock_url = f"{self.base_url}/api/v1/stock/basic"
        
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "symbol": symbol,
                "fields": "symbol,name,close,change,change_rate"
            }
            
            print(f"📈 获取股票数据 {symbol}...")
            response = requests.get(stock_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 股票数据获取成功")
                return result
            else:
                print(f"❌ 股票数据获取失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 股票数据获取异常: {str(e)}")
        
        return None
    
    def run_full_test(self):
        """运行完整测试"""
        print("=" * 60)
        print("iFinD API 连接测试")
        print("=" * 60)
        
        # 1. 检查环境变量
        print("\n1. 环境变量检查:")
        if not self.refresh_token:
            print("❌ IFIND_REFRESH_TOKEN 未设置")
            print("   请运行: bash /Users/tuqibiao/.openclaw/workspace/setup_ifind_env.sh")
            return False
        else:
            print("✅ IFIND_REFRESH_TOKEN 已设置")
        
        # 2. Token信息
        print("\n2. Token信息:")
        token_info = self.safe_token_info()
        if "error" in token_info:
            print(f"❌ {token_info['error']}")
            return False
        
        print(f"   Token: {token_info.get('token_masked')}")
        print(f"   长度: {token_info.get('token_length')} 字符")
        print(f"   JWT格式: {'✅ 有效' if token_info.get('is_valid_jwt') else '❌ 无效'}")
        
        if token_info.get('user_id'):
            print(f"   用户ID: {token_info.get('user_id')}")
        if token_info.get('refresh_expiry'):
            print(f"   刷新过期: {token_info.get('refresh_expiry')}")
        
        # 3. 刷新access_token
        print("\n3. 获取Access Token:")
        access_token = self.refresh_access_token()
        
        if access_token:
            # 4. 测试API
            print("\n4. API连接测试:")
            api_success = self.test_basic_api(access_token)
            
            if api_success:
                print("\n" + "=" * 60)
                print("✅ iFinD API 连接测试通过")
                print("=" * 60)
                
                # 可选：测试股票数据
                test_stock = input("\n是否测试股票数据获取？(y/n): ")
                if test_stock.lower() == 'y':
                    symbol = input("请输入股票代码（默认000001）: ") or "000001"
                    stock_data = self.get_stock_data_example(access_token, symbol)
                    if stock_data:
                        print(f"\n📊 股票数据示例:")
                        print(json.dumps(stock_data, ensure_ascii=False, indent=2)[:500] + "...")
                
                return True
            else:
                print("\n❌ API连接测试失败")
                return False
        else:
            print("\n❌ 无法获取Access Token")
            return False


if __name__ == "__main__":
    tester = IFindConnectionTester()
    
    try:
        success = tester.run_full_test()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n测试已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        sys.exit(1)