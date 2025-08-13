# 🤖 Machine Learning Agent

A comprehensive, production-ready Machine Learning Agent system that provides intelligent model management, task orchestration, and API interfaces for various ML workloads.

## ✨ Features

- **🧠 Smart Model Management**: Automatic loading, caching, and memory optimization
- **🎯 Task Orchestration**: Queue-based task execution with progress tracking
- **🌐 REST API**: FastAPI-based interface for easy integration
- **⚡ Performance**: GPU/CPU optimization and efficient resource management
- **🔧 Configurable**: YAML/JSON configuration with sensible defaults
- **📊 Monitoring**: Real-time status and performance metrics
- **🔄 Async Support**: Non-blocking task execution
- **🛡️ Robust**: Error handling, retries, and graceful shutdown

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
```bash
git clone <your-repo>
cd ml_agent
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the agent**:
```bash
# Interactive mode
python -m ml_agent --interactive

# API server mode
python -m ml_agent --api

# Execute specific task
python -m ml_agent --task text_generation --prompt "Hello, world!"
```

### Basic Usage

```python
from ml_agent import MLAgent, load_default_config

# Create agent with default configuration
config = load_default_config()
agent = MLAgent(config)

# Start the agent
agent.start()

# Generate text
text = agent.generate_text("Write a short story about a robot")
print(text)

# Generate image
image = agent.generate_image("A beautiful sunset over mountains")
image.save("sunset.png")

# Shutdown
agent.shutdown()
```

## 📋 Configuration

The ML Agent is highly configurable. Create a `config.yaml` file:

```yaml
agent_name: "MyMLAgent"
log_level: "INFO"

# Model configurations
models:
  gpt2:
    name: "GPT-2"
    model_type: "text"
    model_path: "gpt2"
    device: "auto"
    precision: "float16"
    temperature: 0.7

# Task configurations
tasks:
  text_generation:
    name: "Text Generation"
    task_type: "text_generation"
    model_name: "gpt2"
    timeout: 60
```

See `example_config.yaml` for a complete configuration example.

## 🔌 API Interface

The ML Agent provides a comprehensive REST API:

### Start API Server
```bash
python -m ml_agent --api --config config.yaml
```

### API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /status` - Agent status
- `GET /models` - Available models
- `GET /tasks` - Available tasks
- `POST /generate/text` - Text generation
- `POST /generate/image` - Image generation
- `POST /tasks` - Create task
- `GET /tasks/{task_id}` - Task status
- `DELETE /tasks/{task_id}` - Cancel task

### Example API Usage

```bash
# Generate text
curl -X POST "http://localhost:8000/generate/text" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Hello, world!", "temperature": 0.8}'

# Generate image
curl -X POST "http://localhost:8000/generate/image" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "A beautiful landscape", "width": 512, "height": 512}'
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ML Agent     │    │  Model Manager  │    │ Task Orchestrator│
│   (Core)       │◄──►│                 │◄──►│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   REST API      │    │   Models        │    │   Tasks         │
│   (FastAPI)     │    │   (Text/Image/  │    │   (Generation/  │
│                 │    │    Multimodal)  │    │    Processing)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🧩 Components

### Core Agent (`ml_agent.core`)
- Main orchestration logic
- Lifecycle management
- Background task management

### Model Manager (`ml_agent.models`)
- Model loading and caching
- Memory optimization
- Device management (CPU/GPU/MPS)

### Task Orchestrator (`ml_agent.tasks`)
- Task queue management
- Execution scheduling
- Progress tracking

### Configuration (`ml_agent.config`)
- YAML/JSON configuration
- Validation and defaults
- Environment-specific settings

### Utilities (`ml_agent.utils`)
- Device detection
- Memory monitoring
- System information

### API Interface (`ml_agent.api`)
- FastAPI application
- REST endpoints
- Request/response models

## 🔧 Supported Models

### Text Models
- GPT-2, GPT-Neo, GPT-J
- BERT, RoBERTa
- T5, BART
- Custom Hugging Face models

### Image Models
- Stable Diffusion
- DALL-E (via API)
- Custom diffusion models

### Multimodal Models
- Qwen-VL
- LLaVA
- Custom vision-language models

## 📊 Monitoring & Logging

The agent provides comprehensive monitoring:

- **Real-time status**: Model and task status
- **Memory usage**: GPU and system memory
- **Performance metrics**: Execution times, throughput
- **Logging**: Configurable log levels and outputs

## 🚨 Error Handling

- **Graceful degradation**: Continues operation on non-critical errors
- **Retry mechanisms**: Automatic retry for failed operations
- **Resource cleanup**: Proper cleanup on errors
- **Detailed logging**: Comprehensive error information

## 🔒 Security Features

- **Input validation**: All inputs are validated
- **Resource limits**: Memory and execution time limits
- **CORS support**: Configurable cross-origin requests
- **Error sanitization**: Safe error messages

## 🧪 Testing

```bash
# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=ml_agent tests/
```

## 📈 Performance Tips

1. **Use appropriate precision**: `float16` for most models
2. **Enable memory optimization**: Automatic attention slicing
3. **Batch processing**: Group similar tasks
4. **Model caching**: Keep frequently used models in memory
5. **GPU optimization**: Use CUDA when available

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and docstrings
- **Issues**: Report bugs on GitHub
- **Discussions**: Ask questions in GitHub Discussions

## 🔮 Roadmap

- [ ] Web UI dashboard
- [ ] Model fine-tuning support
- [ ] Distributed training
- [ ] Model versioning
- [ ] Advanced scheduling
- [ ] Metrics export (Prometheus)
- [ ] Kubernetes deployment
- [ ] Model marketplace integration

---

**Built with ❤️ for the ML community**
