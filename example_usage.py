"""
Example usage of the Audio Search API
"""
import requests
import json
import time

API_URL = "http://localhost:8000"

def example_upload():
    """Example: Upload and transcribe audio"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Upload Audio File")
    print("="*60)
    
    # Replace with your audio file path
    audio_file = "tests/audio/sample.wav"
    
    print(f"Uploading: {audio_file}")
    
    with open(audio_file, "rb") as f:
        response = requests.post(
            f"{API_URL}/upload-audio",
            files={"file": ("sample.wav", f, "audio/wav")}
        )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Success!")
        print(f"Vector ID: {result['vector_id']}")
        print(f"\nTranscription:\n{result['transcription']['text']}")
        print(f"\nEmbedding dimension: {result['embedding']['dimension']}")
        return result
    else:
        print(f"❌ Error: {response.text}")
        return None

def example_search():
    """Example: Search for similar audio"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Semantic Search")
    print("="*60)
    
    queries = [
        "machine learning and artificial intelligence",
        "climate change and global warming",
        "technology and innovation"
    ]
    
    for query in queries:
        print(f"\n🔍 Searching: '{query}'")
        
        response = requests.get(
            f"{API_URL}/search",
            params={"q": query, "k": 3}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Found {result['num_results']} results:")
            
            for i, match in enumerate(result['results'], 1):
                print(f"\n  {i}. Similarity: {match['similarity_score']:.4f}")
                print(f"     Text: {match['text'][:100]}...")
        else:
            print(f"❌ Error: {response.text}")
        
        time.sleep(0.5)

def example_batch_upload():
    """Example: Upload multiple audio files"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Batch Upload")
    print("="*60)
    
    # List of audio files to upload
    audio_files = [
        "tests/audio/sample1.wav",
        "tests/audio/sample2.mp3",
        "tests/audio/sample3.m4a"
    ]
    
    results = []
    for audio_file in audio_files:
        print(f"\nUploading: {audio_file}")
        
        try:
            with open(audio_file, "rb") as f:
                response = requests.post(
                    f"{API_URL}/upload-audio",
                    files={"file": f}
                )
            
            if response.status_code == 200:
                result = response.json()
                results.append(result)
                print(f"✅ Uploaded (ID: {result['vector_id']})")
            else:
                print(f"❌ Failed: {response.text}")
        except FileNotFoundError:
            print(f"⚠️ File not found: {audio_file}")
    
    return results

def example_stats():
    """Example: Get vector store statistics"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Vector Store Statistics")
    print("="*60)
    
    response = requests.get(f"{API_URL}/stats")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"\nTotal vectors: {stats['total_vectors']}")
        print(f"Dimension: {stats['dimension']}")
        print(f"Index path: {stats['index_path']}")
    else:
        print(f"❌ Error: {response.text}")

def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("🎙️ AUDIO SEARCH API - USAGE EXAMPLES")
    print("="*60)
    print("\nMake sure the server is running:")
    print("  uvicorn app.main:app --reload")
    print("\n" + "="*60)
    
    try:
        # Check if server is running
        response = requests.get(f"{API_URL}/")
        if response.status_code != 200:
            print("❌ Server not responding")
            return
        
        print("✅ Server is running\n")
        
        # Run examples
        # example_upload()
        example_search()
        example_stats()
        
        print("\n" + "="*60)
        print("✅ Examples completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server")
        print("Start the server first: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
