# WeChat Article Formatter Skill

将 Markdown 文件自动排版成微信公众号推文格式，支持图片插入。

## ✨ 功能特点

- 📝 **MD 转微信格式** - 自动转换 Markdown 为微信公众号 HTML
- 🎨 **5 套精美主题** - 优雅简洁、暗黑、蓝色、粉色、极简
- 🖼️ **图片插入** - 支持封面图和正文插图
- 📱 **移动端适配** - 响应式设计，完美适配手机阅读
- 🔗 **微信优化** - 针对微信公众号做了专门优化

## 📦 安装依赖

```bash
# 无需额外依赖，Python 标准库即可运行
```

## 🚀 使用方法

### 1. 命令行使用

```bash
# 基本用法
echo '{"input": "article.md", "output": "article.html"}' | python3 index.py

# 指定主题
echo '{"input": "tech.md", "output": "tech.html", "theme": "dark"}' | python3 index.py

# 带封面和图片
echo '{
  "input": "story.md",
  "output": "story.html",
  "theme": "pink",
  "cover": "https://example.com/cover.jpg",
  "images": ["img1.jpg", "img2.jpg"]
}' | python3 index.py
```

**返回结果：**
```json
{
  "success": true,
  "output_path": "article.html",
  "title": "我的第一篇公众号文章",
  "theme": "优雅简洁",
  "word_count": 1234,
  "error": null
}
```

### 2. 在 OpenClaw 中使用

Agent 会自动读取 `SKILL.md`，你只需用自然语言描述：

```
用户: "帮我把 article.md 排版成微信公众号格式"
      ↓
Agent: 解析意图，调用 MCP skill
      ↓
MCP: 执行 wechat_article()
      ↓
输出: {"success": true, "output_path": "article.html"}
```

## 🎨 主题预览

### 1. Elegant (优雅简洁) - 默认
```
┌─────────────────────────────────────┐
│  🖼️ 封面图                           │
│                                     │
│  📰 文章标题                          │
│  ⏱️ 阅读时长: 约 5 分钟               │
│                                     │
│  正文内容...                          │
│  ✓ 要点 1                            │
│  ✓ 要点 2                            │
│                                     │
│  ─────────────────────              │
│  © 文章标题                          │
└─────────────────────────────────────┘
```

### 2. Dark (暗黑风格)
- 黑色背景，适合技术文章
- 白色文字，高对比度

### 3. Blue (蓝色清新)
- 浅蓝背景
- 蓝色链接，适合资讯类文章

### 4. Pink (粉色可爱)
- 粉色背景
- 粉红链接，适合情感类文章

### 5. Minimal (极简白)
- 纯白背景
- 衬线字体，商务风格

## 📋 主题对比

| 主题 ID | 风格 | 背景色 | 链接色 | 适合场景 |
|---------|------|--------|--------|----------|
| `elegant` | 优雅简洁 ⭐ | 白色 | 灰色 | 日常文章 |
| `dark` | 暗黑风格 | 黑色 | 蓝色 | 技术文章 |
| `blue` | 蓝色清新 | 浅蓝 | 蓝色 | 资讯类 |
| `pink` | 粉色可爱 | 粉色 | 粉色 | 情感类 |
| `minimal` | 极简白 | 白色 | 灰色 | 商务类 |

## 📖 使用场景

### 1. 技术文章
```json
{
  "input": "tutorial.md",
  "output": "tutorial.html",
  "theme": "dark",
  "title": "Python 入门教程"
}
```

### 2. 日常随笔
```json
{
  "input": "diary.md",
  "output": "diary.html",
  "theme": "pink",
  "cover": "cover.jpg"
}
```

### 3. 商务报告
```json
{
  "input": "report.md",
  "output": "report.html",
  "theme": "minimal",
  "title": "2024 年度总结"
}
```

### 4. 带图片的文章
```json
{
  "input": "travel.md",
  "output": "travel.html",
  "theme": "elegant",
  "cover": "https://example.com/cover.jpg",
  "images": [
    "https://example.com/img1.jpg",
    "https://example.com/img2.jpg"
  ]
}
```

## 🔧 Markdown 支持

### 支持的语法

```markdown
# 标题 1
## 标题 2
### 标题 3

**加粗文字**
*斜体文字*
~~删除线~~

> 引用文字

- 无序列表
1. 有序列表

`行内代码`

```python
# 代码块
print("Hello")
```

[链接](https://example.com)

![图片描述](image.jpg)

---
分割线
```

### 微信优化

- ✅ **样式内嵌** - CSS 直接嵌入 HTML，复制即用
- ✅ **图片适配** - 自动限制图片宽度适配微信
- ✅ **代码高亮** - 代码块语法高亮
- ✅ **链接处理** - 外链自动添加下划线
- ✅ **移动端适配** - 响应式设计

## 📊 效果展示

### 原始 Markdown
```markdown
# Python 入门教程

## 安装 Python

首先，你需要**下载并安装** Python。

```bash
pip install python
```

### 常用命令
- `python --version`
- `pip install <package>`
```

### 生成的 HTML
```html
<h1 style="font-size:28px">Python 入门教程</h1>

<h2 style="font-size:24px">安装 Python</h2>

<p>首先，你需要<strong style="font-weight:600">下载并安装</strong> Python。</p>

<pre style="background:#f6f8fa;padding:16px;border-radius:8px">
<code>pip install python</code>
</pre>

<h3 style="font-size:20px">常用命令</h3>

<ul>
<li><code>python --version</code></li>
<li><code>pip install &lt;package&gt;</code></li>
</ul>
```

## 🎯 最佳实践

### 1. 文章结构
```markdown
# 文章标题（自动提取）

## 摘要

## 目录

## 主体内容

### 小节 1

### 小节 2

## 总结

## 参考资料
```

### 2. 图片处理
- 将图片上传到图床获取 URL
- 使用 `![描述](URL)` 插入正文图片
- 通过 `cover` 参数设置封面图

### 3. 代码块
- 使用 ```python, ```js 等标注语言
- 代码会自动高亮显示

## 🛠️ 技术原理

```
┌─────────────────────────────────────────────────────────────────┐
│  Markdown 源文件                                                 │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  MarkdownParser                                                 │
│  - 解析标题 (# ## ###)                                          │
│  - 解析文本格式 (**bold**, *italic*)                            │
│  - 解析代码块 (```code```)                                      │
│  - 解析列表 (- item)                                            │
│  - 解析引用 (> quote)                                           │
│  - 解析链接和图片                                                │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  HTML 转换                                                      │
│  - 生成语义化 HTML 标签                                          │
│  - 应用主题 CSS 样式                                             │
│  - 嵌入微信优化样式                                              │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  输出 HTML 文件                                                  │
│  - 响应式设计                                                    │
│  - 移动端适配                                                    │
│  - 微信友好格式                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🐛 常见问题

### Q: 生成的 HTML 如何导入微信？
A: 复制 HTML 内容，或直接在浏览器打开后全选复制。

### Q: 图片显示不了？
A: 确保图片 URL 可访问，建议使用图床服务。

### Q: 样式丢失？
A: CSS 已内嵌，复制时确保复制完整内容。

### Q: 如何修改字体？
A: 在 `THEMES` 字典中修改 `font_family`。

### Q: 支持数学公式？
A: 当前版本不支持 LaTeX 公式。

### Q: 表格样式？
A: 可在 Markdown 中使用表格，会自动转换为 HTML 表格。

## 📝 License

基于 MIT License。
