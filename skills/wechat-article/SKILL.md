# WeChat Article Formatter Skill

将 Markdown 文件自动排版成微信公众号推文格式，支持图片插入。

## 功能特点

- 📝 **MD 转微信格式** - 自动转换 Markdown 为微信公众号 HTML
- 🎨 **多种主题** - 多套精美排版主题可选
- 🖼️ **图片插入** - 支持插入图片到文章合适位置
- 📱 **响应式** - 适配手机端阅读
- 🔗 **图床支持** - 支持多种图床配置

## 使用方法

```json
{
  "tool": "wechat_article",
  "input": "<输入 Markdown 文件路径>",
  "output": "<输出 HTML 文件路径>",
  "theme": "<主题>",      // 可选，默认 "elegant"
  "title": "<文章标题>",  // 可选，从 MD 中提取
  "cover": "<封面图>",    // 可选
  "images": [<图片列表>]  // 可选，插入图片
}
```

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| input | string | ✅ | 输入 Markdown 文件路径 |
| output | string | ✅ | 输出 HTML 文件路径 |
| theme | string | ❌ | 排版主题，默认 "elegant" |
| title | string | ❌ | 文章标题，默认从 MD 提取 |
| cover | string | ❌ | 封面图 URL |
| images | array | ❌ | 要插入的图片列表 |

## 主题选择

| 主题 ID | 风格 | 适合场景 |
|---------|------|----------|
| `elegant` | 优雅简洁 ⭐ | 默认，日常文章 |
| `dark` | 暗黑风格 | 技术文章 |
| `blue` | 蓝色清新 | 资讯类 |
| `pink` | 粉色可爱 | 情感类 |
| `minimal` | 极简白 | 商务类 |

## 示例

```json
{
  "input": "article.md",
  "output": "article.html",
  "theme": "elegant",
  "title": "我的第一篇公众号文章"
}
```

## MCP 协议

```json
{
  "name": "wechat_article",
  "description": "将 Markdown 转换为微信公众号格式",
  "parameters": {
    "type": "object",
    "properties": {
      "input": {
        "type": "string",
        "description": "输入 Markdown 文件路径"
      },
      "output": {
        "type": "string",
        "description": "输出 HTML 文件路径"
      },
      "theme": {
        "type": "string",
        "description": "排版主题"
      },
      "title": {
        "type": "string",
        "description": "文章标题"
      },
      "cover": {
        "type": "string",
        "description": "封面图 URL"
      },
      "images": {
        "type": "array",
        "description": "要插入的图片列表"
      }
    },
    "required": ["input", "output"]
  }
}
```

## Markdown 语法支持

- 标题 (# ## ###)
- 加粗 (**text**)
- 斜体 (*text*)
- 删除线 (~~text~~)
- 引用 (> text)
- 列表 (- item, 1. item)
- 代码块 (```code```)
- 行内代码 (`code`)
- 链接 ([text](url))
- 图片 (![](url))
- 分割线 (---)

## 微信特殊格式

- 📦 **样式内嵌** - CSS 直接嵌入 HTML
- 🖼️ **图片适配** - 自动适配微信图片宽度
- 🔗 **链接处理** - 处理外部链接跳转
- 📊 **代码高亮** - 支持代码块语法高亮
