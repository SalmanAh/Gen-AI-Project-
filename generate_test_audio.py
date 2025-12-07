"""
Generate test audio files using text-to-speech
Useful if you don't have test audio files
"""
import os

def generate_test_audio():
    """Generate test audio files using gTTS (Google Text-to-Speech)"""
    try:
        from gtts import gTTS
    except ImportError:
        print("Installing gTTS...")
        os.system("pip install gtts")
        from gtts import gTTS
    
    os.makedirs("tests/audio", exist_ok=True)
    
    test_texts = [
        {
            "filename": "sample1_ml.wav",
            "text": "Machine learning is a subset of artificial intelligence that enables computers to learn from data without being explicitly programmed. Deep learning uses neural networks with multiple layers to process complex patterns."
        },
        {
            "filename": "sample2_climate.wav",
            "text": "Climate change refers to long-term shifts in global temperatures and weather patterns. The main cause is human activities, particularly the burning of fossil fuels which releases greenhouse gases into the atmosphere."
        },
        {
            "filename": "sample3_tech.wav",
            "text": "Technology innovation drives economic growth and improves quality of life. From smartphones to cloud computing, technological advances continue to transform how we work, communicate, and solve problems."
        }
    ]
    
    print("Generating test audio files...")
    
    for item in test_texts:
        filepath = f"tests/audio/{item['filename']}"
        print(f"Creating: {filepath}")
        
        tts = gTTS(text=item['text'], lang='en', slow=False)
        mp3_path = filepath.replace('.wav', '.mp3')
        tts.save(mp3_path)
        
        print(f"✅ Generated: {mp3_path}")
    
    print("\n✅ Test audio files created in tests/audio/")
    print("Note: Files are in MP3 format (will be auto-converted by API)")

if __name__ == "__main__":
    generate_test_audio()
