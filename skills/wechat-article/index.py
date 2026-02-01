#!/usr/bin/env python3
"""
WeChat Article Formatter MCP Skill

将 Markdown 文件自动排版成微信公众号推文格式，支持图片插入。

输入 (stdin):
{
  "input": "<输入 Markdown 文件路径>",
  "output": "<输出 HTML 文件路径>",
  "theme": "<主题>",      // 可选，默认 "elegant"
  "title": "<文章标题>",  // 可选，从 MD 中提取
  "cover": "<封面图>",    // 可选
  "images": [<图片列表>]  // 可选，插入图片
}

输出 (stdout):
{
  "success": true,
  "output_path": "<输出路径>",
  "title": "<文章标题>",
  "theme": "<主题>",
  "word_count": <字数>,
  "error": null
}
"""

import json
import re
import sys
import html
from pathlib import Path
from typing import List, Dict, Optional


# 主题 CSS 样式
THEMES = {
    "elegant": {
        "name": "优雅简洁",
        "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
        "bg_color": "#ffffff",
        "text_color": "#333333",
        "link_color": "#57606a",
        "code_bg": "#f6f8fa",
        "code_color": "#24292e",
        "blockquote_border": "#dfe2e5",
        "header_color": "#1f2328",
        "accent_color": "#0969da",
        "img_max_width": "100%",
        "border_radius": "8px"
    },
    "dark": {
        "name": "暗黑风格",
        "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif",
        "bg_color": "#1a1a1a",
        "text_color": "#e0e0e0",
        "link_color": "#8ab4f8",
        "code_bg": "#2d2d2d",
        "code_color": "#e0e0e0",
        "blockquote_border": "#4a4a4a",
        "header_color": "#ffffff",
        "accent_color": "#58a6ff",
        "img_max_width": "100%",
        "border_radius": "8px"
    },
    "blue": {
        "name": "蓝色清新",
        "font_family": "-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif",
        "bg_color": "#f0f7ff",
        "text_color": "#333333",
        "link_color": "#0366d6",
        "code_bg": "#e6f3ff",
        "code_color": "#24292e",
        "blockquote_border": "#79b8ff",
        "header_color": "#0366d6",
        "accent_color": "#0366d6",
        "img_max_width": "100%",
        "border_radius": "12px"
    },
    "pink": {
        "name": "粉色可爱",
        "font_family": "-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif",
        "bg_color": "#fff5f5",
        "text_color": "#4a4a4a",
        "link_color": "#e91e63",
        "code_bg": "#fce4ec",
        "code_color": "#880e4f",
        "blockquote_border": "#f48fb1",
        "header_color": "#c2185b",
        "accent_color": "#e91e63",
        "img_max_width": "100%",
        "border_radius": "16px"
    },
    "minimal": {
        "name": "极简白",
        "font_family": "Georgia, 'Times New Roman', serif",
        "bg_color": "#ffffff",
        "text_color": "#222222",
        "link_color": "#666666",
        "code_bg": "#f9f9f9",
        "code_color": "#666666",
        "blockquote_border": "#dddddd",
        "header_color": "#000000",
        "accent_color": "#999999",
        "img_max_width": "100%",
        "border_radius": "4px"
    }
}

DEFAULT_THEME = "elegant"


class MarkdownParser:
    """Markdown 解析器"""
    
    def __init__(self):
        self.html_tags = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }
    
    def escape(self, text: str) -> str:
        """HTML 转义"""
        return ''.join(self.html_tags.get(c, c) for c in text)
    
    def parse(self, content: str) -> str:
        """解析 Markdown 为 HTML"""
        lines = content.split('\n')
        html_lines = []
        in_code_block = False
        code_content = []
        in_list = False
        list_items = []
        in_blockquote = False
        blockquote_content = []
        
        for i, line in enumerate(lines):
            line = line.rstrip()
            
            # 代码块
            if line.startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_content = []
                else:
                    in_code_block = False
                    html_lines.append(self._render_code_block('\n'.join(code_content)))
                continue
            
            if in_code_block:
                code_content.append(line)
                continue
            
            # 引用块
            if line.startswith('>'):
                if not in_blockquote:
                    if blockquote_content:
                        html_lines.append(self._render_blockquote('\n'.join(blockquote_content)))
                    blockquote_content = []
                    in_blockquote = True
                blockquote_content.append(line[1:].strip())
                continue
            
            if in_blockquote and line and not line.startswith('>'):
                html_lines.append(self._render_blockquote('\n'.join(blockquote_content)))
                blockquote_content = []
                in_blockquote = False
            
            # 标题
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                text = line[level+1:].strip()
                if 1 <= level <= 6:
                    html_lines.append(self._render_header(level, text))
                    continue
            
            # 分割线
            if line.startswith('---'):
                html_lines.append('<hr/>')
                continue
            
            # 无序列表
            if line.startswith('- ') or line.startswith('* '):
                list_items.append(line[2:].strip())
                in_list = True
                continue
            
            if in_list and line.strip() == '':
                html_lines.append(self._render_list(list_items))
                list_items = []
                in_list = False
                continue
            
            if in_list and not line.startswith(('- ', '* ')):
                html_lines.append(self._render_list(list_items))
                list_items = []
                in_list = False
            
            # 段落
            if line.strip():
                html_lines.append(self._render_paragraph(line))
            elif html_lines and html_lines[-1] not in ['<br/>', '</p>']:
                pass
        
        # 处理残留
        if in_code_block and code_content:
            html_lines.append(self._render_code_block('\n'.join(code_content)))
        if in_blockquote and blockquote_content:
            html_lines.append(self._render_blockquote('\n'.join(blockquote_content)))
        if in_list and list_items:
            html_lines.append(self._render_list(list_items))
        
        return '\n'.join(html_lines)
    
    def _render_header(self, level: int, text: str) -> str:
        """渲染标题"""
        escaped = self.escape(text)
        size = {1: '28px', 2: '24px', 3: '20px', 4: '18px', 5: '16px', 6: '14px'}[level]
        return f'<h{level} style="font-size:{size};margin:24px 0 16px;font-weight:600;color:#1f2328">{escaped}</h{level}>'
    
    def _render_paragraph(self, text: str) -> str:
        """渲染段落"""
        # 处理行内格式
        text = self._format_inline(text)
        return f'<p style="margin:0 0 16px;line-height:1.8;font-size:16px;color:#333">{text}</p>'
    
    def _format_inline(self, text: str) -> str:
        """行内格式化"""
        # 代码
        text = re.sub(r'`([^`]+)`', r'<code style="background:#f6f8fa;padding:2px 6px;border-radius:4px;font-family:monospace;font-size:14px">\1</code>', text)
        
        # 加粗
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong style="font-weight:600">\1</strong>', text)
        
        # 斜体
        text = re.sub(r'\*([^*]+)\*', r'<em style="font-style:italic">\1</em>', text)
        
        # 删除线
        text = re.sub(r'~~([^~]+)~~', r'<del style="text-decoration:line-through;color:#999">\1</del>', text)
        
        # 链接
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" style="color:#57606a;text-decoration:none;border-bottom:1px solid #57606a">\1</a>', text)
        
        # 图片
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" style="max-width:100%;border-radius:8px;margin:16px 0;display:block"/>', text)
        
        return text
    
    def _render_code_block(self, code: str) -> str:
        """渲染代码块"""
        escaped = self.escape(code)
        return f'<pre style="background:#f6f8fa;padding:16px;border-radius:8px;overflow-x:auto;margin:16px 0"><code style="font-family:monospace;font-size:14px;line-height:1.6;color:#24292e">{escaped}</code></pre>'
    
    def _render_list(self, items: List[str]) -> str:
        """渲染列表"""
        html_items = []
        for item in items:
            formatted = self._format_inline(item)
            html_items.append(f'<li style="margin:8px 0;line-height:1.8">{formatted}</li>')
        return f'<ul style="padding-left:24px;margin:16px 0">{chr(10).join(html_items)}</ul>'
    
    def _render_blockquote(self, text: str) -> str:
        """渲染引用"""
        lines = text.split('\n')
        formatted = []
        for line in lines:
            formatted.append(self._format_inline(line))
        content = '<br/>'.join(formatted)
        return f'<blockquote style="border-left:4px solid #dfe2e5;padding-left:16px;margin:16px 0;color:#666">{content}</blockquote>'


class WeChatArticleFormatter:
    """微信公众号文章格式化器"""
    
    def __init__(self):
        self.parser = MarkdownParser()
    
    def extract_title(self, content: str) -> str:
        """从 Markdown 中提取标题"""
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return "未命名文章"
    
    def format_article(self, input_path: str, output_path: str, 
                      theme: str = DEFAULT_THEME, title: Optional[str] = None,
                      cover: Optional[str] = None, images: Optional[List[str]] = None) -> Dict:
        """
        格式化文章
        
        Args:
            input_path: 输入 Markdown 文件路径
            output_path: 输出 HTML 文件路径
            theme: 主题名称
            title: 文章标题
            cover: 封面图 URL
            images: 要插入的图片列表
        
        Returns:
            处理结果
        """
        try:
            # 读取输入文件
            input_file = Path(input_path)
            if not input_file.exists():
                return {
                    "success": False,
                    "output_path": None,
                    "title": None,
                    "word_count": 0,
                    "error": f"文件不存在: {input_path}"
                }
            
            content = input_file.read_text(encoding='utf-8')
            
            # 提取标题
            if not title:
                title = self.extract_title(content)
            
            # 解析 Markdown
            body_html = self.parser.parse(content)
            
            # 获取主题样式
            theme_config = THEMES.get(theme, THEMES[DEFAULT_THEME])
            
            # 生成完整 HTML
            html_content = self._generate_html(
                title=title,
                body=body_html,
                theme=theme_config,
                cover=cover,
                images=images
            )
            
            # 保存输出文件
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(html_content, encoding='utf-8')
            
            # 统计字数
            word_count = len(content)
            
            return {
                "success": True,
                "output_path": str(output_file),
                "title": title,
                "theme": theme_config["name"],
                "word_count": word_count,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "title": None,
                "word_count": 0,
                "error": str(e)
            }
    
    def _generate_html(self, title: str, body: str, theme: Dict, 
                      cover: Optional[str], images: Optional[List[str]]) -> str:
        """生成完整 HTML"""
        
        # 封面图
        cover_html = ""
        if cover:
            cover_html = f'<img src="{cover}" alt="{title}" style="width:100%;max-width:100%;border-radius:{theme["border_radius"]};margin-bottom:24px"/>'
        
        # 图片画廊
        gallery_html = ""
        if images:
            img_htmls = []
            for i, img in enumerate(images):
                img_htmls.append(f'<img src="{img}" alt="图片{i+1}" style="width:100%;max-width:100%;border-radius:{theme["border_radius"]};margin:8px 0;display:block"/>')
            gallery_html = f'<div style="margin:24px 0">{chr(10).join(img_htmls)}</div>'
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=no">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {theme["font_family"]};
            background-color: {theme["bg_color"]};
            color: {theme["text_color"]};
            line-height: 1.8;
            font-size: 16px;
            padding: 16px;
            max-width: 100%;
        }}
        
        .container {{
            max-width: 100%;
            margin: 0 auto;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {theme["header_color"]};
            font-weight: 600;
            margin: 24px 0 16px;
        }}
        
        h1 {{ font-size: 28px; }}
        h2 {{ font-size: 24px; }}
        h3 {{ font-size: 20px; }}
        
        p {{
            margin: 0 0 16px;
            line-height: 1.8;
        }}
        
        a {{
            color: {theme["link_color"]};
            text-decoration: none;
            border-bottom: 1px solid {theme["link_color"]};
        }}
        
        a:hover {{
            opacity: 0.8;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            border-radius: {theme["border_radius"]};
            margin: 16px 0;
            display: block;
        }}
        
        pre {{
            background: {theme["code_bg"]};
            padding: 16px;
            border-radius: {theme["border_radius"]};
            overflow-x: auto;
            margin: 16px 0;
        }}
        
        code {{
            font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
            font-size: 14px;
            color: {theme["code_color"]};
        }}
        
        blockquote {{
            border-left: 4px solid {theme["blockquote_border"]};
            padding-left: 16px;
            margin: 16px 0;
            color: #666;
        }}
        
        ul, ol {{
            padding-left: 24px;
            margin: 16px 0;
        }}
        
        li {{
            margin: 8px 0;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid {theme["blockquote_border"]};
            margin: 24px 0;
        }}
        
        .cover {{
            margin-bottom: 24px;
        }}
        
        .article-title {{
            font-size: 28px;
            font-weight: 700;
            color: {theme["header_color"]};
            margin: 24px 0;
            line-height: 1.4;
        }}
        
        .meta {{
            color: #999;
            font-size: 14px;
            margin-bottom: 24px;
        }}
        
        .gallery {{
            margin: 24px 0;
        }}
        
        .footer {{
            margin-top: 32px;
            padding-top: 16px;
            border-top: 1px dashed #ddd;
            color: #999;
            font-size: 14px;
            text-align: center;
        }}
        
        /* 公众号特定样式 */
        .wx-video {{
            width: 100%;
            max-width: 100%;
            margin: 16px 0;
        }}
        
        .wx-music {{
            background: {theme["code_bg"]};
            padding: 12px;
            border-radius: 8px;
            margin: 16px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        {cover_html}
        
        <h1 class="article-title">{title}</h1>
        
        <div class="meta">
            <span>阅读时长: 约 5 分钟</span>
        </div>
        
        <div class="content">
{body}
        </div>
        
        {gallery_html}
        
        <div class="footer">
            <p>© {title}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html


def main():
    """主函数"""
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        result = {"success": False, "output_path": None, "title": None, "word_count": 0, "error": "未收到输入数据"}
        print(json.dumps(result))
        return
    
    try:
        data = json.loads(input_data)
        input_path = data.get("input")
        output_path = data.get("output")
        theme = data.get("theme", DEFAULT_THEME)
        title = data.get("title")
        cover = data.get("cover")
        images = data.get("images")
        
        if not input_path or not output_path:
            result = {"success": False, "output_path": None, "title": None, "word_count": 0, "error": "缺少必要参数: input 和 output"}
            print(json.dumps(result))
            return
        
        formatter = WeChatArticleFormatter()
        result = formatter.format_article(input_path, output_path, theme, title, cover, images)
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        result = {"success": False, "output_path": None, "title": None, "word_count": 0, "error": f"JSON 解析错误: {e}"}
        print(json.dumps(result))
    
    except Exception as e:
        result = {"success": False, "output_path": None, "title": None, "word_count": 0, "error": f"处理错误: {e}"}
        print(json.dumps(result))


if __name__ == "__main__":
    main()
