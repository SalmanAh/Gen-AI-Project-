"""
Simple test to demonstrate the audio search system
Run this AFTER starting the server with: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test if server is running"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ Server is running!")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("Make sure server is running: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False

def test_upload_text():
    """Test uploading text (simulated audio transcription)"""
    print("\n" + "="*60)
    print("TEST 2: Simulated Audio Upload")
    print("="*60)
    print("Note: This would normally upload an audio file")
    print("For now, we'll just show what the response looks like")
    
    # Example of what you'd get back
    example_response = {
        "success": True,
        "vector_id": 0,
        "transcription": {
            "text": "Machine learning is a subset of artificial intelligence...",
            "chunks": [
                {"timestamp": [0.0, 5.2], "text": "Machine learning is..."}
            ]
        },
        "embedding": {
            "dimension": 768,
            "vector": [0.123, -0.456, 0.789, "..."]
        }
    }
    
    print("\n📝 Example Response:")
    print(json.dumps(example_response, indent=2))
    print("\n✅ This shows the transcription and embedding you'd receive")

def test_stats():
    """Test getting vector store statistics"""
    print("\n" + "="*60)
    print("TEST 3: Vector Store Statistics")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Stats retrieved:")
            print(f"   Total vectors: {stats['total_vectors']}")
            print(f"   Dimension: {stats['dimension']}")
            print(f"   Index path: {stats['index_path']}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🎙️ AUDIO SEARCH SYSTEM - SIMPLE TEST")
    print("="*60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server is not running. Please start it first:")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return
    
    # Test 2: Show example response
    test_upload_text()
    
    # Test 3: Get stats
    test_stats()
    
    print("\n" + "="*60)
    print("✅ TESTS COMPLETE!")
    print("="*60)
    print("\n📚 Next Steps:")
    print("1. Visit http://localhost:8000/docs for interactive API")
    print("2. Upload a real audio file (.wav, .mp3, .m4a)")
    print("3. See the transcription appear instantly")
    print("4. Search through your audio library")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
