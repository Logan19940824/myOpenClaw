#!/usr/bin/env python3
"""
Text to Podcast MCP Skill

使用 Microsoft Edge TTS 将文本转换为播客音频。

输入 (stdin):
{
  "text": "<文本内容>",
  "voice": "<语音名称>",  // 可选，默认 zh-CN-XiaoxiaoNeural
  "output": "<输出文件路径>"
}

输出 (stdout):
{
  "success": true,
  "output_path": "<输出路径>",
  "duration": <音频时长(秒)>,
  "error": null
}
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import edge_tts


# 默认语音
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"


async def text_to_podcast(text: str, voice: str, output_path: str) -> dict:
    """
    将文本转换为播客音频
    
    Args:
        text: 要转换的文本
        voice: 语音名称
        output_path: 输出文件路径
    
    Returns:
        dict: 结果
    """
    try:
        # 验证输入
        if not text or not text.strip():
            return {
                "success": False,
                "output_path": None,
                "duration": None,
                "error": "文本内容不能为空"
            }
        
        if not output_path:
            return {
                "success": False,
                "output_path": None,
                "duration": None,
                "error": "输出路径不能为空"
            }
        
        # 创建输出目录
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用 edge-tts 生成语音
        communicate = edge_tts.Communicate(text, voice)
        
        # 保存音频文件
        await communicate.save(str(output_file))
        
        # 获取文件信息
        file_size = output_file.stat().st_size
        
        return {
            "success": True,
            "output_path": str(output_file),
            "file_size": file_size,
            "voice": voice,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "output_path": None,
            "duration": None,
            "error": str(e)
        }


async def main():
    """主函数"""
    
    # 读取 stdin
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        result = {
            "success": False,
            "output_path": None,
            "duration": None,
            "error": "未收到输入数据"
        }
        print(json.dumps(result))
        return
    
    try:
        # 解析输入
        data = json.loads(input_data)
        text = data.get("text")
        voice = data.get("voice", DEFAULT_VOICE)
        output = data.get("output")
        
        if not text:
            result = {
                "success": False,
                "output_path": None,
                "duration": None,
                "error": "缺少必要参数: text"
            }
            print(json.dumps(result))
            return
        
        if not output:
            result = {
                "success": False,
                "output_path": None,
                "duration": None,
                "error": "缺少必要参数: output"
            }
            print(json.dumps(result))
            return
        
        # 执行转换
        result = await text_to_podcast(text, voice, output)
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        result = {
            "success": False,
            "output_path": None,
            "duration": None,
            "error": f"JSON 解析错误: {e}"
        }
        print(json.dumps(result))
    
    except Exception as e:
        result = {
            "success": False,
            "output_path": None,
            "duration": None,
            "error": f"处理错误: {e}"
        }
        print(json.dumps(result))


if __name__ == "__main__":
    asyncio.run(main())
