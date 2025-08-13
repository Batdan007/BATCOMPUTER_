"""
REST API interface for the ML Agent
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import json

from .core import MLAgent
from .config import AgentConfig


logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class TextGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for generation")
    model_name: Optional[str] = Field(None, description="Name of the model to use")
    max_length: Optional[int] = Field(100, description="Maximum length of generated text")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    top_p: Optional[float] = Field(0.9, description="Top-p sampling parameter")
    top_k: Optional[int] = Field(50, description="Top-k sampling parameter")


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Text prompt for image generation")
    model_name: Optional[str] = Field(None, description="Name of the model to use")
    width: Optional[int] = Field(512, description="Image width")
    height: Optional[int] = Field(512, description="Image height")
    num_inference_steps: Optional[int] = Field(50, description="Number of inference steps")
    guidance_scale: Optional[float] = Field(7.5, description="Guidance scale")


class TaskRequest(BaseModel):
    task_name: str = Field(..., description="Name of the task to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task parameters")


class TaskResponse(BaseModel):
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Status message")


class StatusResponse(BaseModel):
    agent_name: str = Field(..., description="Name of the ML Agent")
    is_running: bool = Field(..., description="Whether the agent is running")
    uptime: float = Field(..., description="Agent uptime in seconds")
    models: Dict[str, Any] = Field(..., description="Model status information")
    tasks: Dict[str, Any] = Field(..., description="Task queue status")


class MLAgentAPI:
    """FastAPI-based REST API for the ML Agent"""
    
    def __init__(self, agent: MLAgent, config: AgentConfig):
        self.agent = agent
        self.config = config
        self.app = FastAPI(
            title="ML Agent API",
            description="REST API for Machine Learning Agent",
            version="1.0.0"
        )
        
        # Setup CORS
        if config.enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # Setup routes
        self._setup_routes()
        
        logger.info("ML Agent API initialized")
    
    def _setup_routes(self) -> None:
        """Setup API routes"""
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint"""
            return {
                "message": f"Welcome to {self.config.agent_name} API",
                "version": "1.0.0",
                "docs": "/docs"
            }
        
        @self.app.get("/health", response_model=Dict[str, str])
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": time.time()}
        
        @self.app.get("/status", response_model=StatusResponse)
        async def get_status():
            """Get agent status"""
            try:
                status = self.agent.get_status()
                return StatusResponse(**status)
            except Exception as e:
                logger.error(f"Failed to get status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/models", response_model=List[str])
        async def get_available_models():
            """Get list of available models"""
            try:
                return self.agent.get_available_models()
            except Exception as e:
                logger.error(f"Failed to get models: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tasks", response_model=List[str])
        async def get_available_tasks():
            """Get list of available tasks"""
            try:
                return self.agent.get_available_tasks()
            except Exception as e:
                logger.error(f"Failed to get tasks: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/generate/text", response_model=Dict[str, Any])
        async def generate_text(request: TextGenerationRequest):
            """Generate text using specified model"""
            try:
                if not self.agent.is_running:
                    self.agent.start()
                
                # Extract parameters
                params = {
                    'max_length': request.max_length,
                    'temperature': request.temperature,
                    'top_p': request.top_p,
                    'top_k': request.top_k
                }
                
                # Remove None values
                params = {k: v for k, v in params.items() if v is not None}
                
                result = self.agent.generate_text(
                    request.prompt,
                    model_name=request.model_name,
                    **params
                )
                
                return {
                    "success": True,
                    "generated_text": result,
                    "prompt": request.prompt,
                    "model_used": request.model_name or "default",
                    "timestamp": time.time()
                }
                
            except Exception as e:
                logger.error(f"Text generation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/generate/image", response_model=Dict[str, Any])
        async def generate_image(request: ImageGenerationRequest):
            """Generate image using specified model"""
            try:
                if not self.agent.is_running:
                    self.agent.start()
                
                # Extract parameters
                params = {
                    'width': request.width,
                    'height': request.height,
                    'num_inference_steps': request.num_inference_steps,
                    'guidance_scale': request.guidance_scale
                }
                
                # Remove None values
                params = {k: v for k, v in params.items() if v is not None}
                
                result = self.agent.generate_image(
                    request.prompt,
                    model_name=request.model_name,
                    **params
                )
                
                # Save image to temporary file
                timestamp = int(time.time())
                image_path = f"temp/generated_image_{timestamp}.png"
                
                # Ensure temp directory exists
                Path("temp").mkdir(exist_ok=True)
                
                result.save(image_path)
                
                return {
                    "success": True,
                    "image_path": image_path,
                    "prompt": request.prompt,
                    "model_used": request.model_name or "default",
                    "timestamp": timestamp
                }
                
            except Exception as e:
                logger.error(f"Image generation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/tasks", response_model=TaskResponse)
        async def create_task(request: TaskRequest):
            """Create and execute a task"""
            try:
                if not self.agent.is_running:
                    self.agent.start()
                
                task_id = self.agent.execute_task(request.task_name, **request.parameters)
                
                return TaskResponse(
                    task_id=task_id,
                    status="created",
                    message=f"Task {request.task_name} created successfully"
                )
                
            except Exception as e:
                logger.error(f"Task creation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tasks/{task_id}", response_model=Dict[str, Any])
        async def get_task_status(task_id: str):
            """Get status of a specific task"""
            try:
                status = self.agent.get_task_result(task_id)
                if status is None:
                    raise HTTPException(status_code=404, detail="Task not found")
                
                return status
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to get task status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/tasks/{task_id}", response_model=Dict[str, str])
        async def cancel_task(task_id: str):
            """Cancel a running task"""
            try:
                success = self.agent.cancel_task(task_id)
                if success:
                    return {"message": f"Task {task_id} cancelled successfully"}
                else:
                    raise HTTPException(status_code=404, detail="Task not found or not running")
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to cancel task: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/models/{model_name}/load", response_model=Dict[str, str])
        async def load_model(model_name: str):
            """Load a specific model"""
            try:
                self.agent.load_model(model_name)
                return {"message": f"Model {model_name} loaded successfully"}
                
            except Exception as e:
                logger.error(f"Failed to load model {model_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/models/{model_name}/unload", response_model=Dict[str, str])
        async def unload_model(model_name: str):
            """Unload a specific model"""
            try:
                self.agent.unload_model(model_name)
                return {"message": f"Model {model_name} unloaded successfully"}
                
            except Exception as e:
                logger.error(f"Failed to unload model {model_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/models/{model_name}/status", response_model=Dict[str, Any])
        async def get_model_status(model_name: str):
            """Get status of a specific model"""
            try:
                status = self.agent.get_status()
                if model_name in status.get('models', {}):
                    return status['models'][model_name]
                else:
                    raise HTTPException(status_code=404, detail="Model not found")
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Failed to get model status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/files/{filename}")
        async def get_file(filename: str):
            """Get generated files (images, etc.)"""
            file_path = Path("temp") / filename
            if file_path.exists():
                return FileResponse(file_path)
            else:
                raise HTTPException(status_code=404, detail="File not found")
        
        @self.app.post("/shutdown", response_model=Dict[str, str])
        async def shutdown_agent():
            """Shutdown the agent"""
            try:
                self.agent.shutdown()
                return {"message": "Agent shutdown initiated"}
                
            except Exception as e:
                logger.error(f"Failed to shutdown agent: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def run(self, host: str = None, port: int = None, **kwargs) -> None:
        """Run the API server"""
        host = host or self.config.api_host
        port = port or self.config.api_port
        
        logger.info(f"Starting ML Agent API server on {host}:{port}")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            workers=self.config.api_workers,
            **kwargs
        )


def create_api_app(agent: MLAgent, config: AgentConfig) -> FastAPI:
    """Create FastAPI app instance for external use"""
    api = MLAgentAPI(agent, config)
    return api.app


def run_api_server(agent: MLAgent, config: AgentConfig, **kwargs) -> None:
    """Run the API server with the given agent and config"""
    api = MLAgentAPI(agent, config)
    api.run(**kwargs)
