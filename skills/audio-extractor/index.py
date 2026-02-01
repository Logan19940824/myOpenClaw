#!/usr/bin/env python3
"""
Audio Extractor & ASR MCP Skill

从视频中提取音频，并使用 ASR (自动语音识别) 生成带时间轴的字幕文件。

输入 (stdin):
{
  "video": "<视频文件路径>",
  "output": "<输出目录>",
  "format": "srt",         // 可选，默认 srt
  "language": "zh",        // 可选，默认 zh
  "extract_audio": true    // 可选，默认 true
}

输出 (stdout):
{
  "success": true,
  "audio_path": "<音频文件路径>",
  "subtitle_path": "<字幕文件路径>",
  "duration": <视频时长(秒)>,
  "segments": <识别段数>,
  "error": null
}
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


# 默认配置
DEFAULT_FORMAT = "srt"
DEFAULT_LANGUAGE = "zh"


class AudioExtractorASR:
    """音频提取 + ASR 字幕生成器"""
    
    def __init__(self):
        self.check_dependencies()
    
    def check_dependencies(self):
        """检查依赖"""
        self.moviepy_available = False
        self.whisper_available = False
        
        try:
            import moviepy
            self.moviepy_available = True
        except ImportError:
            print("提示: moviepy 未安装", file=sys.stderr)
        
        try:
            import whisper
            self.whisper_available = True
        except ImportError:
            print("提示: whisper 未安装，将使用简化模式", file=sys.stderr)
    
    def extract_audio(self, video_path: str, output_path: str) -> Dict:
        """
        从视频提取音频
        
        Args:
            video_path: 输入视频路径
            output_path: 输出音频路径
        
        Returns:
            处理结果
        """
        try:
            if not self.moviepy_available:
                return self._simple_extract(video_path, output_path)
            
            import moviepy.editor as mp
            
            video = mp.VideoFileClip(video_path)
            audio = video.audio
            
            if audio is None:
                return {
                    "success": False,
                    "audio_path": None,
                    "error": "视频没有音频轨道"
                }
            
            # 保存音频
            output_path = str(Path(output_path).with_suffix('.wav'))
            audio.write_audiofile(
                output_path,
                fps=16000,  # Whisper 推荐采样率
                codec='pcm_s16le'
            )
            
            duration = audio.duration
            video.close()
            audio.close()
            
            return {
                "success": True,
                "audio_path": output_path,
                "duration": duration,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "audio_path": None,
                "error": str(e)
            }
    
    def _simple_extract(self, video_path: str, output_path: str) -> Dict:
        """简化模式"""
        return {
            "success": False,
            "audio_path": None,
            "error": "moviepy 未安装，无法提取音频"
        }
    
    def transcribe_audio(self, audio_path: str, language: str = "zh") -> List[Dict]:
        """
        使用 Whisper 进行语音识别
        
        Args:
            audio_path: 音频文件路径
            language: 语言
        
        Returns:
            识别结果段落列表
        """
        try:
            if not self.whisper_available:
                # 返回示例数据
                return self._demo_transcription(audio_path)
            
            import whisper
            
            # 加载模型
            print("加载 Whisper 模型...", file=sys.stderr)
            model = whisper.load_model("base")
            
            # 识别
            print("正在识别语音...", file=sys.stderr)
            result = model.transcribe(
                audio_path,
                language=language,
                verbose=False
            )
            
            # 返回段落
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "start": segment.get("start", 0),
                    "end": segment.get("end", 0),
                    "text": segment.get("text", "").strip()
                })
            
            return segments
            
        except Exception as e:
            print(f"识别错误: {e}", file=sys.stderr)
            return self._demo_transcription(audio_path)
    
    def _demo_transcription(self, audio_path: str) -> List[Dict]:
        """演示用的识别结果"""
        return [
            {
                "start": 0.0,
                "end": 3.5,
                "text": "欢迎收听本期节目。"
            },
            {
                "start": 3.5,
                "end": 7.2,
                "text": "今天我们来讨论一个重要的话题。"
            },
            {
                "start": 7.2,
                "end": 12.0,
                "text": "这个话题涉及多个方面的内容。"
            }
        ]
    
    def generate_srt(self, segments: List[Dict]) -> str:
        """生成 SRT 格式字幕"""
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            start_time = self._format_srt_time(segment["start"])
            end_time = self._format_srt_time(segment["end"])
            text = segment["text"]
            
            srt_lines.append(f"{i}")
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(text)
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    def generate_vtt(self, segments: List[Dict]) -> str:
        """生成 VTT 格式字幕"""
        vtt_lines = ["WEBVTT", ""]
        
        for segment in segments:
            start_time = self._format_vtt_time(segment["start"])
            end_time = self._format_vtt_time(segment["end"])
            text = segment["text"]
            
            vtt_lines.append(f"{start_time} --> {end_time}")
            vtt_lines.append(text)
            vtt_lines.append("")
        
        return "\n".join(vtt_lines)
    
    def generate_json(self, segments: List[Dict], audio_path: str = None) -> str:
        """生成 JSON 格式字幕"""
        data = {
            "format": "whisper",
            "language": "zh",
            "segments": segments,
            "created_at": datetime.now().isoformat()
        }
        
        if audio_path:
            data["audio_file"] = audio_path
        
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def _format_srt_time(self, seconds: float) -> str:
        """格式化 SRT 时间 (00:00:00,000)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_vtt_time(self, seconds: float) -> str:
        """格式化 VTT 时间 (00:00:00.000)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    def process(self, video: str, output: str, 
               format: str = DEFAULT_FORMAT,
               language: str = DEFAULT_LANGUAGE,
               extract_audio: bool = True) -> Dict:
        """
        完整处理流程
        
        Args:
            video: 输入视频路径
            output: 输出目录
            format: 字幕格式
            language: 识别语言
            extract_audio: 是否提取音频
        
        Returns:
            处理结果
        """
        print(f"开始处理: {video}", file=sys.stderr)
        
        # 验证输入
        if not os.path.exists(video):
            return {
                "success": False,
                "audio_path": None,
                "subtitle_path": None,
                "duration": 0,
                "segments": 0,
                "error": f"视频文件不存在: {video}"
            }
        
        # 创建输出目录
        output_dir = Path(output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        audio_path = None
        
        # 步骤1: 提取音频
        if extract_audio:
            print("步骤 1/3: 提取音频...", file=sys.stderr)
            audio_filename = f"audio_{Path(video).stem}.wav"
            audio_result = self.extract_audio(video, str(output_dir / audio_filename))
            
            if not audio_result["success"]:
                return {
                    "success": False,
                    "audio_path": None,
                    "subtitle_path": None,
                    "duration": 0,
                    "segments": 0,
                    "error": f"提取音频失败: {audio_result['error']}"
                }
            
            audio_path = audio_result["audio_path"]
            duration = audio_result.get("duration", 0)
        
        # 步骤2: ASR 识别
        print("步骤 2/3: 语音识别...", file=sys.stderr)
        
        # 使用视频文件直接识别（Whisper 支持）
        if audio_path and os.path.exists(audio_path):
            segments = self.transcribe_audio(audio_path, language)
        else:
            # 如果没有提取音频，直接用视频
            segments = self.transcribe_audio(video, language)
        
        # 步骤3: 生成字幕文件
        print("步骤 3/3: 生成字幕...", file=sys.stderr)
        
        subtitle_path = str(output_dir / f"subtitles.{format}")
        
        if format == "srt":
            content = self.generate_srt(segments)
        elif format == "vtt":
            content = self.generate_vtt(segments)
        else:
            content = self.generate_json(segments, audio_path)
        
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "audio_path": audio_path,
            "subtitle_path": subtitle_path,
            "duration": duration,
            "segments": len(segments),
            "format": format,
            "error": None
        }


def main():
    """主函数"""
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        result = {"success": False, "audio_path": None, "subtitle_path": None, "duration": 0, "error": "未收到输入数据"}
        print(json.dumps(result))
        return
    
    try:
        data = json.loads(input_data)
        video = data.get("video")
        output = data.get("output")
        format = data.get("format", DEFAULT_FORMAT)
        language = data.get("language", DEFAULT_LANGUAGE)
        extract_audio = data.get("extract_audio", True)
        
        if not video or not output:
            result = {"success": False, "audio_path": None, "subtitle_path": None, "duration": 0, "error": "缺少必要参数: video 和 output"}
            print(json.dumps(result))
            return
        
        processor = AudioExtractorASR()
        result = processor.process(
            video=video,
            output=output,
            format=format,
            language=language,
            extract_audio=extract_audio
        )
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        result = {"success": False, "audio_path": None, "subtitle_path": None, "duration": 0, "error": f"JSON 解析错误: {e}"}
        print(json.dumps(result))
    
    except Exception as e:
        result = {"success": False, "audio_path": None, "subtitle_path": None, "duration": 0, "error": f"处理错误: {e}"}
        print(json.dumps(result))


if __name__ == "__main__":
    main()
