#!/usr/bin/env python3
"""
Background Remove MCP Skill

使用 rembg AI 模型去除图片背景。

输入 (stdin):
{
  "input": "<图片路径>",
  "output": "<输出路径>"
}

输出 (stdout):
{
  "success": true,
  "output_path": "<输出路径>",
  "error": null
}
"""

import sys
import json
from rembg import remove
from PIL import Image


def remove_background(input_path, output_path):
    """
    去除图片背景
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径（PNG格式）
    
    Returns:
        dict: 结果
    """
    try:
        # 检查文件是否存在
        import os
        if not os.path.exists(input_path):
            return {
                "success": False,
                "output_path": None,
                "error": f"文件不存在: {input_path}"
            }
        
        # 打开并处理图片
        input_image = Image.open(input_path)
        
        # 去除背景
        output_image = remove(input_image)
        
        # 保存结果
        output_image.save(output_path, "PNG")
        
        return {
            "success": True,
            "output_path": output_path,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "output_path": None,
            "error": str(e)
        }


def main():
    """主函数 - 从 stdin 读取输入，输出结果到 stdout"""
    
    # 读取 stdin
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        result = {
            "success": False,
            "output_path": None,
            "error": "未收到输入数据"
        }
        print(json.dumps(result))
        return
    
    try:
        # 解析输入
        data = json.loads(input_data)
        input_path = data.get("input")
        output_path = data.get("output")
        
        if not input_path or not output_path:
            result = {
                "success": False,
                "output_path": None,
                "error": "缺少必要参数: input 和 output"
            }
            print(json.dumps(result))
            return
        
        # 执行去背景
        result = remove_background(input_path, output_path)
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        result = {
            "success": False,
            "output_path": None,
            "error": f"JSON 解析错误: {e}"
        }
        print(json.dumps(result))
    
    except Exception as e:
        result = {
            "success": False,
            "output_path": None,
            "error": f"处理错误: {e}"
        }
        print(json.dumps(result))


if __name__ == "__main__":
    main()
