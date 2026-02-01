# Calculator Skill

一个简单的计算器技能，支持加减乘除运算。

## 使用方法

```json
{
  "tool": "calculator",
  "action": "add|sub|mul|div",
  "a": <第一个数字>,
  "b": <第二个数字>
}
```

## 示例

- 加法: `{"action": "add", "a": 10, "b": 5}` → 15
- 减法: `{"action": "sub", "a": 10, "b": 5}` → 5
- 乘法: `{"action": "mul", "a": 10, "b": 5}` → 50
- 除法: `{"action": "div", "a": 10, "b": 5}` → 2

## MCP 协议

```json
{
  "name": "calculator",
  "description": "执行基本数学运算",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["add", "sub", "mul", "div"],
        "description": "运算操作"
      },
      "a": {
        "type": "number",
        "description": "第一个数字"
      },
      "b": {
        "type": "number",
        "description": "第二个数字"
      }
    },
    "required": ["action", "a", "b"]
  }
}
```
