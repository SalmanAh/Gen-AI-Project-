"""
Quick FFmpeg fix script
This will help locate or download FFmpeg
"""
import os
import sys
import subprocess

print("🔍 Searching for FFmpeg...")

# Check if ffmpeg is in PATH
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ FFmpeg found in PATH!")
        print(result.stdout.split('\n')[0])
        sys.exit(0)
except:
    pass

# Check common installation paths
common_paths = [
    r"C:\Program Files\FFmpeg\bin\ffmpeg.exe",
    r"C:\Program Files (x86)\FFmpeg\bin\ffmpeg.exe",
    r"C:\ffmpeg\bin\ffmpeg.exe",
    os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffmpeg.exe"),
]

found_path = None
for path in common_paths:
    if os.path.exists(path):
        found_path = path
        print(f"✅ Found FFmpeg at: {path}")
        break

if found_path:
    # Add to PATH for this session
    bin_dir = os.path.dirname(found_path)
    os.environ['PATH'] = bin_dir + os.pathsep + os.environ['PATH']
    print(f"\n✅ Added to PATH: {bin_dir}")
    print("\n📝 To make this permanent, add this to your System Environment Variables:")
    print(f"   {bin_dir}")
    print("\n🚀 You can now run the server!")
else:
    print("\n❌ FFmpeg not found in common locations")
    print("\n📥 SOLUTION: Download FFmpeg manually:")
    print("   1. Go to: https://www.gyan.dev/ffmpeg/builds/")
    print("   2. Download: ffmpeg-release-essentials.zip")
    print("   3. Extract to C:\\ffmpeg")
    print("   4. Add C:\\ffmpeg\\bin to your PATH")
    print("\n   OR restart your terminal (FFmpeg may already be installed)")
