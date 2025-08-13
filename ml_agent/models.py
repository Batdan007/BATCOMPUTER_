"""
Model management system for the ML Agent
"""

import os
import gc
import time
import logging
from typing import Dict, List, Optional, Any, Union, Type
from pathlib import Path
import torch
import torch.nn as nn
from transformers import (
    AutoModel, AutoTokenizer, AutoModelForCausalLM, 
    AutoModelForSequenceClassification, AutoModelForImageClassification,
    pipeline, Pipeline
)
from diffusers import (
    StableDiffusionPipeline, StableDiffusionImg2ImgPipeline,
    DDIMPipeline, DDPMPipeline
)
import numpy as np
from PIL import Image

from .config import ModelConfig
from .utils import get_device, get_memory_usage, clear_gpu_cache


logger = logging.getLogger(__name__)


class BaseModel:
    """Base class for all models"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.device = None
        self.is_loaded = False
        self.load_time = None
        self.last_used = None
        
    def load(self) -> None:
        """Load the model"""
        raise NotImplementedError
        
    def unload(self) -> None:
        """Unload the model to free memory"""
        if self.model is not None:
            del self.model
        if self.tokenizer is not None:
            del self.tokenizer
        if self.pipeline is not None:
            del self.pipeline
            
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.is_loaded = False
        
        # Clear GPU cache
        clear_gpu_cache()
        gc.collect()
        
    def is_available(self) -> bool:
        """Check if model is available and loaded"""
        return self.is_loaded
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        return get_memory_usage()
        
    def update_usage(self) -> None:
        """Update last usage timestamp"""
        self.last_used = time.time()


class TextModel(BaseModel):
    """Text generation and processing models"""
    
    def load(self) -> None:
        """Load text model"""
        try:
            start_time = time.time()
            
            # Determine device
            self.device = get_device(self.config.device)
            logger.info(f"Loading text model {self.config.name} on {self.device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True
            )
            
            # Load model
            if self.config.precision == "float16":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_path,
                    torch_dtype=torch.float16,
                    device_map=self.device,
                    trust_remote_code=True
                )
            else:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model_path,
                    device_map=self.device,
                    trust_remote_code=True
                )
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device
            )
            
            self.is_loaded = True
            self.load_time = time.time() - start_time
            logger.info(f"Text model {self.config.name} loaded in {self.load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to load text model {self.config.name}: {e}")
            raise
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        if not self.is_loaded:
            self.load()
            
        self.update_usage()
        
        # Set default parameters
        generation_kwargs = {
            'max_length': self.config.max_length or 100,
            'temperature': self.config.temperature,
            'top_p': self.config.top_p,
            'top_k': self.config.top_k,
            'do_sample': True,
            'pad_token_id': self.tokenizer.eos_token_id
        }
        generation_kwargs.update(kwargs)
        
        try:
            outputs = self.pipeline(prompt, **generation_kwargs)
            generated_text = outputs[0]['generated_text']
            
            # Remove the input prompt from output
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
                
            return generated_text
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise


class ImageModel(BaseModel):
    """Image generation and processing models"""
    
    def load(self) -> None:
        """Load image model"""
        try:
            start_time = time.time()
            
            # Determine device
            self.device = get_device(self.config.device)
            logger.info(f"Loading image model {self.config.name} on {self.device}")
            
            # Load pipeline based on model type
            if "stable-diffusion" in self.config.model_path.lower():
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    self.config.model_path,
                    torch_dtype=torch.float16 if self.config.precision == "float16" else torch.float32
                )
            else:
                # Generic image pipeline
                self.pipeline = pipeline(
                    "image-generation",
                    model=self.config.model_path,
                    device=self.device
                )
            
            # Move to device
            self.pipeline = self.pipeline.to(self.device)
            
            # Enable memory optimization
            if self.config.enable_memory_optimization:
                self.pipeline.enable_attention_slicing()
                self.pipeline.enable_vae_slicing()
            
            self.is_loaded = True
            self.load_time = time.time() - start_time
            logger.info(f"Image model {self.config.name} loaded in {self.load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to load image model {self.config.name}: {e}")
            raise
    
    def generate_image(self, prompt: str, **kwargs) -> Image.Image:
        """Generate image from prompt"""
        if not self.is_loaded:
            self.load()
            
        self.update_usage()
        
        # Set default parameters
        generation_kwargs = {
            'num_inference_steps': 50,
            'guidance_scale': 7.5,
            'width': 512,
            'height': 512
        }
        generation_kwargs.update(kwargs)
        
        try:
            image = self.pipeline(prompt, **generation_kwargs).images[0]
            return image
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise


class MultimodalModel(BaseModel):
    """Multimodal models (text + image)"""
    
    def load(self) -> None:
        """Load multimodal model"""
        try:
            start_time = time.time()
            
            # Determine device
            self.device = get_device(self.config.device)
            logger.info(f"Loading multimodal model {self.config.name} on {self.device}")
            
            # Load model and tokenizer
            self.model = AutoModel.from_pretrained(
                self.config.model_path,
                torch_dtype=torch.float16 if self.config.precision == "float16" else torch.float32,
                device_map=self.device,
                trust_remote_code=True
            )
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True
            )
            
            self.is_loaded = True
            self.load_time = time.time() - start_time
            logger.info(f"Multimodal model {self.config.name} loaded in {self.load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to load multimodal model {self.config.name}: {e}")
            raise
    
    def process_multimodal(self, text: str, image: Image.Image, **kwargs) -> str:
        """Process text and image input"""
        if not self.is_loaded:
            self.load()
            
        self.update_usage()
        
        try:
            # This is a generic implementation - specific models may have different APIs
            inputs = self.tokenizer(
                text,
                image,
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            # Process outputs based on model type
            # This is a simplified example
            return "Multimodal processing completed"
            
        except Exception as e:
            logger.error(f"Multimodal processing failed: {e}")
            raise


class ModelManager:
    """Manages loading, caching, and lifecycle of ML models"""
    
    def __init__(self, config: 'AgentConfig'):
        self.config = config
        self.models: Dict[str, BaseModel] = {}
        self.model_cache: Dict[str, BaseModel] = {}
        self.max_cache_size = 5  # Maximum number of models to keep in memory
        
    def get_model(self, model_name: str) -> BaseModel:
        """Get a model by name, loading it if necessary"""
        if model_name not in self.config.models:
            raise ValueError(f"Model {model_name} not found in configuration")
            
        # Check if model is already loaded
        if model_name in self.models:
            return self.models[model_name]
            
        # Check cache
        if model_name in self.model_cache:
            model = self.model_cache.pop(model_name)
            self.models[model_name] = model
            return model
            
        # Load new model
        model_config = self.config.models[model_name]
        model = self._create_model(model_config)
        
        # Manage memory if needed
        if len(self.models) >= self.max_cache_size:
            self._evict_least_used()
            
        self.models[model_name] = model
        return model
    
    def _create_model(self, config: ModelConfig) -> BaseModel:
        """Create appropriate model instance based on type"""
        if config.model_type == "text":
            return TextModel(config)
        elif config.model_type == "image":
            return ImageModel(config)
        elif config.model_type == "multimodal":
            return MultimodalModel(config)
        else:
            raise ValueError(f"Unknown model type: {config.model_type}")
    
    def _evict_least_used(self) -> None:
        """Evict least recently used model from memory"""
        if not self.models:
            return
            
        # Find least recently used model
        lru_model = min(
            self.models.items(),
            key=lambda x: x[1].last_used or 0
        )
        
        model_name, model = lru_model
        
        # Move to cache
        self.model_cache[model_name] = model
        del self.models[model_name]
        
        # Unload from memory
        model.unload()
        logger.info(f"Evicted model {model_name} to cache")
    
    def unload_model(self, model_name: str) -> None:
        """Unload a specific model"""
        if model_name in self.models:
            model = self.models[model_name]
            model.unload()
            del self.models[model_name]
            logger.info(f"Unloaded model {model_name}")
    
    def unload_all(self) -> None:
        """Unload all models"""
        for model_name in list(self.models.keys()):
            self.unload_model(model_name)
        
        # Clear cache
        for model in self.model_cache.values():
            model.unload()
        self.model_cache.clear()
        
        logger.info("All models unloaded")
    
    def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models"""
        return list(self.models.keys())
    
    def get_model_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all models"""
        status = {}
        
        for name, model in self.models.items():
            status[name] = {
                'loaded': model.is_loaded,
                'device': model.device,
                'memory_usage': model.get_memory_usage(),
                'load_time': model.load_time,
                'last_used': model.last_used
            }
            
        return status
    
    def preload_models(self, model_names: List[str]) -> None:
        """Preload specified models"""
        for model_name in model_names:
            if model_name in self.config.models:
                try:
                    self.get_model(model_name)
                    logger.info(f"Preloaded model {model_name}")
                except Exception as e:
                    logger.warning(f"Failed to preload model {model_name}: {e}")
    
    def optimize_memory(self) -> None:
        """Optimize memory usage by unloading unused models"""
        current_time = time.time()
        threshold = 300  # 5 minutes
        
        for model_name in list(self.models.keys()):
            model = self.models[model_name]
            if (model.last_used and 
                current_time - model.last_used > threshold):
                self.unload_model(model_name)
                logger.info(f"Unloaded unused model {model_name}")
