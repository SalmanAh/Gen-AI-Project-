# 🎙️ Zero-Shot Audio → Text → Embeddings → Vector Search System

Complete pipeline for audio transcription and semantic search using state-of-the-art models.

## 🚀 Features

- **Zero-shot ASR**: Whisper Large V3 Turbo (best accuracy)
- **Semantic embeddings**: MPNet (768-dim, top-tier quality)
- **Vector search**: FAISS (fast similarity search)
- **REST API**: FastAPI with async support
- **GPU optimized**: FP16 for 8GB RTX 5060

## 📦 Models Used

1. **ASR**: `openai/whisper-large-v3-turbo` (fallback: whisper-large-v3)
2. **Embeddings**: `sentence-transformers/all-mpnet-base-v2` (fallback: all-MiniLM-L6-v2)

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- CUDA-capable GPU (RTX 5060 8GB)
- FFmpeg (for audio conversion)

### Install FFmpeg
**Windows**: Download from https://ffmpeg.org/download.html
**Linux**: `sudo apt install ffmpeg`
**Mac**: `brew install ffmpeg`

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

For GPU support (CUDA 11.8):
```bash
pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118
```

For FAISS GPU (optional, faster):
```bash
pip uninstall faiss-cpu
pip install faiss-gpu
```

## 🏃 Quick Start

### 1. Start the API Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will:
- Auto-download models on first run (~3GB total)
- Initialize FAISS index
- Start API on http://localhost:8000

### 2. API Documentation
Visit http://localhost:8000/docs for interactive API docs

## 📡 API Endpoints

### Health Check
```bash
curl http://localhost:8000/
```

### Upload Audio
```bash
curl -X POST "http://localhost:8000/upload-audio" \
  -F "file=@your_audio.wav"
```

**Response:**
```json
{
  "success": true,
  "vector_id": 0,
  "transcription": {
    "text": "Full transcription...",
    "chunks": [
      {"timestamp": [0.0, 5.2], "text": "First segment..."}
    ]
  },
  "embedding": {
    "dimension": 768,
    "vector": [0.123, -0.456, ...]
  }
}
```

### Search
```bash
curl "http://localhost:8000/search?q=machine%20learning&k=5"
```

**Response:**
```json
{
  "success": true,
  "query": "machine learning",
  "num_results": 3,
  "results": [
    {
      "id": 0,
      "similarity_score": 0.89,
      "text": "Transcription text...",
      "audio_path": "data/uploads/audio.wav",
      "chunks": [...]
    }
  ]
}
```

### Get Statistics
```bash
curl http://localhost:8000/stats
```

## 🧪 Testing

### Run Test Suite
```bash
python app/test_pipeline.py
```

### Create Test Audio Files
Place test audio files in `tests/audio/`:
```
tests/
└── audio/
    ├── sample1.wav
    ├── sample2.mp3
    └── sample3.m4a
```

## 📁 Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── asr.py            # Whisper ASR module
│   ├── embedder.py       # MPNet embedding module
│   ├── vector_store.py   # FAISS vector store
│   └── test_pipeline.py  # Test suite
├── data/
│   ├── uploads/          # Uploaded audio files
│   ├── faiss.index       # FAISS index (auto-created)
│   └── metadata.json     # Vector metadata (auto-created)
├── tests/
│   └── audio/            # Test audio files
├── requirements.txt
└── README.md
```

## 🔧 Configuration

### Memory Optimization
The system uses FP16 precision to fit in 8GB VRAM:
- Whisper: ~3GB VRAM
- MPNet: ~500MB VRAM
- Total: ~4GB peak usage

### Supported Audio Formats
- WAV (16kHz recommended)
- MP3
- M4A
- FLAC
- OGG

All formats are auto-converted to 16kHz mono WAV.

## 🎯 Usage Examples

### Python Client
```python
import requests

# Upload audio
with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload-audio",
        files={"file": f}
    )
    result = response.json()
    print(f"Transcription: {result['transcription']['text']}")

# Search
response = requests.get(
    "http://localhost:8000/search",
    params={"q": "artificial intelligence", "k": 5}
)
results = response.json()
for match in results['results']:
    print(f"Score: {match['similarity_score']:.3f}")
    print(f"Text: {match['text'][:100]}...")
```

## 🐛 Troubleshooting

### CUDA Out of Memory
- Reduce `batch_size` in `asr.py`
- Use smaller model: `whisper-large-v3` → `whisper-medium`
- Close other GPU applications

### Model Download Issues
Models auto-download from HuggingFace. If blocked:
```bash
export HF_ENDPOINT=https://hf-mirror.com  # China mirror
```

### FFmpeg Not Found
Install FFmpeg and add to PATH, or audio conversion will fail.

## 📊 Performance

- **Transcription**: ~0.1x realtime (10min audio → 1min processing)
- **Embedding**: ~100ms per text
- **Search**: <10ms for 10k vectors

## 🔒 Security Notes

- API has no authentication (add JWT for production)
- File uploads are not validated beyond extension
- Consider rate limiting for production use

## 📝 License

MIT License - Free for commercial and personal use

## 🙏 Credits

- OpenAI Whisper
- Sentence Transformers
- FAISS by Meta AI
- FastAPI
