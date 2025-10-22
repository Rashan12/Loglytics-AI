# Ollama LLM Setup Scripts

This directory contains scripts for setting up and managing the Ollama local LLM integration for Loglytics AI.

## Scripts Overview

### 1. `install_ollama.py`
Installs Ollama on your system (Linux, macOS, Windows).

```bash
python backend/scripts/install_ollama.py
```

**Features:**
- Auto-detects operating system
- Installs Ollama via package manager
- Starts Ollama service
- Verifies installation

### 2. `setup_ollama.py`
Sets up and configures the best Ollama model for log analysis.

```bash
python backend/scripts/setup_ollama.py
```

**Features:**
- Recommends best models for 16GB RAM
- Pulls and installs recommended models
- Tests model inference with sample logs
- Creates configuration file
- Verifies model performance

### 3. `test_ollama.py`
Tests the Ollama integration with various scenarios.

```bash
python backend/scripts/test_ollama.py
```

**Features:**
- Basic inference testing
- Log analysis testing
- Chat functionality testing
- Anomaly detection testing
- Performance benchmarking

## Quick Start

### Step 1: Install Ollama
```bash
python backend/scripts/install_ollama.py
```

### Step 2: Setup Model
```bash
python backend/scripts/setup_ollama.py
```

### Step 3: Test Integration
```bash
python backend/scripts/test_ollama.py
```

## Recommended Models

The setup script automatically selects the best model for your system:

| Model | Size | Parameters | Best For |
|-------|------|------------|----------|
| `llama3.2:3b` | ~2.1GB | 3B | General log analysis |
| `phi3:3.8b` | ~2.3GB | 3.8B | Structured data analysis |
| `qwen2.5:3b` | ~2.0GB | 3B | Code and technical tasks |

## Configuration

After running `setup_ollama.py`, a configuration file is created at:
```
backend/app/config/llm_config.py
```

This file contains:
- Model settings
- Performance parameters
- Log analysis prompts
- Error handling configuration

## Troubleshooting

### Ollama Not Running
```bash
# Start Ollama service
ollama serve

# Check if running
curl http://localhost:11434/api/tags
```

### Model Not Found
```bash
# List installed models
ollama list

# Pull a specific model
ollama pull llama3.2:3b
```

### Performance Issues
- Ensure you have at least 8GB RAM
- Close other applications
- Use a smaller model if needed
- Check system resources

### Connection Issues
- Verify Ollama is running on port 11434
- Check firewall settings
- Ensure no other service is using the port

## Manual Installation

If the automated scripts fail, you can install Ollama manually:

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

### macOS
```bash
brew install ollama
ollama serve
```

### Windows
Download from: https://ollama.ai/download

## Usage in Application

Once set up, the Ollama integration can be used in your FastAPI application:

```python
from app.config.llm_config import get_ollama_config, get_log_analysis_prompts

# Get configuration
config = get_ollama_config()
prompts = get_log_analysis_prompts()

# Use in your LLM service
# (See app/services/llm/llm_service.py)
```

## Performance Tips

1. **Model Selection**: Choose the right model for your RAM
2. **Batch Processing**: Process multiple logs together
3. **Caching**: Enable response caching for repeated queries
4. **Streaming**: Use streaming for real-time responses
5. **Resource Monitoring**: Monitor CPU and memory usage

## Support

For issues with Ollama setup:
1. Check the Ollama documentation: https://ollama.ai/docs
2. Verify system requirements
3. Check logs for error messages
4. Try a different model if performance is poor

For Loglytics AI specific issues:
1. Check the configuration file
2. Verify the model is working with test script
3. Check application logs
4. Ensure proper permissions
