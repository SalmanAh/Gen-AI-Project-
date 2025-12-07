import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import os
import soundfile as sf
import numpy as np
from pydub import AudioSegment
import io

class WhisperASR:
    def __init__(self, model_name="openai/whisper-large-v3-turbo", device="cuda"):
        """Initialize Whisper ASR model with FP16 optimization for 8GB GPU"""
        self.device = device if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        
        print(f"Loading Whisper model: {model_name} on {self.device}")
        
        try:
            # Load model with memory optimization
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_name,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
            self.model.to(self.device)
            
            self.processor = AutoProcessor.from_pretrained(model_name)
            
            # Create pipeline with optimizations
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model,
                tokenizer=self.processor.tokenizer,
                feature_extractor=self.processor.feature_extractor,
                max_new_tokens=128,
                chunk_length_s=30,
                batch_size=16,
                return_timestamps=True,
                torch_dtype=self.torch_dtype,
                device=self.device,
            )
            
            print(f"✅ Whisper model loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Failed to load {model_name}, trying fallback...")
            # Fallback to whisper-large-v3
            model_name = "openai/whisper-large-v3"
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_name,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True
            )
            self.model.to(self.device)
            self.processor = AutoProcessor.from_pretrained(model_name)
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model,
                tokenizer=self.processor.tokenizer,
                feature_extractor=self.processor.feature_extractor,
                max_new_tokens=128,
                chunk_length_s=30,
                batch_size=16,
                return_timestamps=True,
                torch_dtype=self.torch_dtype,
                device=self.device,
            )
            print(f"✅ Fallback model loaded: {model_name}")
    
    def transcribe(self, audio_path):
        """
        Transcribe audio file to text with timestamps
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            dict with 'text' and 'chunks' (segments with timestamps)
        """
        print(f"Transcribing: {audio_path}")
        
        try:
            # Try to load audio - handle MP3 and other formats
            audio_data = None
            sample_rate = None
            
            # First try soundfile (works for WAV, FLAC, OGG)
            try:
                audio_data, sample_rate = sf.read(audio_path)
                print(f"✅ Loaded audio with soundfile: {sample_rate}Hz")
            except Exception as sf_error:
                print(f"⚠️ soundfile failed: {sf_error}")
                
                # Try pydub for MP3 (requires FFmpeg but gives better error)
                try:
                    print("Trying pydub for MP3 conversion...")
                    audio = AudioSegment.from_file(audio_path)
                    
                    # Convert to mono
                    if audio.channels > 1:
                        audio = audio.set_channels(1)
                    
                    # Convert to 16kHz
                    audio = audio.set_frame_rate(16000)
                    
                    # Convert to numpy array
                    samples = np.array(audio.get_array_of_samples())
                    audio_data = samples.astype(np.float32) / 32768.0  # Normalize to [-1, 1]
                    sample_rate = 16000
                    print(f"✅ Loaded audio with pydub: {sample_rate}Hz")
                    
                except Exception as pydub_error:
                    print(f"❌ pydub also failed: {pydub_error}")
                    return {
                        "text": "ERROR: FFmpeg is required to process MP3 files. Please restart your terminal to update PATH, or convert your audio to WAV format.",
                        "chunks": []
                    }
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            # Resample to 16kHz if needed (Whisper expects 16kHz)
            if sample_rate != 16000:
                print(f"Resampling from {sample_rate}Hz to 16000Hz...")
                duration = len(audio_data) / sample_rate
                target_length = int(duration * 16000)
                audio_data = np.interp(
                    np.linspace(0, len(audio_data), target_length),
                    np.arange(len(audio_data)),
                    audio_data
                )
            
            print(f"Audio shape: {audio_data.shape}, dtype: {audio_data.dtype}")
            
            # Pass numpy array directly to pipeline
            result = self.pipe(audio_data.astype(np.float32))
            
            # Extract full text
            full_text = result.get("text", "")
            
            # Extract chunks with timestamps if available
            chunks = []
            if "chunks" in result and result["chunks"]:
                for chunk in result["chunks"]:
                    chunks.append({
                        "timestamp": chunk.get("timestamp", [0.0, 0.0]),
                        "text": chunk.get("text", "")
                    })
            
            print(f"✅ Transcription complete: {len(full_text)} characters")
            
            return {
                "text": full_text,
                "chunks": chunks
            }
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            import traceback
            traceback.print_exc()
            # Return empty result if transcription fails
            return {
                "text": f"Error: Could not transcribe audio - {str(e)}",
                "chunks": []
            }
    
    def clear_cache(self):
        """Clear GPU cache to free memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
