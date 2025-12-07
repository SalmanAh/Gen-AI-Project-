import torch
from sentence_transformers import SentenceTransformer
import numpy as np

class TextEmbedder:
    def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2", device=None):
        """Initialize sentence embedding model"""
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Loading embedding model: {model_name} on {self.device}")
        
        try:
            self.model = SentenceTransformer(model_name, device=self.device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"✅ Embedding model loaded (dim={self.embedding_dim})")
            
        except Exception as e:
            print(f"⚠️ Failed to load {model_name}, trying fallback...")
            # Fallback to smaller model
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.model = SentenceTransformer(model_name, device=self.device)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"✅ Fallback embedding model loaded: {model_name} (dim={self.embedding_dim})")
    
    def embed(self, text):
        """
        Generate embedding for text
        
        Args:
            text: Input text string or list of strings
            
        Returns:
            numpy array of normalized embeddings
        """
        # Generate embeddings
        embeddings = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        
        return embeddings
    
    def embed_batch(self, texts, batch_size=32):
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            
        Returns:
            numpy array of normalized embeddings
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )
        
        return embeddings
    
    def get_dimension(self):
        """Return embedding dimension"""
        return self.embedding_dim
