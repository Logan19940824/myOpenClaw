# Research & PPT Report Skill

根据研究主题，联网搜索、分析总结，自动生成专业 PPT 报告。

## ✨ 功能特点

- 🔍 **智能搜索** - 自动联网搜索相关信息（使用 DuckDuckGo）
- 📊 **分析总结** - 智能提取关键信息
- 📄 **PPT 生成** - 自动生成专业演示文稿
- 🌐 **多语言支持** - 中文、英文
- ⚡ **一键完成** - 输入主题，自动输出 PPT

## 📦 安装依赖

```bash
pip install python-pptx requests beautifulsoup4
```

## 🚀 使用方法

### 1. 命令行使用

```bash
# 基本用法
echo '{"topic": "人工智能发展趋势", "output": "ai-report.pptx"}' | python3 index.py

# 指定页数和语言
echo '{"topic": "新能源汽车市场", "output": "ev-report.pptx", "slides": 12, "language": "zh"}' | python3 index.py
```

**返回结果：**
```json
{
  "success": true,
  "output_path": "ai-report.pptx",
  "slides_created": 10,
  "sources": ["https://example.com/1", "https://example.com/2"],
  "error": null
}
```

### 2. 在 OpenClaw 中使用

Agent 会自动读取 `SKILL.md`，你只需用自然语言描述：

```
用户: "帮我生成一份关于区块链技术的 PPT 报告"
      ↓
Agent: 解析意图，调用 MCP skill
      ↓
MCP: 执行 research_ppt()
      ↓
输出: {"success": true, "output_path": "blockchain-report.pptx"}
```

## 📋 工作流程

```
┌─────────────────────────────────────────────────────────────────┐
│  用户输入研究主题                                                │
│  "帮我生成关于量子计算的 PPT"                                    │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. 联网搜索 (DuckDuckGo)                                        │
│     - 搜索关键词提取                                             │
│     - 获取搜索结果                                               │
│     - 提取标题和摘要                                             │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. 分析总结                                                     │
│     - 提取关键信息                                               │
│     - 生成 PPT 大纲                                              │
│     - 组织内容结构                                               │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. 生成 PPT (python-pptx)                                       │
│     - 封面页                                                     │
│     - 目录页                                                     │
│     - 内容页（市场、趋势、挑战、展望等）                          │
│     - 总结页                                                     │
│     - 参考资料页                                                 │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  输出 PPT 文件                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 PPT 结构

每份 PPT 包含以下页面：

| 页码 | 标题 | 内容 |
|------|------|------|
| 1 | 封面 | 主题 + 日期 |
| 2 | 目录 | 报告大纲 |
| 3 | 概述 | 研究背景、目的、方法 |
| 4 | 市场规模 | 行业现状、数据分析 |
| 5 | 主要趋势 | 技术/业务趋势 |
| 6 | 挑战与机遇 | 痛点、增长点 |
| 7 | 未来展望 | 短期/中期/长期预测 |
| 8 | 总结 | 核心发现、建议 |
| 9 | 参考资料 | 信息来源 |

## 🎯 使用场景

### 商业报告
```json
{
  "topic": "2024 年中国 SaaS 市场分析",
  "output": "saas-market-2024.pptx",
  "slides": 12,
  "language": "zh"
}
```

### 技术研究
```json
{
  "topic": "ChatGPT 和大语言模型发展趋势",
  "output": "llm-trends.pptx",
  "slides": 15,
  "language": "zh"
}
```

### 行业分析
```json
{
  "topic": "全球电动汽车市场趋势",
  "output": "ev-market-analysis.pptx",
  "slides": 10,
  "language": "zh"
}
```

### 英文报告
```json
{
  "topic": "AI in Healthcare Industry Report",
  "output": "ai-healthcare.pptx",
  "slides": 12,
  "language": "en"
}
```

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| **python-pptx** | PPT 文件生成 |
| **requests** | HTTP 请求 |
| **BeautifulSoup** | HTML 解析 |
| **DuckDuckGo** | 无需 API key 的搜索 |

## 📈 性能特点

| 指标 | 数值 |
|------|------|
| 搜索耗时 | ~2-3 秒 |
| 分析耗时 | ~1 秒 |
| PPT 生成 | ~1-2 秒 |
| 总耗时 | ~5-7 秒 |

## ⚠️ 注意事项

1. **网络依赖** - 需要网络连接进行搜索
2. **搜索结果** - 基于公开信息，不保证完整性
3. **内容质量** - AI 生成仅供参考，建议人工审核
4. **文件格式** - 输出为 .pptx 格式

## 🔧 进阶自定义

### 修改 PPT 样式

```python
# 在 index.py 中修改
prs.slide_width = Inches(13.333)  # 宽度
prs.slide_height = Inches(7.5)    # 高度

# 修改字体大小
p.font.size = Pt(24)
```

### 添加 Logo

```python
# 添加公司 Logo
slide.shapes.add_image('logo.png', Inches(0.5), Inches(0.3))
```

### 自定义颜色

```python
from pptx.dml.color import RgbColor

# 设置标题颜色
title_box.fill.solid()
title_box.fill.fore_color.rgb = RgbColor(0, 51, 102)
```

## 🐛 常见问题

### Q: 搜索失败怎么办？
A: 检查网络连接，skill 会使用默认内容继续生成。

### Q: 生成的 PPT 内容太少？
A: 可以增加 slides 参数，或后续手动编辑。

### Q: 支持图片插入吗？
A: 当前版本暂不支持自动图片插入，可手动添加。

### Q: 能生成其他格式吗？
A: 当前支持 .pptx，可另存为 PDF 或其他格式。

## 📝 License

基于 MIT License。
