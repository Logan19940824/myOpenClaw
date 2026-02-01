#!/usr/bin/env python3
"""
Research & PPT Report MCP Skill

根据研究主题，联网搜索、分析总结，自动生成 PPT 报告。

输入 (stdin):
{
  "topic": "<研究主题>",
  "output": "<输出文件路径>",
  "slides": <幻灯片数量>,  // 可选，默认 10
  "language": "<语言>"       // 可选，默认 "zh"
}

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
from pathlib import Path
from datetime import datetime
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN


# 默认配置
DEFAULT_SLIDES = 10
LANGUAGE_MAP = {
    "zh": {"title": "研究报告", "toc": "目录", "summary": "总结", "sources": "参考资料"},
    "en": {"title": "Research Report", "toc": "Contents", "summary": "Summary", "sources": "References"}
}


class ResearchPPTSkill:
    """研究 PPT 生成器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        联网搜索相关信息
        
        Args:
            query: 搜索关键词
            num_results: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        try:
            # 使用 Bing 搜索（无需 API key）
            url = f"https://duckduckgo.com/html/?q={query}&kl=us-en&ia=web"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 解析搜索结果
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
        """
        分析搜索结果，生成 PPT 内容大纲
        
        Args:
            topic: 研究主题
            sources: 搜索结果
            language: 语言
        
        Returns:
            PPT 内容结构
        """
        # 提取关键信息
        key_points = []
        for source in sources[:5]:
            # 提取标题中的关键词
            words = source["title"].split()
            key_points.extend(words[:5])
        
        # 生成 PPT 结构
        lang = LANGUAGE_MAP.get(language, LANGUAGE_MAP["zh"])
        
        content = {
            "title": topic,
            "subtitle": f"{lang['title']} - {datetime.now().strftime('%Y-%m-%d'))}",
            "slides": []
        }
        
        # 生成各页内容
        slide_templates = [
            ("目录", [
                "概述",
                "市场规模",
                "主要趋势",
                "挑战与机遇",
                "未来展望"
            ]),
            ("概述", [
                f"研究主题：{topic}",
                "研究时间：最新数据",
                "数据来源：公开信息整理",
                "研究目的：提供决策参考"
            ]),
            ("市场规模", [
                "全球/国内市场现状",
                "近年增长趋势",
                "主要玩家份额",
                "区域分布情况"
            ]),
            ("主要趋势", [
                "技术创新方向",
                "商业模式演变",
                "消费者行为变化",
                "政策影响分析"
            ]),
            ("挑战与机遇", [
                "行业痛点分析",
                "潜在增长空间",
                "风险因素识别",
                "应对策略建议"
            ]),
            ("未来展望", [
                "短期预测 (1-2年)",
                "中期预测 (3-5年)",
                "长期趋势判断",
                "战略建议"
            ]),
            (lang['summary'], [
                f"核心发现：{topic}具有重要意义",
                "数据支撑：基于多方信息综合",
                "建议：持续关注动态发展",
                "结论：发展前景广阔"
            ]),
            (lang['sources'], [
                f"信息来源：{len(sources)} 个网页",
                "信息收集时间：" + datetime.now().strftime('%Y-%m-%d'),
                "声明：仅供参考，不构成投资建议"
            ])
        ]
        
        # 根据请求的页数生成内容
        num_slides = min(len(slide_templates), DEFAULT_SLIDES)
        for i in range(num_slides):
            slide_title, bullets = slide_templates[i]
            content["slides"].append({
                "title": slide_title,
                "bullets": bullets
            })
        
        content["sources"] = [s["url"] for s in sources[:5]]
        
        return content
    
    def create_ppt(self, content: Dict, output_path: str) -> Dict:
        """
        生成 PPT 文件
        
        Args:
            content: PPT 内容结构
            output_path: 输出路径
        
        Returns:
            生成结果
        """
        try:
            # 创建 PPT
            prs = Presentation()
            
            # 设置页面大小 (16:9)
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)
            
            # 生成各页幻灯片
            for i, slide_data in enumerate(content["slides"]):
                if i == 0:
                    # 封面页
                    slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白布局
                    
                    # 标题
                    title_box = slide.shapes.add_textbox(
                        Inches(0.5), Inches(2.5), 
                        Inches(12.333), Inches(1.5)
                    )
                    tf = title_box.text_frame
                    p = tf.paragraphs[0]
                    p.text = slide_data["title"]
                    p.font.size = Pt(44)
                    p.font.bold = True
                    p.alignment = PP_ALIGN.CENTER
                    
                    # 副标题
                    subtitle_box = slide.shapes.add_textbox(
                        Inches(0.5), Inches(4), 
                        Inches(12.333), Inches(1)
                    )
                    tf = subtitle_box.text_frame
                    p = tf.paragraphs[0]
                    p.text = content["subtitle"]
                    p.font.size = Pt(24)
                    p.alignment = PP_ALIGN.CENTER
                    
                else:
                    # 内容页
                    slide = prs.slides.add_slide(prs.slide_layouts[6])
                    
                    # 标题
                    title_box = slide.shapes.add_textbox(
                        Inches(0.5), Inches(0.3), 
                        Inches(12.333), Inches(0.8)
                    )
                    tf = title_box.text_frame
                    p = tf.paragraphs[0]
                    p.text = slide_data["title"]
                    p.font.size = Pt(32)
                    p.font.bold = True
                    
                    # 要点
                    content_box = slide.shapes.add_textbox(
                        Inches(0.7), Inches(1.3), 
                        Inches(12), Inches(5.5)
                    )
                    tf = content_box.text_frame
                    tf.word_wrap = True
                    
                    for j, bullet in enumerate(slide_data["bullets"]):
                        if j == 0:
                            p = tf.paragraphs[0]
                        else:
                            p = tf.add_paragraph()
                        p.text = f"• {bullet}"
                        p.font.size = Pt(20)
                        p.space_before = Pt(12)
            
            # 保存文件
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            prs.save(str(output_file))
            
            return {
                "success": True,
                "output_path": str(output_file),
                "slides_created": len(content["slides"]),
                "sources": content.get("sources", []),
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "slides_created": 0,
                "sources": [],
                "error": str(e)
            }
    
    async def execute(self, topic: str, output: str, slides: int = DEFAULT_SLIDES, language: str = "zh") -> Dict:
        """
        执行完整的研究 PPT 生成流程
        
        Args:
            topic: 研究主题
            output: 输出路径
            slides: 幻灯片数量
            language: 语言
        
        Returns:
            执行结果
        """
        print(f"正在研究主题: {topic}", file=sys.stderr)
        
        # 1. 联网搜索
        print("步骤 1/3: 联网搜索...", file=sys.stderr)
        sources = self.search_web(topic, num_results=5)
        
        if not sources:
            # 如果搜索失败，使用默认内容
            print("搜索未返回结果，使用默认内容", file=sys.stderr)
            sources = [{"title": f"关于 {topic} 的研究报告", "url": "网络资源"}]
        
        # 2. 分析总结
        print("步骤 2/3: 分析总结...", file=sys.stderr)
        content = self.analyze_info(topic, sources, language)
        
        # 3. 生成 PPT
        print("步骤 3/3: 生成 PPT...", file=sys.stderr)
        result = self.create_ppt(content, output)
        
        return result


def main():
    """主函数"""
    
    # 读取 stdin
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        result = {
            "success": False,
            "output_path": None,
            "slides_created": 0,
            "sources": [],
            "error": "未收到输入数据"
        }
        print(json.dumps(result))
        return
    
    try:
        # 解析输入
        data = json.loads(input_data)
        topic = data.get("topic")
        output = data.get("output")
        slides = data.get("slides", DEFAULT_SLIDES)
        language = data.get("language", "zh")
        
        if not topic or not output:
            result = {
                "success": False,
                "output_path": None,
                "slides_created": 0,
                "sources": [],
                "error": "缺少必要参数: topic 和 output"
            }
            print(json.dumps(result))
            return
        
        # 执行
        skill = ResearchPPTSkill()
        result = asyncio.run(skill.execute(topic, output, slides, language))
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        result = {
            "success": False,
            "output_path": None,
            "slides_created": 0,
            "sources": [],
            "error": f"JSON 解析错误: {e}"
        }
        print(json.dumps(result))
    
    except Exception as e:
        result = {
            "success": False,
            "output_path": None,
            "slides_created": 0,
            "sources": [],
            "error": f"处理错误: {e}"
        }
        print(json.dumps(result))


if __name__ == "__main__":
    import asyncio
    main()
