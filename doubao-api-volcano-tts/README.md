# 火山引擎豆包语音合成技能 (Doubao API TTS)

## 概述
这是一个基于火山引擎（字节跳动）Doubao语音合成API的文本转语音技能。支持高质量的中英文语音合成，多种声音类型可选，适用于AI助手、播客生成、辅助阅读等场景。

## 火山引擎控制台
- **服务模块**: 音频生成 > 语音合成
- **控制台URL**: https://console.volcengine.com/speech/service/8?AppID=7464343102
- **API文档**: https://www.volcengine.com/docs/6561/107708

## 功能特性
- ✅ 支持中英文语音合成
- ✅ 200+声音类型可选
- ✅ 多种音频格式输出 (MP3, PCM, WAV)
- ✅ 可调节语速、音量、音调
- ✅ 长文本自动处理
- ✅ 完整的错误处理机制

## 安装配置

### 1. 环境变量配置
```bash
# 火山引擎豆包API凭据
export DOUBAO_APPID="your_app_id"              # 应用ID
export DOUBAO_ACCESS_TOKEN="your_access_token" # 访问令牌
export DOUBAO_SECRET_KEY="your_secret_key"     # 密钥（部分接口使用）
export DOUBAO_CLUSTER="volcano_tts"            # 服务集群
```

### 2. 依赖安装
```bash
pip install requests
```

## 使用方法

### 基础使用
```python
from skills.doubao_tts import DoubaoTTS

# 初始化客户端
tts = DoubaoTTS()

# 语音合成
audio_path = tts.synthesize(
    text="要合成的文本内容",
    output_file="output.mp3"
)
```

### 使用指定声音类型
```python
# 使用译制片风格男声（猴哥角色）
audio_path = tts.synthesize(
    text="文本内容",
    output_file="output.mp3",
    voice_type="zh_male_sunwukong_mars_bigtts"  # 猴哥声音
)

# 使用流式语音
audio_path = tts.synthesize(
    text="文本内容",
    output_file="output.mp3",
    voice_type="BV700_V2_streaming"  # 流式语音700
)
```

### 调整语音参数
```python
audio_path = tts.synthesize(
    text="文本内容",
    output_file="output.mp3",
    voice_type="zh_female_cancan_mars_bigtts",  # 灿灿女声
    speed_ratio=1.2,    # 语速 (0.5-2.0)
    volume_ratio=0.8,   # 音量 (0.5-2.0)
    pitch_ratio=1.0,    # 音调 (0.5-2.0)
    encoding="mp3"      # 音频格式: mp3, pcm, wav
)
```

## 常用声音类型
根据测试，以下声音类型已确认可用：

### 通用声音
| 中文描述 | voice_type参数 | 特点 |
|---------|---------------|------|
| 灿灿/Shiny (默认) | `zh_female_cancan_mars_bigtts` | 通用女声，中英文 |
| 猴哥 | `zh_male_sunwukong_mars_bigtts` | 角色男声，有特色 |
| 流式语音700 | `BV700_V2_streaming` | 流式合成，响应快 |
| 流式语音202 | `BV202_streaming` | 流式合成，标准 |

### 其他可用声音
- `zh_male_sokui` - 男声苏葵
- `zh_female_sokui` - 女声苏葵

## API服务配置

### 1. 开通服务
1. 登录火山引擎控制台：https://console.volcengine.com/
2. 进入"音频生成 > 语音合成"服务
3. 创建应用，获取 AppID、Access Token 和 Secret Key

### 2. API详情
- **端点**: `https://openspeech.bytedance.com/api/v1/tts`
- **认证方式**: Bearer Token (`Authorization: Bearer;{access_token}`)
- **响应格式**: JSON，音频数据以base64编码在`data`字段中
- **必填参数**: `appid`, `access_token`, `cluster`

### 3. 请求示例
```json
{
  "app": {
    "appid": "your_appid",
    "token": "your_token",
    "cluster": "volcano_tts"
  },
  "user": {
    "uid": "user_id"
  },
  "audio": {
    "voice_type": "zh_female_cancan_mars_bigtts",
    "encoding": "mp3",
    "speed_ratio": 1.0,
    "volume_ratio": 1.0
  },
  "request": {
    "reqid": "unique_request_id",
    "text": "要合成的文本",
    "text_type": "plain",
    "operation": "query"
  }
}
```

## 错误处理
技能包含完整的错误处理机制：

1. **环境验证**：检查必要的环境变量
2. **参数验证**：验证文本、声音类型等参数
3. **API错误**：处理火山引擎API返回的错误
4. **网络异常**：处理超时、连接失败等情况

## 示例代码

### 示例1：生成哲学思考音频
```python
from skills.doubao_tts import DoubaoTTS

tts = DoubaoTTS()

text = """老一辈人经常说，年轻人要多多接受苦难的毒打，吃得苦中苦，方为人上人。他们的逻辑是活得久等于活得通透，等于思想深刻。而事实上，随着年龄越来越深刻的，只有脸上的皱纹。人在顺境中很难产生深刻的思考，很多东西确实只有在逆境中才能感知。一个深刻而通透的人，必须经历怀疑一切，摧毁一切，重建一切，而这三步分别对应的是苦难、勇气和认知，三点缺一不可。"""

audio_path = tts.synthesize(
    text=text,
    output_file="philosophy_speech.mp3",
    voice_type="zh_male_sunwukong_mars_bigtts"
)

print(f"音频已生成: {audio_path}")
```

### 示例2：批量生成音频
```python
import os
from skills.doubao_tts import DoubaoTTS

tts = DoubaoTTS()

texts = [
    "欢迎使用豆包语音合成",
    "这里是第二个音频片段",
    "语音合成质量优秀，自然流畅"
]

for i, text in enumerate(texts):
    output_file = f"audio_{i+1}.mp3"
    audio_path = tts.synthesize(text, output_file)
    print(f"生成: {output_file}")
```

## 性能提示
1. **文本长度**：建议单次请求不超过1000字符，长文本可分多次
2. **声音选择**：不同的声音类型可能有不同的性能表现
3. **网络延迟**：首次请求可能较慢，建议添加超时处理
4. **错误重试**：网络波动时可考虑添加重试机制

## 测试验证
本技能已通过以下测试：
- ✅ 短文本合成 (test_short.mp3)
- ✅ 长文本合成 (philosophical_speech_2mb.mp3)
- ✅ 指定声音类型 (BV700_V2_streaming)
- ✅ 参数调整 (语速、音量)
- ✅ 错误处理和环境验证

## 许可证
MIT License

## 开发者
- GitHub: https://github.com/FE-xiaoJiang/myawesome-skills
- 技能目录: /doubao-api-volcano-tts/

## 更新日志
- v1.0.0 (2026-03-09): 初始版本发布
  - 基本语音合成功能
  - 多种声音类型支持
  - 完整错误处理
  - 环境变量配置