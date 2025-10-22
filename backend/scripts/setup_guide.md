# Ollama LLM Setup Guide for Loglytics AI

This guide will help you set up and configure Ollama for local LLM inference in the Loglytics AI application.

## Prerequisites

- **RAM**: At least 8GB (16GB recommended)
- **Storage**: 5GB free space for models
- **OS**: Linux, macOS, or Windows
- **Python**: 3.10 or higher

## Quick Setup (Recommended)

### Step 1: Install Ollama
```bash
# Run the automated installer
python backend/scripts/install_ollama.py
```

### Step 2: Setup Model
```bash
# Configure the best model for your system
python backend/scripts/setup_ollama.py
```

### Step 3: Test Installation
```bash
# Verify everything is working
python backend/scripts/test_ollama.py
```

## Manual Setup

### 1. Install Ollama

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### macOS
```bash
brew install ollama
```

#### Windows
Download from: https://ollama.ai/download

### 2. Start Ollama Service
```bash
ollama serve
```

### 3. Pull Recommended Model
```bash
# For 16GB RAM systems
ollama pull llama3.2:3b

# Alternative models
ollama pull phi3:3.8b
ollama pull qwen2.5:3b
```

### 4. Test Model
```bash
ollama run llama3.2:3b "Hello, can you help me analyze logs?"
```

## Model Recommendations

| Model | Size | RAM Usage | Best For |
|-------|------|-----------|----------|
| `llama3.2:3b` | ~2.1GB | 4-6GB | General log analysis |
| `phi3:3.8b` | ~2.3GB | 5-7GB | Structured data analysis |
| `qwen2.5:3b` | ~2.0GB | 4-6GB | Code and technical tasks |
| `llama3.2:1b` | ~1.3GB | 2-4GB | Lightweight systems |
| `gemma2:2b` | ~1.6GB | 3-5GB | Fast inference |

## Configuration

After running the setup script, configuration is saved to:
```
backend/app/config/llm_config.py
```

### Key Settings

```python
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "model_name": "llama3.2:3b",
    "timeout": 60,
    "temperature": 0.3,
    "max_tokens": 2000
}
```

## Usage in Application

### Basic Usage
```python
from app.services.llm.llm_service import LLMService

# Initialize service
llm_service = LLMService(db)

# Generate response
response = await llm_service.generate_response(
    session_id=1,
    user_message="Analyze these logs for errors"
)
```

### Log Analysis
```python
# Analyze log entries
log_entries = [
    {"level": "ERROR", "message": "Database connection failed"},
    {"level": "WARN", "message": "High memory usage detected"}
]

analysis = await llm_service.analyze_logs(log_entries)
```

### Anomaly Detection
```python
# Detect anomalies
anomalies = await llm_service.detect_anomalies(log_entries)
```

## Performance Optimization

### 1. Model Selection
- Choose the right model for your RAM
- Smaller models = faster inference
- Larger models = better quality

### 2. System Optimization
```bash
# Increase file descriptor limits
ulimit -n 65536

# Optimize memory usage
echo 'vm.swappiness=10' >> /etc/sysctl.conf
```

### 3. Ollama Configuration
```bash
# Set environment variables
export OLLAMA_NUM_PARALLEL=2
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_MAX_QUEUE=4
```

## Troubleshooting

### Common Issues

#### 1. Ollama Not Starting
```bash
# Check if port is in use
lsof -i :11434

# Kill existing process
pkill ollama

# Start fresh
ollama serve
```

#### 2. Model Not Found
```bash
# List installed models
ollama list

# Pull specific model
ollama pull llama3.2:3b
```

#### 3. Out of Memory
- Use a smaller model
- Close other applications
- Increase swap space
- Use model quantization

#### 4. Slow Performance
- Check system resources
- Use a faster model
- Enable GPU acceleration (if available)
- Optimize prompts

### Debug Commands

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test model directly
ollama run llama3.2:3b "Test message"

# Check system resources
htop
free -h
df -h
```

## Advanced Configuration

### Custom Model Configuration
```python
# In llm_config.py
CUSTOM_MODEL_CONFIG = {
    "model_name": "custom-model:latest",
    "temperature": 0.1,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "num_ctx": 4096
}
```

### GPU Acceleration
```bash
# Install CUDA support (Linux)
export CUDA_VISIBLE_DEVICES=0
ollama run llama3.2:3b
```

### Model Quantization
```bash
# Use quantized models for better performance
ollama pull llama3.2:3b-q4_K_M
```

## Monitoring and Maintenance

### Health Checks
```python
# Check service health
health = await llm_service.health_check()
print(health)
```

### Performance Monitoring
```python
# Monitor response times
import time

start = time.time()
response = await llm_service.generate_response(...)
duration = time.time() - start
print(f"Response time: {duration:.2f}s")
```

### Model Updates
```bash
# Update model
ollama pull llama3.2:3b

# Remove old model
ollama rm old-model:version
```

## Security Considerations

### 1. Network Security
- Run Ollama on localhost only
- Use firewall rules if needed
- Consider VPN for remote access

### 2. Model Security
- Use trusted model sources
- Verify model checksums
- Regular security updates

### 3. Data Privacy
- Models run locally
- No data sent to external services
- Full control over data processing

## Support and Resources

### Documentation
- [Ollama Documentation](https://ollama.ai/docs)
- [Model Library](https://ollama.ai/library)
- [API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)

### Community
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Discord Community](https://discord.gg/ollama)
- [Reddit Community](https://reddit.com/r/ollama)

### Loglytics AI Support
- Check application logs
- Run test scripts
- Verify configuration
- Contact support team

## Next Steps

1. **Test the Setup**: Run the test script to verify everything works
2. **Configure Application**: Update your app settings to use Ollama
3. **Upload Logs**: Test with real log data
4. **Monitor Performance**: Keep an eye on system resources
5. **Optimize**: Fine-tune settings for your use case

## Troubleshooting Checklist

- [ ] Ollama is installed and running
- [ ] Model is downloaded and available
- [ ] Port 11434 is accessible
- [ ] Sufficient RAM available
- [ ] Python dependencies installed
- [ ] Configuration file created
- [ ] Test script passes
- [ ] Application can connect to Ollama

For additional help, check the logs or contact the development team.
