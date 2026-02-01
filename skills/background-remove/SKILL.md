# Background Remove Skill

使用 AI 自动去除图片背景。

## 使用方法

```json
{
  "tool": "background_remove",
  "input": "<图片文件路径>",
  "output": "<输出文件路径>"
}
```

## 示例

```json
{
  "input": "photo.jpg",
  "output": "photo-no-bg.png"
}
```

## MCP 协议

```json
{
  "name": "background_remove",
  "description": "使用 AI 去除图片背景",
  "parameters": {
    "type": "object",
    "properties": {
      "input": {
        "type": "string",
        "description": "输入图片路径"
      },
      "output": {
        "type": "string",
        "description": "输出图片路径"
      }
    },
    "required": ["input", "output"]
  }
}
```

## 依赖安装

```bash
pip install rembg
pip install pillow
```

## 支持格式

- 输入: JPG, PNG, BMP, WEBP
- 输出: PNG (透明背景)
