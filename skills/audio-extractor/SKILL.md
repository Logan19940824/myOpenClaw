# Audio Extractor & ASR Skill

从视频中提取音频，并使用 ASR (自动语音识别) 生成带时间轴的字幕文件。

## 功能特点

- 🎵 **提取音频** - 从 MP4 视频中提取音频为 WAV/MP3
- 📝 **ASR 识别** - 自动识别语音生成字幕
- ⏱️ **时间轴** - 生成精确的时间轴字幕 (SRT/VTT 格式)
- 🌐 **多语言** - 支持中文、英文等多种语言
- 💾 **多种格式** - 支持导出 SRT、VTT、JSON 格式

## 使用方法

```json
{
  "tool": "audio_extractor",
  "video": "<视频文件路径>",
  "output": "<输出目录>",
  "format": "srt",         // 可选，默认 srt
  "language": "zh",        // 可选，默认 zh
  "extract_audio": true    // 可选，默认 true
}
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| video | string | ✅ | 输入视频文件路径 |
| output | string | ✅ | 输出目录 |
| format | string | ❌ | 字幕格式，srt/vtt/json |
| language | string | ❌ | 语言，zh/en，默认 zh |
| extract_audio | bool | ❌ | 是否提取音频，默认 true |

## 输出文件

```
output/
├── audio.wav              # 提取的音频（如果 extract_audio=true）
├── subtitles.srt          # SRT 格式字幕
├── subtitles.vtt          # VTT 格式字幕（可选）
└── subtitles.json         # JSON 格式（可选）
```

## 示例

```json
{
  "video": "interview.mp4",
  "output": "./results",
  "format": "srt",
  "language": "zh",
  "extract_audio": true
}
```

## MCP 协议

```json
{
  "name": "audio_extractor",
  "description": "从视频提取音频并生成 ASR 字幕",
  "parameters": {
    "type": "object",
    "properties": {
      "video": {
        "type": "string",
        "description": "输入视频文件路径"
      },
      "output": {
        "type": "string",
        "description": "输出目录"
      },
      "format": {
        "type": "string",
        "description": "字幕格式"
      },
      "language": {
        "type": "string",
        "description": "识别语言"
      },
      "extract_audio": {
        "type": "boolean",
        "description": "是否提取音频"
      }
    },
    "required": ["video", "output"]
  }
}
```

## 依赖安装

```bash
pip install moviepy whisper
# 需要先安装 ffmpeg
```
