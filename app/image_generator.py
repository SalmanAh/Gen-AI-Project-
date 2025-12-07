"""
Sound2Scene Image Generation
Converts audio scene descriptions into visual scenes using Stable Diffusion
"""
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler
from PIL import Image
import os

class Sound2SceneGenerator:
    def __init__(self, model_name="stabilityai/stable-diffusion-xl-base-1.0", device="cuda"):
        """
        Initialize Stable Diffusion XL for high-quality image generation
        
        Args:
            model_name: Hugging Face model ID
            device: cuda or cpu
        """
        self.device = device if torch.cuda.is_available() else "cpu"
        
        print(f"Loading Stable Diffusion XL on {self.device}")
        print("⚠️ This will download ~7GB of models on first run...")
        
        try:
            # Load SDXL with memory optimizations for 8GB GPU
            self.pipe = StableDiffusionXLPipeline.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True,
                variant="fp16" if self.device == "cuda" else None
            )
            
            # Optimize for 8GB GPU
            if self.device == "cuda":
                self.pipe.enable_model_cpu_offload()  # Move models to CPU when not in use
                self.pipe.enable_vae_slicing()  # Process VAE in slices
                self.pipe.enable_vae_tiling()  # Process large images in tiles
            
            self.pipe.to(self.device)
            
            # Use faster scheduler
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )
            
            print(f"✅ Stable Diffusion XL loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load SDXL: {e}")
            print("Trying Stable Diffusion 2.1 as fallback...")
            
            # Fallback to SD 2.1 (smaller, faster)
            from diffusers import StableDiffusionPipeline
            self.pipe = StableDiffusionPipeline.from_pretrained(
                "stabilityai/stable-diffusion-2-1",
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True
            )
            self.pipe.to(self.device)
            print(f"✅ Stable Diffusion 2.1 loaded as fallback")
    
    def generate_scene(
        self,
        prompt,
        negative_prompt=None,
        num_inference_steps=30,
        guidance_scale=7.5,
        width=1024,
        height=1024,
        seed=None
    ):
        """
        Generate image from audio scene description
        
        Args:
            prompt: Scene description from audio analysis
            negative_prompt: What to avoid in the image
            num_inference_steps: Quality vs speed (20-50)
            guidance_scale: How closely to follow prompt (7-12)
            width: Image width (512, 768, 1024)
            height: Image height (512, 768, 1024)
            seed: Random seed for reproducibility
            
        Returns:
            PIL Image
        """
        print(f"🎨 Generating scene: {prompt[:100]}...")
        
        # Default negative prompt for better quality
        if negative_prompt is None:
            negative_prompt = (
                "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
                "watermark, text, signature, cartoon, anime, illustration, "
                "low resolution, pixelated, grainy"
            )
        
        # Set seed for reproducibility
        generator = None
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        
        try:
            # Generate image
            with torch.inference_mode():
                result = self.pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    width=width,
                    height=height,
                    generator=generator
                )
            
            image = result.images[0]
            print(f"✅ Image generated successfully")
            
            return image
            
        except Exception as e:
            print(f"❌ Error generating image: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error image
            error_img = Image.new('RGB', (width, height), color='gray')
            return error_img
    
    def enhance_prompt(self, audio_description):
        """
        Enhance audio scene description for better image generation
        
        Args:
            audio_description: Raw description from audio classifier
            
        Returns:
            Enhanced prompt for Stable Diffusion
        """
        # Extract the main scene from description
        if "Audio contains:" in audio_description:
            scene = audio_description.split("Audio contains:")[1].split("(confidence")[0].strip()
        else:
            scene = audio_description
        
        # Add quality enhancers
        enhanced = f"{scene}, high quality, detailed, photorealistic, 8k, professional photography"
        
        return enhanced
    
    def save_image(self, image, output_path):
        """Save generated image to disk"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path, quality=95)
            print(f"💾 Image saved to: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving image: {e}")
            return False
    
    def clear_cache(self):
        """Clear GPU cache to free memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
