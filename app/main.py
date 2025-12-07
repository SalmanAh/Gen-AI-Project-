from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
import os
import shutil
from pathlib import Path
from pydub import AudioSegment
import tempfile
import io
import base64

from app.asr import WhisperASR
from app.audio_classifier import AudioSceneAnalyzer
from app.embedder import TextEmbedder
from app.vector_store import FAISSVectorStore
from app.image_generator import Sound2SceneGenerator

# Initialize FastAPI
app = FastAPI(
    title="Sound2Scene: Audio to Visual Scene Generation",
    description="Complete pipeline: Audio → Scene Analysis → Image Generation using CLAP + Stable Diffusion XL",
    version="3.0.0"
)

# Global models (loaded on startup)
audio_analyzer = None
embedder = None
vector_store = None
image_generator = None

# Create directories
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global audio_analyzer, embedder, vector_store, image_generator
    
    print("🚀 Initializing Sound2Scene pipeline...")
    
    # Initialize Audio Scene Analyzer (CLAP)
    audio_analyzer = AudioSceneAnalyzer()
    
    # Initialize embedder
    embedder = TextEmbedder()
    
    # Initialize vector store
    vector_store = FAISSVectorStore(dimension=embedder.get_dimension())
    
    # Initialize image generator (Stable Diffusion XL)
    print("\n🎨 Loading image generation model...")
    image_generator = Sound2SceneGenerator()
    
    print("\n✅ Sound2Scene pipeline ready!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "Zero-Shot Audio Search API",
        "endpoints": {
            "upload": "/upload-audio",
            "search": "/search?q=your_query",
            "stats": "/stats"
        }
    }

@app.get("/stats")
async def get_stats():
    """Get vector store statistics"""
    return vector_store.get_stats()

def convert_to_wav(input_path, output_path):
    """Convert audio file to 16kHz WAV format"""
    try:
        # Try with pydub first
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(output_path, format="wav")
        return True
    except Exception as e:
        print(f"Warning: Audio conversion failed: {e}")
        print(f"Attempting to use file directly without conversion...")
        # If conversion fails, just copy the file and try to use it directly
        import shutil
        try:
            shutil.copy(input_path, output_path)
            return True
        except:
            return False

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    Upload audio file, analyze scene, embed, and store in vector DB
    
    Returns:
        - scene_analysis (description + top predictions)
        - embedding vector
        - stored vector ID
    """
    try:
        # Validate file type
        allowed_extensions = [".wav", ".mp3", ".m4a", ".flac", ".ogg"]
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Save uploaded file
        upload_path = f"data/uploads/{file.filename}"
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        audio_path = upload_path
        print(f"Using audio file: {audio_path}")
        
        # Step 1: Analyze audio scene
        print(f"🎵 Analyzing audio scene: {file.filename}")
        scene_analysis = audio_analyzer.analyze_audio(audio_path)
        
        # Step 2: Generate embedding from description
        print(f"🧠 Generating embedding from scene description...")
        embedding = embedder.embed(scene_analysis["description"])
        
        # Step 3: Store in vector DB
        print(f"💾 Storing in vector database...")
        vector_id = vector_store.add(
            embedding=embedding,
            text=scene_analysis["description"],
            audio_path=audio_path,
            chunks=[]  # No chunks for audio classification
        )
        
        return JSONResponse(content={
            "success": True,
            "vector_id": vector_id,
            "scene_analysis": {
                "description": scene_analysis["description"],
                "best_match": scene_analysis["best_match"],
                "confidence": scene_analysis["confidence"],
                "top_predictions": scene_analysis["top_predictions"]
            },
            "embedding": {
                "dimension": len(embedding),
                "vector": embedding.tolist()[:10]  # Return first 10 values as preview
            },
            "audio_path": audio_path
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search(q: str = Query(..., description="Search query text"), k: int = Query(5, description="Number of results")):
    """
    Semantic search for similar audio scenes
    
    Args:
        q: Query text (e.g., "birds chirping", "car crash", "nature sounds")
        k: Number of results to return (default: 5)
        
    Returns:
        List of matching audio scenes with similarity scores
    """
    try:
        if not q or len(q.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Generate query embedding
        print(f"🔍 Searching for: {q}")
        query_embedding = embedder.embed(q)
        
        # Search vector store
        results = vector_store.search(query_embedding, k=k)
        
        return JSONResponse(content={
            "success": True,
            "query": q,
            "num_results": len(results),
            "results": results
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sound2scene")
async def sound2scene(
    file: UploadFile = File(...),
    num_steps: int = Query(30, description="Quality (20-50, higher=better)"),
    guidance: float = Query(7.5, description="Prompt adherence (7-12)"),
    width: int = Query(1024, description="Image width"),
    height: int = Query(1024, description="Image height"),
    seed: int = Query(None, description="Random seed for reproducibility")
):
    """
    🎵→🖼️ Complete Sound2Scene Pipeline
    
    Upload audio → Analyze scene → Generate image
    
    Returns:
        - Scene analysis
        - Generated image (base64)
        - Image path
    """
    try:
        # Validate file type
        allowed_extensions = [".wav", ".mp3", ".m4a", ".flac", ".ogg"]
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Save uploaded file
        upload_path = f"data/uploads/{file.filename}"
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"\n{'='*60}")
        print(f"🎵 SOUND2SCENE PIPELINE: {file.filename}")
        print(f"{'='*60}")
        
        # Step 1: Analyze audio scene
        print(f"\n[1/4] 🎵 Analyzing audio scene...")
        scene_analysis = audio_analyzer.analyze_audio(upload_path)
        scene_prompt = scene_analysis["best_match"]
        confidence = scene_analysis["confidence"]
        
        print(f"✅ Scene detected: {scene_prompt} ({confidence:.1%} confidence)")
        
        # Step 2: Enhance prompt for image generation
        print(f"\n[2/4] ✨ Enhancing prompt for image generation...")
        enhanced_prompt = image_generator.enhance_prompt(scene_prompt)
        print(f"Enhanced: {enhanced_prompt[:100]}...")
        
        # Step 3: Generate image
        print(f"\n[3/4] 🎨 Generating visual scene...")
        print(f"   Steps: {num_steps}, Guidance: {guidance}, Size: {width}x{height}")
        
        generated_image = image_generator.generate_scene(
            prompt=enhanced_prompt,
            num_inference_steps=num_steps,
            guidance_scale=guidance,
            width=width,
            height=height,
            seed=seed
        )
        
        # Step 4: Save image
        print(f"\n[4/4] 💾 Saving generated image...")
        image_filename = f"{Path(file.filename).stem}_scene.png"
        image_path = f"data/generated/{image_filename}"
        os.makedirs("data/generated", exist_ok=True)
        image_generator.save_image(generated_image, image_path)
        
        # Convert image to base64 for response
        import io
        import base64
        buffered = io.BytesIO()
        generated_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Store in vector DB
        print(f"\n[5/5] 💾 Storing in vector database...")
        embedding = embedder.embed(scene_prompt)
        vector_id = vector_store.add(
            embedding=embedding,
            text=scene_prompt,
            audio_path=upload_path,
            chunks=[]
        )
        
        # Clear GPU cache
        image_generator.clear_cache()
        
        print(f"\n{'='*60}")
        print(f"✅ SOUND2SCENE COMPLETE!")
        print(f"{'='*60}\n")
        
        return JSONResponse(content={
            "success": True,
            "audio_file": file.filename,
            "scene_analysis": {
                "description": scene_analysis["description"],
                "scene": scene_prompt,
                "confidence": confidence,
                "top_predictions": scene_analysis["top_predictions"][:5]
            },
            "image_generation": {
                "prompt_used": enhanced_prompt,
                "image_path": image_path,
                "image_base64": img_base64,
                "parameters": {
                    "steps": num_steps,
                    "guidance": guidance,
                    "size": f"{width}x{height}",
                    "seed": seed
                }
            },
            "vector_id": vector_id
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
