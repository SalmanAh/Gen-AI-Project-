"""
Monitor GPU usage and API performance
"""
import time
import requests
import psutil
import json

try:
    import GPUtil
except ImportError:
    print("Installing GPUtil...")
    import os
    os.system("pip install gputil")
    import GPUtil

API_URL = "http://localhost:8000"

def get_gpu_stats():
    """Get GPU memory and utilization"""
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            return {
                "name": gpu.name,
                "memory_used_mb": gpu.memoryUsed,
                "memory_total_mb": gpu.memoryTotal,
                "memory_percent": (gpu.memoryUsed / gpu.memoryTotal) * 100,
                "gpu_utilization": gpu.load * 100
            }
    except:
        pass
    return None

def get_cpu_memory():
    """Get CPU and RAM usage"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_used_gb": psutil.virtual_memory().used / (1024**3),
        "ram_total_gb": psutil.virtual_memory().total / (1024**3),
        "ram_percent": psutil.virtual_memory().percent
    }

def test_upload_performance(audio_file):
    """Test upload and transcription performance"""
    print(f"\n{'='*60}")
    print(f"Testing: {audio_file}")
    print(f"{'='*60}")
    
    # Get initial stats
    print("\n📊 Initial System Stats:")
    gpu_before = get_gpu_stats()
    if gpu_before:
        print(f"  GPU: {gpu_before['name']}")
        print(f"  VRAM: {gpu_before['memory_used_mb']:.0f}MB / {gpu_before['memory_total_mb']:.0f}MB ({gpu_before['memory_percent']:.1f}%)")
    
    cpu_before = get_cpu_memory()
    print(f"  RAM: {cpu_before['ram_used_gb']:.1f}GB / {cpu_before['ram_total_gb']:.1f}GB ({cpu_before['ram_percent']:.1f}%)")
    
    # Upload and time
    print("\n⏱️ Uploading and transcribing...")
    start_time = time.time()
    
    try:
        with open(audio_file, "rb") as f:
            response = requests.post(
                f"{API_URL}/upload-audio",
                files={"file": f}
            )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Success!")
            print(f"  Time: {elapsed:.2f}s")
            print(f"  Transcription length: {len(result['transcription']['text'])} chars")
            print(f"  Chunks: {len(result['transcription']['chunks'])}")
            
            # Get stats after
            time.sleep(1)
            gpu_after = get_gpu_stats()
            if gpu_after:
                print(f"\n📊 Peak VRAM Usage:")
                print(f"  {gpu_after['memory_used_mb']:.0f}MB ({gpu_after['memory_percent']:.1f}%)")
            
            return elapsed
        else:
            print(f"❌ Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_search_performance(query, k=5):
    """Test search performance"""
    print(f"\n🔍 Searching: '{query}'")
    
    start_time = time.time()
    response = requests.get(f"{API_URL}/search", params={"q": query, "k": k})
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        print(f"  Time: {elapsed*1000:.1f}ms")
        print(f"  Results: {result['num_results']}")
        return elapsed
    else:
        print(f"  ❌ Error: {response.text}")
        return None

def monitor_continuous():
    """Continuously monitor system stats"""
    print("\n📊 Continuous Monitoring (Ctrl+C to stop)")
    print(f"{'Time':<12} {'CPU%':<8} {'RAM%':<8} {'VRAM MB':<12} {'GPU%':<8}")
    print("-" * 60)
    
    try:
        while True:
            cpu = get_cpu_memory()
            gpu = get_gpu_stats()
            
            timestamp = time.strftime("%H:%M:%S")
            cpu_pct = f"{cpu['cpu_percent']:.1f}%"
            ram_pct = f"{cpu['ram_percent']:.1f}%"
            
            if gpu:
                vram = f"{gpu['memory_used_mb']:.0f}MB"
                gpu_pct = f"{gpu['gpu_utilization']:.1f}%"
            else:
                vram = "N/A"
                gpu_pct = "N/A"
            
            print(f"{timestamp:<12} {cpu_pct:<8} {ram_pct:<8} {vram:<12} {gpu_pct:<8}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")

def main():
    """Run performance tests"""
    print("\n" + "="*60)
    print("🎯 PERFORMANCE MONITORING")
    print("="*60)
    
    # Check server
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code != 200:
            print("❌ Server not responding")
            return
    except:
        print("❌ Cannot connect to server")
        print("Start server: uvicorn app.main:app --reload")
        return
    
    print("✅ Server is running")
    
    # Test search performance
    print("\n" + "="*60)
    print("SEARCH PERFORMANCE TEST")
    print("="*60)
    
    queries = [
        "machine learning",
        "artificial intelligence",
        "data science"
    ]
    
    search_times = []
    for query in queries:
        elapsed = test_search_performance(query, k=5)
        if elapsed:
            search_times.append(elapsed)
    
    if search_times:
        avg_search = sum(search_times) / len(search_times)
        print(f"\n📊 Average search time: {avg_search*1000:.1f}ms")
    
    # Get stats
    print("\n" + "="*60)
    print("VECTOR STORE STATS")
    print("="*60)
    
    response = requests.get(f"{API_URL}/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"  Total vectors: {stats['total_vectors']}")
        print(f"  Dimension: {stats['dimension']}")
    
    print("\n" + "="*60)
    print("✅ Performance tests completed")
    print("="*60)

if __name__ == "__main__":
    main()
