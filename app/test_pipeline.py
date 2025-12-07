"""
Test script for the audio search pipeline
"""
import requests
import json
import os
from pathlib import Path

API_URL = "http://localhost:8000"

def test_health_check():
    """Test API health check"""
    print("\n🧪 Test 1: Health Check")
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health check passed")

def test_upload_audio(audio_file):
    """Test audio upload and transcription"""
    print(f"\n🧪 Test 2: Upload Audio - {audio_file}")
    
    if not os.path.exists(audio_file):
        print(f"⚠️ Audio file not found: {audio_file}")
        return None
    
    with open(audio_file, "rb") as f:
        files = {"file": (os.path.basename(audio_file), f, "audio/wav")}
        response = requests.post(f"{API_URL}/upload-audio", files=files)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload successful")
        print(f"Vector ID: {result['vector_id']}")
        print(f"Transcription: {result['transcription']['text'][:200]}...")
        print(f"Embedding dimension: {result['embedding']['dimension']}")
        print(f"Number of chunks: {len(result['transcription']['chunks'])}")
        return result
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

def test_search(query, k=3):
    """Test semantic search"""
    print(f"\n🧪 Test 3: Search - '{query}'")
    
    response = requests.get(f"{API_URL}/search", params={"q": query, "k": k})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Search successful")
        print(f"Query: {result['query']}")
        print(f"Number of results: {result['num_results']}")
        
        for i, match in enumerate(result['results'], 1):
            print(f"\n  Result {i}:")
            print(f"    Similarity: {match['similarity_score']:.4f}")
            print(f"    Text: {match['text'][:150]}...")
            print(f"    Audio: {match['audio_path']}")
        
        return result
    else:
        print(f"❌ Search failed: {response.text}")
        return None

def test_stats():
    """Test vector store statistics"""
    print("\n🧪 Test 4: Vector Store Stats")
    response = requests.get(f"{API_URL}/stats")
    print(f"Status: {response.status_code}")
    print(f"Stats: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Stats retrieved")

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 AUDIO SEARCH PIPELINE TEST SUITE")
    print("=" * 60)
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: Upload test audios
        test_audio_dir = "tests/audio"
        if os.path.exists(test_audio_dir):
            audio_files = list(Path(test_audio_dir).glob("*.wav")) + \
                         list(Path(test_audio_dir).glob("*.mp3"))
            
            for audio_file in audio_files[:3]:  # Test first 3 files
                test_upload_audio(str(audio_file))
        else:
            print(f"\n⚠️ Test audio directory not found: {test_audio_dir}")
            print("Creating sample test with API...")
        
        # Test 3: Search
        test_queries = [
            "machine learning",
            "artificial intelligence",
            "data science"
        ]
        
        for query in test_queries:
            test_search(query, k=3)
        
        # Test 4: Stats
        test_stats()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Make sure the server is running: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
