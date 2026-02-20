from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
import os

def create_shorts_video(output_path, text="AI Shorts Demo", duration=5):
    """
    Creates a simple 9:16 aspect ratio video (720x1280) with a background color and text overlay.
    """
    try:
        # 1. Background (Dark Blue)
        # Size: 720x1280 (Vertical HD for Shorts/Reels)
        bg_clip = ColorClip(size=(720, 1280), color=(10, 25, 50), duration=duration)
        
        # 2. Text Overlay (Title)
        # Note: TextClip might require ImageMagick installed. 
        # Fallback: Simple text if ImageMagick is tricky, but let's try standard approach.
        # If ImageMagick error occurs, user might need to install it.
        # For robustness without ImageMagick, we can skip TextClip or use PIL and ImageClip.
        
        # Using a safer approach: standard TextClip if updated moviepy, or error handling.
        # Ensure compatibility:
        try:
             txt_clip = TextClip(text, fontsize=70, color='white', size=(600, None), method='caption')
             txt_clip = txt_clip.set_position('center').set_duration(duration)
             video = CompositeVideoClip([bg_clip, txt_clip])
        except Exception as e:
             print(f"TextClip Error (ImageMagick missing?): {e}")
             # Fallback: Just return background color video
             video = bg_clip
        
        # 3. Write File
        video.write_videofile(output_path, fps=24, codec="libx264", audio=False)
        return True
        
    except Exception as e:
        print(f"Video Generation Failed: {e}")
        return False

if __name__ == "__main__":
    if not os.path.exists("outputs/videos"):
        os.makedirs("outputs/videos")
    create_shorts_video("outputs/videos/test_shorts.mp4", "Lotte AI Real Estate\nShorts Demo")
