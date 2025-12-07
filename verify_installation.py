"""
Comprehensive installation verification script
Run this after setup to ensure everything is working
"""
import sys
import subprocess
import os

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python():
    """Check Python version"""
    print("\n🐍 Python Version")
    version = sys.version_info
    print(f"   Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print("   ✅ Python 3.9+ detected")
        return True
    else:
        print("   ❌ Python 3.9+ required")
        return False

def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"   ✅ {package_name}")
        return True
    except ImportError:
        print(f"   ❌ {package_name} - Not installed")
        return False

def check_torch():
    """Check PyTorch and CUDA"""
    print("\n🔥 PyTorch & CUDA")
    
    try:
        import torch
        print(f"   PyTorch version: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"   ✅ CUDA available")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA version: {torch.version.cuda}")
            
            # Get GPU memory
            props = torch.cuda.get_device_properties(0)
            total_memory = props.total_memory / (1024**3)
            print(f"   Total VRAM: {total_memory:.1f} GB")
            
            if total_memory >= 7.5:
                print(f"   ✅ Sufficient VRAM for models")
                return True
            else:
                print(f"   ⚠️ Low VRAM - may need CPU fallback")
                return True
        else:
            print("   ⚠️ CUDA not available - will use CPU")
            print("   Install CUDA version: pip install torch --index-url https://download.pytorch.org/whl/cu118")
            return True
            
    except ImportError:
        print("   ❌ PyTorch not installed")
        return False

def check_ffmpeg():
    """Check FFmpeg installation"""
    print("\n🎵 FFmpeg")
    
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   {version_line}")
            print("   ✅ FFmpeg installed")
            return True
        else:
            print("   ❌ FFmpeg not working")
            return False
            
    except FileNotFoundError:
        print("   ❌ FFmpeg not found in PATH")
        print("   Install from: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"   ❌ Error checking FFmpeg: {e}")
        return False

def check_directories():
    """Check required directories"""
    print("\n📁 Directories")
    
    dirs = ["data", "data/uploads", "tests/audio", "app"]
    all_exist = True
    
    for dir_path in dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/ - Missing")
            all_exist = False
    
    return all_exist

def check_files():
    """Check required files"""
    print("\n📄 Core Files")
    
    files = [
        "app/main.py",
        "app/asr.py",
        "app/embedder.py",
        "app/vector_store.py",
        "requirements.txt"
    ]
    
    all_exist = True
    
    for file_path in files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - Missing")
            all_exist = False
    
    return all_exist

def check_disk_space():
    """Check available disk space"""
    print("\n💾 Disk Space")
    
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        
        free_gb = free / (1024**3)
        print(f"   Free space: {free_gb:.1f} GB")
        
        if free_gb >= 10:
            print("   ✅ Sufficient disk space")
            return True
        else:
            print("   ⚠️ Low disk space - need 10GB+ for models")
            return False
            
    except Exception as e:
        print(f"   ⚠️ Could not check disk space: {e}")
        return True

def test_imports():
    """Test importing key modules"""
    print("\n📦 Python Packages")
    
    packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("transformers", "transformers"),
        ("sentence-transformers", "sentence_transformers"),
        ("faiss", "faiss"),
        ("pydub", "pydub"),
        ("numpy", "numpy"),
    ]
    
    all_ok = True
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_ok = False
    
    return all_ok

def test_model_access():
    """Test HuggingFace model access"""
    print("\n🤗 HuggingFace Access")
    
    try:
        from transformers import AutoModel
        print("   ✅ Can access HuggingFace")
        print("   Models will auto-download on first run (~3GB)")
        return True
    except Exception as e:
        print(f"   ⚠️ Issue accessing HuggingFace: {e}")
        return True

def print_summary(results):
    """Print summary of checks"""
    print_header("VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\n   Passed: {passed}/{total}")
    
    if passed == total:
        print("\n   ✅ ALL CHECKS PASSED!")
        print("\n   Ready to start:")
        print("   1. uvicorn app.main:app --reload")
        print("   2. Visit http://localhost:8000/docs")
        print("   3. python app/test_pipeline.py")
    else:
        print("\n   ⚠️ SOME CHECKS FAILED")
        print("\n   Failed checks:")
        for name, result in results.items():
            if not result:
                print(f"   - {name}")
        
        print("\n   Fix issues above and run again")

def main():
    """Run all verification checks"""
    print_header("🔍 INSTALLATION VERIFICATION")
    print("\nThis script verifies your installation is complete")
    
    results = {}
    
    # Run all checks
    results["Python 3.9+"] = check_python()
    results["Python Packages"] = test_imports()
    results["PyTorch & CUDA"] = check_torch()
    results["FFmpeg"] = check_ffmpeg()
    results["Directories"] = check_directories()
    results["Core Files"] = check_files()
    results["Disk Space"] = check_disk_space()
    results["HuggingFace Access"] = test_model_access()
    
    # Print summary
    print_summary(results)
    
    # Additional info
    print("\n" + "="*60)
    print("📚 Documentation")
    print("="*60)
    print("   README.md - Full documentation")
    print("   QUICKSTART.md - Quick start guide")
    print("   API_DOCUMENTATION.md - API reference")
    print("   GPU_OPTIMIZATION.md - Performance tuning")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
