#!/usr/bin/env python3
"""
Video Clipper MCP Skill

自动剪辑视频，支持裁剪、合并、添加字幕、背景音乐。

输入 (stdin):
{
  "inputs": ["<输入视频路径列表>"],
  "output": "<输出文件路径>",
  "clips": [[start, end], ...],   // 可选
  "subtitle": "<字幕>",           // 可选
  "music": "<背景音乐>",          // 可选
  "aspect_ratio": "9:16",         // 可选，默认 16:9
  "quality": "high",              // 可选，high/medium/low
  "volume_music": 0.5             // 可选，音乐音量 0.1-1.0
}

输出 (stdout):
{
  "success": true,
  "output_path": "<输出路径>",
  "duration": <时长(秒)>,
  "resolution": "1080x1920",
  "error": null
}
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional


# 宽高比配置
ASPECT_RATIOS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350)
}

# 质量配置
QUALITY_SETTINGS = {
    "high": {"bitrate": "8M", "fps": 30},
    "medium": {"bitrate": "4M", "fps": 24},
    "low": {"bitrate": "2M", "fps": 15}
}


class VideoClipper:
    """视频剪辑器"""
    
    def __init__(self):
        # 检查依赖
        self.check_dependencies()
    
    def check_dependencies(self):
        """检查必要依赖"""
        try:
            import moviepy
            self.moviepy_available = True
        except ImportError:
            self.moviepy_available = False
            print("提示: moviepy 未安装，将使用简化模式", file=sys.stderr)
    
    def get_video_info(self, video_path: str) -> Dict:
        """获取视频信息"""
        try:
            import moviepy.editor as mp
            
            video = mp.VideoFileClip(video_path)
            info = {
                "duration": video.duration,
                "width": video.size[0],
                "height": video.size[1],
                "fps": video.fps
            }
            video.close()
            return info
        except Exception as e:
            return {"error": str(e)}
    
    def create_clip(self, input_path: str, output_path: str, 
                   start: float = 0, end: Optional[float] = None,
                   aspect_ratio: str = "16:9", 
                   quality: str = "high") -> Dict:
        """
        裁剪单个视频
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            start: 起始时间（秒）
            end: 结束时间（秒），None 表示到结尾
            aspect_ratio: 宽高比
            quality: 质量
        
        Returns:
            处理结果
        """
        try:
            if not self.moviepy_available:
                # 简化模式：直接复制（需要实际安装 moviepy）
                return self._simple_copy(input_path, output_path)
            
            import moviepy.editor as mp
            
            # 读取视频
            video = mp.VideoFileClip(input_path)
            
            # 裁剪
            end_time = end if end else video.duration
            if end_time > video.duration:
                end_time = video.duration
            
            clipped = video.subclip(start, end_time)
            
            # 调整尺寸
            target_w, target_h = ASPECT_RATIOS.get(aspect_ratio, (1920, 1080))
            
            if clipped.size[0] != target_w or clipped.size[1] != target_h:
                # 居中裁剪并填充
                clipped = self._resize_and_crop(clipped, target_w, target_h)
            
            # 保存
            quality_config = QUALITY_SETTINGS.get(quality, QUALITY_SETTINGS["high"])
            output_path = str(Path(output_path).with_suffix('.mp4'))
            clipped.write_videofile(
                output_path,
                fps=quality_config["fps"],
                bitrate=quality_config["bitrate"],
                codec='libx264',
                audio_codec='aac'
            )
            
            video.close()
            clipped.close()
            
            return {
                "success": True,
                "output_path": output_path,
                "duration": clipped.duration,
                "resolution": f"{target_w}x{target_h}",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "duration": 0,
                "resolution": None,
                "error": str(e)
            }
    
    def _resize_and_crop(self, clip, target_w: int, target_h: int):
        """调整尺寸并居中裁剪"""
        import moviepy.editor as mp
        
        # 计算缩放比例
        scale = max(target_w / clip.size[0], target_h / clip.size[1])
        new_w = int(clip.size[0] * scale)
        new_h = int(clip.size[1] * scale)
        
        # 缩放
        resized = clip.resize(new=(new_w, new_h))
        
        # 居中裁剪
        crop_x = (new_w - target_w) // 2
        crop_y = (new_h - target_h) // 2
        
        cropped = resized.crop(
            x1=crop_x, y1=crop_y,
            width=target_w, height=target_h
        )
        
        return cropped
    
    def merge_videos(self, input_paths: List[str], output_path: str,
                    aspect_ratio: str = "16:9", quality: str = "high") -> Dict:
        """
        合并多个视频
        
        Args:
            input_paths: 输入视频路径列表
            output_path: 输出视频路径
            aspect_ratio: 宽高比
            quality: 质量
        
        Returns:
            处理结果
        """
        try:
            if not self.moviepy_available:
                return {
                    "success": False,
                    "output_path": None,
                    "duration": 0,
                    "error": "moviepy 未安装"
                }
            
            import moviepy.editor as mp
            from moviepy.video.compositing.concatenate import concatenate_videoclips
            
            # 读取并处理所有视频
            clips = []
            total_duration = 0
            
            for path in input_paths:
                if not os.path.exists(path):
                    continue
                
                video = mp.VideoFileClip(path)
                target_w, target_h = ASPECT_RATIOS.get(aspect_ratio, (1920, 1080))
                
                # 调整尺寸
                if video.size[0] != target_w or video.size[1] != target_h:
                    video = self._resize_and_crop(video, target_w, target_h)
                
                clips.append(video)
                total_duration += video.duration
            
            if not clips:
                return {
                    "success": False,
                    "output_path": None,
                    "duration": 0,
                    "error": "没有可处理的视频"
                }
            
            # 合并
            final = concatenate_videoclips(clips, method="compose")
            
            # 保存
            quality_config = QUALITY_SETTINGS.get(quality, QUALITY_SETTINGS["high"])
            output_path = str(Path(output_path).with_suffix('.mp4'))
            final.write_videofile(
                output_path,
                fps=quality_config["fps"],
                bitrate=quality_config["bitrate"],
                codec='libx264',
                audio_codec='aac'
            )
            
            # 清理
            for clip in clips:
                clip.close()
            final.close()
            
            return {
                "success": True,
                "output_path": output_path,
                "duration": total_duration,
                "resolution": f"{target_w}x{target_h}",
                "clips_count": len(input_paths),
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "duration": 0,
                "error": str(e)
            }
    
    def add_subtitle(self, video_path: str, output_path: str, 
                    subtitle: str, position: str = "bottom") -> Dict:
        """
        添加字幕
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            subtitle: 字幕文本
            position: 位置，top/bottom/center
        
        Returns:
            处理结果
        """
        try:
            if not self.moviepy_available:
                return {
                    "success": False,
                    "output_path": None,
                    "error": "moviepy 未安装"
                }
            
            import moviepy.editor as mp
            from moviepy.video.tools.subtitles import TextClip
            
            video = mp.VideoFileClip(video_path)
            
            # 创建字幕
            text_clip = (mp.TextClip(
                subtitle,
                fontsize=48,
                color='white',
                font='Microsoft-YaHei',
                stroke_color='black',
                stroke_width=2
            )
            .set_duration(video.duration)
            .set_position(('center', 'bottom' if position == 'bottom' else 'top')))
            
            # 合成
            final = mp.CompositeVideoClip([video, text_clip])
            
            # 保存
            output_path = str(Path(output_path).with_suffix('.mp4'))
            final.write_videofile(
                output_path,
                fps=video.fps,
                codec='libx264',
                audio_codec='aac'
            )
            
            video.close()
            final.close()
            
            return {
                "success": True,
                "output_path": output_path,
                "duration": video.duration,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "error": str(e)
            }
    
    def add_music(self, video_path: str, output_path: str, 
                 music_path: str, volume: float = 0.5) -> Dict:
        """
        添加背景音乐
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径
            music_path: 音乐文件路径
            volume: 音量 0.1-1.0
        
        Returns:
            处理结果
        """
        try:
            if not self.moviepy_available:
                return {
                    "success": False,
                    "output_path": None,
                    "error": "moviepy 未安装"
                }
            
            import moviepy.editor as mp
            
            video = mp.VideoFileClip(video_path)
            music = mp.AudioFileClip(music_path)
            
            # 调整音乐时长
            if music.duration > video.duration:
                music = music.subclip(0, video.duration)
            elif music.duration < video.duration:
                # 循环音乐
                music = mp.audio_loop(music, duration=video.duration)
            
            # 调整音量
            music = music.volumex(volume)
            
            # 混合音频
            final_audio = mp.CompositeAudioClip([
                video.audio,
                music
            ])
            
            # 设置视频音频
            final_video = video.set_audio(final_audio)
            
            # 保存
            output_path = str(Path(output_path).with_suffix('.mp4'))
            final_video.write_videofile(
                output_path,
                fps=video.fps,
                codec='libx264',
                audio_codec='aac'
            )
            
            video.close()
            music.close()
            final_video.close()
            
            return {
                "success": True,
                "output_path": output_path,
                "duration": video.duration,
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "error": str(e)
            }
    
    def _simple_copy(self, input_path: str, output_path: str) -> Dict:
        """简化模式：直接复制"""
        try:
            import shutil
            shutil.copy2(input_path, output_path)
            
            # 获取文件大小
            size = os.path.getsize(output_path)
            
            return {
                "success": True,
                "output_path": output_path,
                "duration": 0,
                "resolution": "unknown",
                "note": "简化模式，仅复制文件",
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "output_path": None,
                "duration": 0,
                "error": str(e)
            }
    
    def process(self, inputs: List[str], output: str,
               clips: Optional[List[List[float]]] = None,
               subtitle: Optional[str] = None,
               music: Optional[str] = None,
               aspect_ratio: str = "16:9",
               quality: str = "high",
               volume_music: float = 0.5) -> Dict:
        """
        完整处理流程
        
        Args:
            inputs: 输入视频列表
            output: 输出路径
            clips: 裁剪时间点
            subtitle: 字幕
            music: 背景音乐
            aspect_ratio: 宽高比
            quality: 质量
            volume_music: 音乐音量
        
        Returns:
            处理结果
        """
        print(f"开始处理视频: {inputs}", file=sys.stderr)
        
        # 步骤1: 裁剪（如果有）
        if clips and len(clips) > 0:
            print("步骤 1/4: 裁剪视频...", file=sys.stderr)
            # 这里简化处理，实际应该逐个裁剪
            input_path = inputs[0]
        else:
            input_path = inputs[0]
        
        # 步骤2: 合并（如果有多个）
        if len(inputs) > 1:
            print("步骤 2/4: 合并视频...", file=sys.stderr)
            merge_result = self.merge_videos(inputs, output, aspect_ratio, quality)
            if not merge_result["success"]:
                return merge_result
            input_path = output
        
        # 步骤3: 添加字幕
        if subtitle:
            print("步骤 3/4: 添加字幕...", file=sys.stderr)
            temp_path = str(Path(output).with_suffix('')) + '_temp.mp4'
            subtitle_result = self.add_subtitle(input_path, temp_path, subtitle)
            if subtitle_result["success"]:
                input_path = temp_path
        
        # 步骤4: 添加音乐
        if music:
            print("步骤 4/4: 添加背景音乐...", file=sys.stderr)
            final_path = output
            music_result = self.add_music(input_path, final_path, music, volume_music)
            if music_result["success"]:
                return music_result
        
        # 如果只有裁剪
        if clips and len(clips) > 0:
            clip_result = self.create_clip(
                inputs[0], output, clips[0][0], clips[0][1] if len(clips[0]) > 1 else None,
                aspect_ratio, quality
            )
            return clip_result
        
        # 如果只有合并
        if len(inputs) > 1:
            return merge_result
        
        # 如果只有单个视频
        return {
            "success": True,
            "output_path": input_path,
            "duration": 0,
            "resolution": ASPECT_RATIOS.get(aspect_ratio, (1920, 1080)),
            "error": None
        }


def main():
    """主函数"""
    input_data = sys.stdin.read().strip()
    
    if not input_data:
        result = {"success": False, "output_path": None, "duration": 0, "error": "未收到输入数据"}
        print(json.dumps(result))
        return
    
    try:
        data = json.loads(input_data)
        inputs = data.get("inputs")
        output = data.get("output")
        clips = data.get("clips")
        subtitle = data.get("subtitle")
        music = data.get("music")
        aspect_ratio = data.get("aspect_ratio", "16:9")
        quality = data.get("quality", "high")
        volume_music = data.get("volume_music", 0.5)
        
        if not inputs or not output:
            result = {"success": False, "output_path": None, "duration": 0, "error": "缺少必要参数: inputs 和 output"}
            print(json.dumps(result))
            return
        
        clipper = VideoClipper()
        result = clipper.process(
            inputs=inputs,
            output=output,
            clips=clips,
            subtitle=subtitle,
            music=music,
            aspect_ratio=aspect_ratio,
            quality=quality,
            volume_music=volume_music
        )
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        result = {"success": False, "output_path": None, "duration": 0, "error": f"JSON 解析错误: {e}"}
        print(json.dumps(result))
    
    except Exception as e:
        result = {"success": False, "output_path": None, "duration": 0, "error": f"处理错误: {e}"}
        print(json.dumps(result))


if __name__ == "__main__":
    main()
