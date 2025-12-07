import faiss
import numpy as np
import json
import os
from pathlib import Path

class FAISSVectorStore:
    def __init__(self, dimension=768, index_path="data/faiss.index", metadata_path="data/metadata.json"):
        """
        Initialize FAISS vector store
        
        Args:
            dimension: Embedding dimension
            index_path: Path to save/load FAISS index
            metadata_path: Path to save/load metadata
        """
        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.metadata = {}
        self.next_id = 0
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # Load or create index
        if os.path.exists(index_path):
            print(f"Loading existing FAISS index from {index_path}")
            self.index = faiss.read_index(index_path)
            self._load_metadata()
        else:
            print(f"Creating new FAISS index (dimension={dimension})")
            self.index = faiss.IndexFlatL2(dimension)
            self._save_metadata()
        
        print(f"✅ FAISS index ready (total vectors: {self.index.ntotal})")
    
    def add(self, embedding, text, audio_path, chunks=None):
        """
        Add embedding to index with metadata
        
        Args:
            embedding: numpy array of shape (dimension,)
            text: transcribed text
            audio_path: path to audio file
            chunks: optional list of text chunks with timestamps
            
        Returns:
            ID of added vector
        """
        # Ensure embedding is 2D
        if len(embedding.shape) == 1:
            embedding = embedding.reshape(1, -1)
        
        # Normalize embedding
        faiss.normalize_L2(embedding)
        
        # Add to index
        self.index.add(embedding.astype('float32'))
        
        # Store metadata
        vector_id = self.next_id
        self.metadata[vector_id] = {
            "text": text,
            "audio_path": audio_path,
            "chunks": chunks or []
        }
        self.next_id += 1
        
        # Save to disk
        self._save_index()
        self._save_metadata()
        
        return vector_id
    
    def search(self, query_embedding, k=5):
        """
        Search for similar vectors
        
        Args:
            query_embedding: numpy array of shape (dimension,)
            k: number of results to return
            
        Returns:
            list of dicts with 'id', 'distance', 'text', 'audio_path', 'chunks'
        """
        # Ensure embedding is 2D
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Normalize query
        faiss.normalize_L2(query_embedding)
        
        # Search
        k = min(k, self.index.ntotal)
        if k == 0:
            return []
        
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Format results
        results = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # No result found
                continue
            
            metadata = self.metadata.get(int(idx), {})
            results.append({
                "id": int(idx),
                "distance": float(dist),
                "similarity_score": float(1 / (1 + dist)),  # Convert distance to similarity
                "text": metadata.get("text", ""),
                "audio_path": metadata.get("audio_path", ""),
                "chunks": metadata.get("chunks", [])
            })
        
        return results
    
    def _save_index(self):
        """Save FAISS index to disk"""
        faiss.write_index(self.index, self.index_path)
    
    def _save_metadata(self):
        """Save metadata to disk"""
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                "next_id": self.next_id,
                "metadata": self.metadata
            }, f, indent=2, ensure_ascii=False)
    
    def _load_metadata(self):
        """Load metadata from disk"""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.next_id = data.get("next_id", 0)
                # Convert string keys back to integers
                self.metadata = {int(k): v for k, v in data.get("metadata", {}).items()}
        else:
            self.metadata = {}
            self.next_id = 0
    
    def get_stats(self):
        """Get statistics about the vector store"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_path": self.index_path
        }
