# Text to Podcast Skill

将文本转换为自然流畅的播客音频。

## 使用方法

```json
{
  "tool": "text_to_podcast",
  "text": "<要转换的文本>",
  "voice": "<语音名称>",
  "output": "<输出文件路径>"
}
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| text | string | ✅ | 要转换的文本内容 |
| voice | string | ❌ | 语音名称，默认为 "zh-CN-XiaoxiaoNeural" (女声) |
| output | string | ✅ | 输出 MP3 文件路径 |

## 语音列表

**中文语音：**
- `zh-CN-XiaoxiaoNeural` - 晓晓 (女声，推荐)
- `zh-CN-XiaoyouNeural` - 悠悠 (童声)
- `zh-CN-YunxiNeural` - 云希 (男声)
- `zh-CN-YunyangNeural` - 云扬 (男声，新闻)

**英文语音：**
- `en-US-AriaNeural` - Aria (女声)
- `en-US-GuyNeural` - Guy (男声)
- `en-US-JennyNeural` - Jenny (女声)

## 示例

```json
{
  "text": "欢迎收听本期播客，今天我们来聊聊人工智能的发展。",
  "voice": "zh-CN-XiaoxiaoNeural",
  "output": "podcast-intro.mp3"
}
```

## MCP 协议

```json
{
  "name": "text_to_podcast",
  "description": "将文本转换为播客音频",
  "parameters": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "要转换为语音的文本内容"
      },
      "voice": {
        "type": "string",
        "description": "语音名称，默认为中文女声"
      },
      "output": {
        "type": "string",
        "description": "输出 MP3 文件路径"
      }
    },
    "required": ["text", "output"]
  }
}
```

## 依赖安装

```bash
pip install edge-tts
pip install asyncio
```
