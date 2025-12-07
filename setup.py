"""
Setup script for Audio Search System
Installs dependencies and verifies GPU setup
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Success")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ Failed")
        if result.stderr:
            print(result.stderr)
        return False

def check_python_version():
    """Check Python version"""
    print("\n🐍 Checking Python version...")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ required")
        return False
    
    print("✅ Python version OK")
    return True

def check_cuda():
    """Check CUDA availability"""
    print("\n🎮 Checking CUDA...")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA available")
            print(f"   Device: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA Version: {torch.version.cuda}")
            print(f"   Total VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
            return True
        else:
            print("⚠️ CUDA not available - will use CPU (slower)")
            return False
    except ImportError:
        print("⚠️ PyTorch not installed yet")
        return None

def check_ffmpeg():
    """Check FFmpeg installation"""
    print("\n🎵 Checking FFmpeg...")
    
    result = subprocess.run("ffmpeg -version", shell=True, capture_output=True)
    
    if result.returncode == 0:
        print("✅ FFmpeg installed")
        return True
    else:
        print("❌ FFmpeg not found")
        print("\nInstall FFmpeg:")
        print("  Windows: https://ffmpeg.org/download.html")
        print("  Linux: sudo apt install ffmpeg")
        print("  Mac: brew install ffmpeg")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Install base requirements
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing base requirements"
    ):
        return False
    
    # Install PyTorch with CUDA
    print("\n🔥 Installing PyTorch with CUDA support...")
    cuda_cmd = f"{sys.executable} -m pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118"
    
    if not run_command(cuda_cmd, "Installing PyTorch with CUDA"):
        print("⚠️ CUDA installation failed, trying CPU version...")
        run_command(
            f"{sys.executable} -m pip install torch==2.1.2 torchaudio==2.1.2",
            "Installing PyTorch (CPU)"
        )
    
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    dirs = [
        "data",
        "data/uploads",
        "tests/audio"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✅ {dir_path}")
    
    return True

def verify_installation():
    """Verify all components are installed"""
    print("\n" + "="*60)
    print("🔍 VERIFYING INSTALLATION")
    print("="*60)
    
    checks = {
        "Python 3.9+": check_python_version(),
        "FFmpeg": check_ffmpeg(),
        "CUDA": check_cuda(),
    }
    
    print("\n" + "="*60)
    print("📊 INSTALLATION SUMMARY")
    print("="*60)
    
    for component, status in checks.items():
        if status is True:
            print(f"  ✅ {component}")
        elif status is False:
            print(f"  ❌ {component}")
        else:
            print(f"  ⚠️ {component} (not checked)")
    
    all_ok = all(v is not False for v in checks.values())
    
    if all_ok:
        print("\n✅ Installation complete!")
        print("\nNext steps:")
        print("  1. Start server: uvicorn app.main:app --reload")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Run tests: python app/test_pipeline.py")
    else:
        print("\n⚠️ Some components missing - see errors above")
    
    return all_ok

def main():
    """Main setup function"""
    print("="*60)
    print("🚀 AUDIO SEARCH SYSTEM SETUP")
    print("="*60)
    
    # Check prerequisites
    if not check_python_version():
        return
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed")
        return
    
    # Verify installation
    verify_installation()

if __name__ == "__main__":
    main()
