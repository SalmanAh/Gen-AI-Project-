"""
Test the new Audio Scene Analysis system
Upload your bird/nature audio and get proper scene descriptions
"""
import requests
import json
import sys

API_URL = "http://localhost:8000"

print("🎵 Audio Scene Analysis Test")
print("=" * 60)

# Check if server is running
try:
    response = requests.get(f"{API_URL}/")
    print(f"✅ Server is running: {response.json()['message']}")
except:
    print("❌ Server is not running!")
    print("   Start it with: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    sys.exit(1)

# Test with your bird audio
audio_file = "data/uploads/birds-forest-nature-445379.wav"

print(f"\n📤 Uploading audio: {audio_file}")
print("   This will:")
print("   1. Analyze the audio scene (detect birds, nature, etc.)")
print("   2. Generate a description")
print("   3. Create embeddings for search")
print("   4. Store in vector database")

try:
    with open(audio_file, "rb") as f:
        files = {"file": (audio_file, f, "audio/wav")}
        response = requests.post(f"{API_URL}/upload-audio", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS!")
        print("=" * 60)
        print(f"\n📊 Scene Analysis:")
        print(f"   Description: {result['scene_analysis']['description']}")
        print(f"   Best Match: {result['scene_analysis']['best_match']}")
        print(f"   Confidence: {result['scene_analysis']['confidence']:.2%}")
        
        print(f"\n🎯 Top 3 Predictions:")
        for i, pred in enumerate(result['scene_analysis']['top_predictions'], 1):
            print(f"   {i}. {pred['label']} ({pred['score']:.2%})")
        
        print(f"\n💾 Storage:")
        print(f"   Vector ID: {result['vector_id']}")
        print(f"   Embedding Dimension: {result['embedding']['dimension']}")
        
        print("\n" + "=" * 60)
        print("🔍 Now try searching:")
        print(f"   http://localhost:8000/search?q=birds%20chirping")
        print(f"   http://localhost:8000/search?q=nature%20sounds")
        
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        
except FileNotFoundError:
    print(f"\n❌ Audio file not found: {audio_file}")
    print("   Upload an audio file first through the web interface")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "=" * 60)
