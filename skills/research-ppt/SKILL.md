# Research & PPT Report Skill

根据需求联网搜索、分析总结，自动生成 PPT 报告。

## 功能特点

- 🔍 **智能搜索** - 自动联网搜索相关信息
- 📊 **分析总结** - AI 智能分析关键信息
- 📄 **PPT 生成** - 自动生成专业 PPT 报告
- 🎯 **一键完成** - 输入主题，自动输出完整报告

## 使用方法

```json
{
  "tool": "research_ppt",
  "topic": "<研究主题>",
  "output": "<输出文件路径>",
  "slides": "<幻灯片数量>",  // 可选，默认 10
  "language": "<语言>"       // 可选，默认 "zh"
}
```

## 示例

```json
{
  "topic": "人工智能在医疗领域的应用",
  "output": "ai-medical-report.pptx",
  "slides": 12,
  "language": "zh"
}
```

## MCP 协议

```json
{
  "name": "research_ppt",
  "description": "联网搜索并生成 PPT 报告",
  "parameters": {
    "type": "object",
    "properties": {
      "topic": {
        "type": "string",
        "description": "研究主题或问题"
      },
      "output": {
        "type": "string",
        "description": "输出 PPT 文件路径"
      },
      "slides": {
        "type": "integer",
        "description": "幻灯片数量，默认 10"
      },
      "language": {
        "type": "string",
        "description": "语言，zh 或 en"
      }
    },
    "required": ["topic", "output"]
  }
}
```

## 依赖安装

```bash
pip install python-pptx requests beautifulsoup4
pip install openai anthropic  # 用于分析总结（可选）
```

## 工作流程

```
1. 用户输入研究主题
      ↓
2. 联网搜索相关信息
      ↓
3. 提取关键信息
      ↓
4. AI 分析总结
      ↓
5. 生成 PPT 幻灯片
      ↓
6. 输出 PPT 文件
```

## PPT 结构

每页 PPT 包含：
- 标题
- 关键要点 (3-5 个)
- 数据支撑
- 来源引用

## 输出示例

**主题**: "新能源汽车市场趋势"

**PPT 结构**:
1. 封面 - 新能源汽车市场趋势分析
2. 目录
3. 市场规模现状
4. 主要品牌分析
5. 技术发展趋势
6. 政策环境分析
7. 消费者偏好
8. 挑战与机遇
9. 未来预测
10. 总结与建议
