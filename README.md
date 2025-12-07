# 🎵→🖼️ Sound2Scene: Audio to Visual Scene Generation

> Transforming environmental sounds into photorealistic visual scenes using Generative AI

**Team:** Salman Ahmed (22I-0743), Haider Bukhari (22I-0980), Hamza Arshad (22I-1126)  
**Institution:** FAST-NUCES Islamabad  
**Course:** Generative AI - Dr. Akhtar Jamil

---

## Overview

Sound2Scene converts non-speech environmental audio into photorealistic images using:
- **CLAP** for zero-shot audio understanding
- **180+ scene categories** for comprehensive classification
- **Stable Diffusion XL** for high-quality image generation

### Pipeline
```
Audio → CLAP Analysis → Scene Description → Stable Diffusion XL → Generated Image
```

---

## Quick Start

### Installation
```bash
git clone https://github.com/SalmanAh/Gen-AI-Project-.git
cd Gen-AI-Project-
pip install -r requirements.txt
```

### Run Server
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Access API
Open: http://localhost:8000/docs

---

## API Usage

### Complete Pipeline: `/sound2scene`
```bash
curl -X POST "http://localhost:8000/sound2scene" \
  -F "file=@audio.wav" \
  -F "num_steps=30" \
  -F "guidance=7.5"
```

**Response:**
```json
{
  "success": true,
  "scene_analysis": {
    "scene": "peaceful forest with birds chirping",
    "confidence": 0.95
  },
  "image_generation": {
    "image_path": "data/generated/audio_scene.png",
    "image_base64": "..."
  }
}
```

---

## Features

- 🎵 Zero-shot audio understanding (no training required)
- 🖼️ Photorealistic 1024×1024 images
- 🚀 30-40 second generation (GPU) / 2-5 min (CPU)
- 🎯 180+ real-world scene categories
- 🔌 REST API with FastAPI
- 💾 Vector search with FAISS

---

## Scene Categories

- **Nature & Animals** (25): Birds, wildlife, ocean
- **Weather** (12): Rain, thunder, wind
- **Urban** (23): Traffic, construction, crowds
- **Indoor** (32): Household, appliances, doors
- **Human Sounds** (28): Conversation, laughter
- **Vehicles** (23): Cars, trains, airplanes
- **Music** (15): Instruments, genres
- **Emergency** (6): Alarms, sirens
- **Food & Cooking** (14): Frying, chopping
- **Sports** (10): Ball games, gym
- **Miscellaneous** (30+): Office, tools, ambient

---

## Tech Stack

- Python 3.14
- PyTorch 2.9.1
- Transformers 4.57.3
- Diffusers 0.35.2
- FastAPI
- FAISS

---

## Project Structure

```
project/
├── app/
│   ├── main.py              # FastAPI server
│   ├── audio_classifier.py  # CLAP audio analysis
│   ├── image_generator.py   # Stable Diffusion XL
│   ├── embedder.py          # Text embeddings
│   └── vector_store.py      # FAISS storage
├── data/
│   ├── uploads/             # Input audio
│   └── generated/           # Output images
├── requirements.txt
├── RESEARCH_PAPER.md
└── GPT_PROMPTS.txt
```

---

## Performance

| Metric | GPU (RTX 5060) | CPU |
|--------|----------------|-----|
| Audio Analysis | 2-3s | 5-10s |
| Image Generation | 25-35s | 2-5 min |
| Memory | 7.8 GB VRAM | 12-16 GB RAM |

---

## Citation

```bibtex
@project{sound2scene2025,
  title={Sound2Scene: Transforming Environmental Sounds into Visual Scenes},
  author={Ahmed, Salman and Bukhari, Haider and Arshad, Hamza},
  institution={FAST-NUCES Islamabad},
  year={2025}
}
```

---

## License

MIT License - See LICENSE file for details

---

## Contact

- Email: i220743@nu.edu.pk
- GitHub: [@SalmanAh](https://github.com/SalmanAh)
