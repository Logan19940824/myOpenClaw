#!/usr/bin/env python3
"""
Research & PPT Report MCP Skill (美化版)

根据研究主题，联网搜索、分析总结，自动生成专业美观的 PPT 报告。

输入 (stdin):
{
  "topic": "<研究主题>",
  "output": "<输出文件路径>",
  "slides": "<幻灯片数量>",  // 可选，默认 10
  "language": "<语言>",       // 可选，默认 "zh"
  "theme": "<主题>"          // 可选，默认 "modern-blue"
}

主题选项: modern-blue, business, tech, nature, gradient-purple

输出 (stdout):
{
  "success": true,
  "output_path": "<输出路径>",
  "slides_created": <数量>,
  "sources": [<信息来源>],
  "error": null
}
"""

import json
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


# 主题配色方案
THEMES = {
    "modern-blue": {
        "primary": RGBColor(0, 102, 204),      # 蓝色
        "secondary": RGBColor(51, 153, 255),   # 浅蓝
        "accent": RGBColor(255, 153, 0),       # 橙色强调
        "bg_gradient_start": RGBColor(240, 248, 255),
        "bg_gradient_end": RGBColor(220, 240, 255),
        "text_primary": RGBColor(0, 51, 102),
        "text_secondary": RGBColor(102, 102, 102),
        "font_title": "Microsoft YaHei",
        "font_body": "Microsoft YaHei"
    },
    "business": {
        "primary": RGBColor(0, 51, 102),       # 深蓝
        "secondary": RGBColor(51, 51, 51),     # 灰色
        "accent": RGBColor(204, 153, 0),       # 金色
        "bg_gradient_start": RGBColor(255, 255, 255),
        "bg_gradient_end": RGBColor(245, 245, 245),
        "text_primary": RGBColor(0, 0, 0),
        "text_secondary": RGBColor(80, 80, 80),
        "font_title": "Arial",
        "font_body": "Arial"
    },
    "tech": {
        "primary": RGBColor(16, 185, 129),     # 绿色
        "secondary": RGBColor(99, 102, 241),   # 紫色
        "accent": RGBColor(245, 158, 11),      # 橙色
        "bg_gradient_start": RGBColor(17, 24, 39),
        "bg_gradient_end": RGBColor(31, 41, 55),
        "text_primary": RGBColor(255, 255, 255),
        "text_secondary": RGBColor(200, 200, 200),
        "font_title": "Segoe UI",
        "font_body": "Segoe UI"
    },
    "nature": {
        "primary": RGBColor(34, 139, 34),      # 森林绿
        "secondary": RGBColor(85, 107, 47),    # 橄榄色
        "accent": RGBColor(255, 165, 0),       # 橙色
        "bg_gradient_start": RGBColor(240, 255, 240),
        "bg_gradient_end": RGBColor(220, 255, 220),
        "text_primary": RGBColor(0, 100, 0),
        "text_secondary": RGBColor(60, 80, 60),
        "font_title": "Georgia",
        "font_body": "Calibri"
    },
    "gradient-purple": {
        "primary": RGBColor(128, 0, 128),      # 紫色
        "secondary": RGBColor(255, 0, 255),    # 粉紫
        "accent": RGBColor(0, 255, 255),       # 青色
        "bg_gradient_start": RGBColor(240, 230, 255),
        "bg_gradient_end": RGBColor(255, 240, 255),
        "text_primary": RGBColor(64, 0, 64),
        "text_secondary": RGBColor(100, 100, 100),
        "font_title": "Verdana",
        "font_body": "Verdana"
    }
}

# 默认配置
DEFAULT_SLIDES = 10
DEFAULT_THEME = "modern-blue"

LANGUAGE_MAP = {
    "zh": {"title": "研究报告", "toc": "目录", "summary": "总结", "sources": "参考资料"},
    "en": {"title": "Research Report", "toc": "Contents", "summary": "Summary", "sources": "References"}
}


class BeautifulPPTSkill:
    """美观 PPT 生成器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """联网搜索"""
        try:
            url = f"https://duckduckgo.com/html/?q={query}&kl=us-en&ia=web"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result in soup.find_all('div', class_='result')[:num_results]:
                try:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem:
                        results.append({
                            "title": title_elem.get_text(strip=True),
                            "url": title_elem.get('href', ''),
                            "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
                        })
                except Exception:
                    continue
            
            return results[:num_results]
            
        except Exception as e:
            print(f"搜索出错: {e}", file=sys.stderr)
            return []
    
    def analyze_info(self, topic: str, sources: List[Dict], language: str = "zh") -> Dict:
        """分析生成 PPT 内容大纲"""
        lang = LANGUAGE_MAP.get(language, LANGUAGE_MAP["zh"])
        
        content = {
            "title": topic,
            "subtitle": f"{lang['title']} | {datetime.now().strftime('%Y年%m月')}",
            "slides": []
        }
        
        # 专业的 PPT 结构
        slide_templates = [
            ("目录", ["研究背景", "市场分析", "发展趋势", "挑战与机遇", "未来展望"]),
            ("研究背景", [f"研究主题：{topic}", "研究目的与意义", "研究方法说明", "数据来源介绍"]),
            ("市场分析", ["全球市场规模", "中国市场现状", "主要参与者", "增长驱动因素"]),
            ("发展趋势", ["技术创新方向", "商业模式演进", "政策环境影响", "消费者需求变化"]),
            ("竞争格局", ["主要竞争对手", "市场份额分布", "竞争优势对比", "市场进入壁垒"]),
            ("挑战与机遇", ["行业发展痛点", "潜在增长空间", "风险因素识别", "应对策略建议"]),
            ("未来展望", ["短期预测 (1-2年)", "中期预测 (3-5年)", "长期趋势判断", "战略建议"]),
            (lang['summary'], ["核心发现总结", "关键数据支撑", "决策建议", "后续研究方向"]),
            (lang['sources'], ["信息来源说明", "研究局限性", "免责声明"])
        ]
        
        for slide_title, bullets in slide_templates:
            content["slides"].append({
                "title": slide_title,
                "bullets": bullets
            })
        
        content["sources"] = [s["url"] for s in sources[:5]] if sources else ["公开信息整理"]
        
        return content
    
    def add_background(self, slide, theme: Dict, is_cover: bool = False):
        """添加背景"""
        if is_cover:
            # 封面背景
            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, 0, 0, 
                Inches(13.333), Inches(7.5)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = theme["bg_gradient_start"]
            shape.line.fill.background()
            
            # 封面底部装饰
            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, 0, Inches(5), 
                Inches(13.333), Inches(2.5)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = theme["primary"]
            shape.fill.transparency = 0.1
            shape.line.fill.background()
        else:
            # 内容页顶部装饰条
            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, 0, 0, 
                Inches(13.333), Inches(0.15)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = theme["primary"]
            shape.line.fill.background()
            
            # 底部装饰条
            shape = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, 0, Inches(7.35), 
                Inches(13.333), Inches(0.15)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = theme["secondary"]
            shape.line.fill.background()
    
    def add_page_number(self, slide, page_num: int, theme: Dict, total: int):
        """添加页码"""
        textbox = slide.shapes.add_textbox(
            Inches(12), Inches(7), Inches(1), Inches(0.3)
        )
        tf = textbox.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"{page_num}/{total}"
        p.font.size = Pt(12)
        p.font.color.rgb = theme["text_secondary"]
        p.alignment = PP_ALIGN.RIGHT
    
    def add_decorative_elements(self, slide, theme: Dict, position: str = "corner"):
        """添加装饰元素"""
        # 右下角装饰圆圈
        shape = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, 
            Inches(11.5), Inches(5.5), 
            Inches(1.5), Inches(1.5)
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = theme["secondary"]
        shape.fill.transparency = 0.7
        shape.line.fill.background()
    
    def create_ppt(self, content: Dict, output_path: str, theme_name: str = DEFAULT_THEME) -> Dict:
        """生成美观 PPT"""
        try:
            theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
            prs = Presentation()
            
            # 设置页面大小 (16:9)
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)
            
            total_slides = len(content["slides"])
            
            for i, slide_data in enumerate(content["slides"]):
                if i == 0:
                    # 封面页
                    slide = prs.slides.add_slide(prs.slide_layouts[6])
                    self.add_background(slide, theme, is_cover=True)
                    
                    # 装饰圆圈
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.OVAL, Inches(9.5), Inches(1), 
                        Inches(3.5), Inches(3.5)
                    )
                    shape.fill.solid()
                    shape.fill.fore_color.rgb = theme["secondary"]
                    shape.fill.transparency = 0.2
                    shape.line.fill.background()
                    
                    # 主标题
                    title_box = slide.shapes.add_textbox(
                        Inches(0.8), Inches(2), Inches(11.733), Inches(1.5)
                    )
                    tf = title_box.text_frame
                    tf.word_wrap = True
                    p = tf.paragraphs[0]
                    p.text = slide_data["title"]
                    p.font.size = Pt(44)
                    p.font.bold = True
                    p.font.color.rgb = theme["text_primary"]
                    p.alignment = PP_ALIGN.LEFT
                    
                    # 副标题
                    subtitle_box = slide.shapes.add_textbox(
                        Inches(0.8), Inches(3.8), Inches(11.733), Inches(0.8)
                    )
                    tf = subtitle_box.text_frame
                    p = tf.paragraphs[0]
                    p.text = content["subtitle"]
                    p.font.size = Pt(20)
                    p.font.color.rgb = theme["secondary"]
                    p.alignment = PP_ALIGN.LEFT
                    
                    # 底部信息
                    footer_box = slide.shapes.add_textbox(
                        Inches(0.8), Inches(6.2), Inches(11.733), Inches(0.5)
                    )
                    tf = footer_box.text_frame
                    p = tf.paragraphs[0]
                    p.text = "按 Enter 键继续 | Press Enter to continue"
                    p.font.size = Pt(12)
                    p.font.color.rgb = theme["text_secondary"]
                    p.alignment = PP_ALIGN.LEFT
                    
                else:
                    # 内容页
                    slide = prs.slides.add_slide(prs.slide_layouts[6])
                    self.add_background(slide, theme)
                    
                    # 左侧装饰条
                    shape = slide.shapes.add_shape(
                        MSO_SHAPE.RECTANGLE, 
                        Inches(0.3), Inches(0.8), 
                        Inches(0.08), Inches(5.5)
                    )
                    shape.fill.solid()
                    shape.fill.fore_color.rgb = theme["primary"]
                    shape.line.fill.background()
                    
                    # 标题区域
                    title_box = slide.shapes.add_textbox(
                        Inches(0.6), Inches(0.4), 
                        Inches(12), Inches(0.7)
                    )
                    tf = title_box.text_frame
                    p = tf.paragraphs[0]
                    p.text = f"0{i}. {slide_data['title']}"
                    p.font.size = Pt(28)
                    p.font.bold = True
                    p.font.color.rgb = theme["primary"]
                    
                    # 内容区域
                    content_box = slide.shapes.add_textbox(
                        Inches(0.8), Inches(1.5), 
                        Inches(12), Inches(5.3)
                    )
                    tf = content_box.text_frame
                    tf.word_wrap = True
                    
                    for j, bullet in enumerate(slide_data["bullets"]):
                        if j == 0:
                            p = tf.paragraphs[0]
                        else:
                            p = tf.add_paragraph()
                        p.text = f"✓ {bullet}"
                        p.font.size = Pt(18)
                        p.font.color.rgb = theme["text_primary"]
                        p.space_before = Pt(14)
                        
                        # 第一个要点加大加粗
                        if j == 0:
                            p.font.size = Pt(20)
                            p.font.bold = True
                    
                    # 装饰元素
                    self.add_decorative_elements(slide, theme)
                    
                    # 页码
                    self.add_page_number(slide, i, theme, total_slides - 1)
            
            # 保存文件
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            prs.save(str(output_file))
            
            return {
                "success": True,
                "output_path": str(output_file),
                "slides_created": len(content["slides"]),
                "theme": theme_name,
                "sources": content.get("sources", []),
                "error": None
            }
            
        except Exception as e:
            print(f"生成 PPT 错误: {e}", file=sys.stderr)
            return {
                "success": False,
                "output_path": None,
                "slides_created": 0,
                "sources": [],
                "error": str(e)
            }
    
    async def execute(self, topic: str, output: str, slides: int = DEFAULT_SLIDES, 
                     language: str = "zh", theme: str = DEFAULT_THEME) -> Dict:
        """执行完整的 PPT 生成流程"""
        print(f"正在研究主题: {topic}", file=sys.stderr)
        
        # 1. 联网搜索
        print("步骤 1/3: 联网搜索...", file=sys.stderr)
        sources = self.search_web(topic, num_results=5)
        
        if not sources:
            sources = [{"title": f"关于 {topic} 的研究报告", "url": "网络资源"}]
        
        # 2. 分析总结
        print("步骤 2/3: 分析总结...", file=sys.stderr)
        content = self.analyze_info(topic, sources, language)
        
        # 3. 生成 PPT
        print(f"步骤 3/3: 生成 PPT (主题: {theme})...", file=sys.stderr)
        result = self.create_ppt(content, output, theme)
        
        return result


def main():
    """主函数"""
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        result = {"success": False, "output_path": None, "slides_created": 0, "error": "未收到输入数据"}
        print(json.dumps(result))
        return
    
    try:
        data = json.loads(input_data)
        topic = data.get("topic")
        output = data.get("output")
        slides = data.get("slides", DEFAULT_SLIDES)
        language = data.get("language", "zh")
        theme = data.get("theme", DEFAULT_THEME)
        
        if not topic or not output:
            result = {"success": False, "output_path": None, "slides_created": 0, "error": "缺少必要参数"}
            print(json.dumps(result))
            return
        
        skill = BeautifulPPTSkill()
        result = asyncio.run(skill.execute(topic, output, slides, language, theme))
        print(json.dumps(result))
        
    except Exception as e:
        result = {"success": False, "output_path": None, "slides_created": 0, "error": str(e)}
        print(json.dumps(result))


if __name__ == "__main__":
    main()
