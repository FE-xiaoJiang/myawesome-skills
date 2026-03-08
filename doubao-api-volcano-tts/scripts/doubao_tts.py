#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
火山引擎豆包语音合成 (Doubao TTS)
基于火山引擎（ByteDance）Doubao语音合成API实现
服务：音频生成 > 语音合成
控制台：https://console.volcengine.com/speech/service/8?AppID=7464343102
"""

import os
import sys
import json
import uuid
import base64
import requests
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

class DoubaoTTS:
    """火山引擎豆包语音合成客户端"""
    
    def __init__(self, appid: str = None, access_token: str = None, 
                 secret_key: str = None, cluster: str = "volcano_tts"):
        """
        初始化豆包TTS客户端
        
        Args:
            appid: 火山引擎AppID，如未提供则从环境变量读取
            access_token: API访问令牌，如未提供则从环境变量读取
            secret_key: API密钥，如未提供则从环境变量读取
            cluster: 服务集群，默认为 volcano_tts
            
        Raises:
            ValueError: 当必要的环境变量未设置时
        """
        self.appid = appid or os.getenv("DOUBAO_APPID")
        self.access_token = access_token or os.getenv("DOUBAO_ACCESS_TOKEN")
        self.secret_key = secret_key or os.getenv("DOUBAO_SECRET_KEY")
        self.cluster = cluster or os.getenv("DOUBAO_CLUSTER", "volcano_tts")
        
        if not self.appid:
            raise ValueError("火山引擎AppID未配置。请设置环境变量 DOUBAO_APPID")
        if not self.access_token:
            raise ValueError("API访问令牌未配置。请设置环境变量 DOUBAO_ACCESS_TOKEN")
        
        # API配置
        self.api_url = "https://openspeech.bytedance.com/api/v1/tts"
        self.default_voice_type = "zh_female_cancan_mars_bigtts"  # 灿灿/Shiny默认声音
        
        print(f"[Doubao TTS] 初始化完成，集群: {self.cluster}")
    
    def synthesize(self, text: str, output_file: Optional[str] = None, 
                   voice_type: Optional[str] = None, encoding: str = "mp3",
                   speed_ratio: float = 1.0, volume_ratio: float = 1.0,
                   pitch_ratio: float = 1.0) -> Optional[str]:
        """
        语音合成
        
        Args:
            text: 要合成的文本内容，建议不超过1000字符
            output_file: 输出音频文件路径，如不提供则返回base64音频数据
            voice_type: 声音类型，默认为 zh_female_cancan_mars_bigtts
            encoding: 音频编码格式，支持 mp3, pcm, wav
            speed_ratio: 语速比例 (0.5-2.0)
            volume_ratio: 音量比例 (0.5-2.0)
            pitch_ratio: 音调比例 (0.5-2.0)
            
        Returns:
            如果output_file提供，返回文件路径；否则返回base64音频数据字符串
            
        Raises:
            Exception: 当API调用失败或参数错误时
        """
        # 参数验证
        if not text or not text.strip():
            raise ValueError("合成的文本内容不能为空")
            
        text = text.strip()
        if len(text) > 1000:
            print(f"[警告] 文本长度({len(text)})较长，建议分批处理")
        
        # 使用默认voice_type或传入的voice_type
        voice_type = voice_type or self.default_voice_type
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer;{self.access_token}"
        }
        
        # 构建请求体
        payload = {
            "app": {
                "appid": self.appid,
                "token": self.access_token,
                "cluster": self.cluster
            },
            "user": {
                "uid": "12345678"  # 固定用户ID，可根据需要修改
            },
            "audio": {
                "voice_type": voice_type,
                "encoding": encoding,
                "channel": 1,
                "sample_rate": 24000,
                "bit_rate": 32000,
                "speed_ratio": max(0.5, min(2.0, speed_ratio)),
                "volume_ratio": max(0.5, min(2.0, volume_ratio)),
                "pitch_ratio": max(0.5, min(2.0, pitch_ratio))
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "text_type": "plain",
                "operation": "query"
            }
        }
        
        try:
            print(f"[Doubao TTS] 正在合成语音...")
            print(f"  文本长度: {len(text)} 字符")
            print(f"  声音类型: {voice_type}")
            print(f"  输出格式: {encoding}")
            
            # API调用
            response = requests.post(self.api_url, headers=headers, 
                                    json=payload, timeout=60)
            
            # 处理响应
            if response.status_code == 200:
                result = response.json()
                
                if result.get('code') == 3000 and result.get('data'):
                    # 解码base64音频数据
                    audio_data = base64.b64decode(result['data'])
                    
                    if output_file:
                        # 保存到文件
                        with open(output_file, 'wb') as f:
                            f.write(audio_data)
                        
                        print(f"[Doubao TTS] ✅ 音频保存成功: {output_file}")
                        print(f"  文件大小: {len(audio_data)} 字节")
                        return output_file
                    else:
                        # 返回base64数据
                        return result['data']
                else:
                    error_code = result.get('code', '未知')
                    error_msg = result.get('message', '未知错误')
                    error_msg_full = f"API错误 [{error_code}]: {error_msg}"
                    print(f"[Doubao TTS] ❌ {error_msg_full}")
                    raise Exception(error_msg_full)
            else:
                error_msg = f"HTTP错误 {response.status_code}: {response.text[:200]}"
                print(f"[Doubao TTS] ❌ {error_msg}")
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "请求超时，请检查网络或稍后重试"
            print(f"[Doubao TTS] ❌ {error_msg}")
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求异常: {str(e)}"
            print(f"[Doubao TTS] ❌ {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"处理异常: {str(e)}"
            print(f"[Doubao TTS] ❌ {error_msg}")
            raise Exception(error_msg)
    
    def get_available_voices(self) -> Dict[str, Any]:
        """
        获取可用声音列表
        
        Returns:
            声音类型分类字典
        """
        return {
            "confirmed_working": {
                "灿灿/Shiny (默认女声)": "zh_female_cancan_mars_bigtts",
                "猴哥 (Monkey King)": "zh_male_sunwukong_mars_bigtts",
                "流式语音700": "BV700_V2_streaming",
                "流式语音202": "BV202_streaming"
            },
            "needs_testing": {
                "男声苏葵": "zh_male_sokui",
                "女声苏葵": "zh_female_sokui",
                "配音男声": "zh_male_dubbing",
                "老电影男声": "zh_male_vintage_cinema"
            },
            "categories": [
                "zh_female_cancan_mars_bigtts",
                "zh_male_sunwukong_mars_bigtts",
                "BV700_V2_streaming",
                "BV202_streaming",
                "zh_female_sokui",
                "zh_male_sokui",
                "zh_male_dubbing",
                "zh_male_vintage_cinema"
            ]
        }
    
    def test_voice_type(self, voice_type: str, test_text: str = "测试语音合成") -> Tuple[bool, str]:
        """
        测试指定的声音类型是否可用
        
        Args:
            voice_type: 要测试的声音类型
            test_text: 测试文本
            
        Returns:
            (是否可用, 错误信息)
        """
        try:
            # 使用测试模式，不保存文件
            result = self.synthesize(
                text=test_text,
                voice_type=voice_type,
                encoding="mp3"
            )
            
            if result:
                return True, "声音类型可用"
            else:
                return False, "返回数据为空"
                
        except Exception as e:
            return False, str(e)

def main():
    """命令行接口"""
    if len(sys.argv) > 1:
        text = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else "output.mp3"
        voice_type = sys.argv[3] if len(sys.argv) > 3 else None
        
        try:
            tts = DoubaoTTS()
            
            # 配置声音类型
            kwargs = {}
            if voice_type:
                kwargs['voice_type'] = voice_type
            
            # 合成语音
            result = tts.synthesize(text, output_file, **kwargs)
            
            if result:
                print(f"✅ 合成成功: {result}")
                sys.exit(0)
            else:
                print("❌ 合成失败")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            sys.exit(1)
    else:
        print("火山引擎豆包语音合成技能")
        print("=" * 50)
        print("使用方式: python doubao_tts.py <文本> [输出文件] [声音类型]")
        print("\n示例:")
        print("  python doubao_tts.py \"你好世界\" hello.mp3")
        print("  python doubao_tts.py \"测试文本\" test.mp3 zh_male_sunwukong_mars_bigtts")
        print("\n环境变量:")
        print("  DOUBAO_APPID: 火山引擎应用ID")
        print("  DOUBAO_ACCESS_TOKEN: API访问令牌")
        print("  DOUBAO_SECRET_KEY: API密钥（可选）")
        print("  DOUBAO_CLUSTER: 服务集群（默认: volcano_tts）")
        sys.exit(0)

if __name__ == "__main__":
    main()