# Ollama LLM Setup for Loglytics AI

This guide will help you set up Ollama for local LLM inference in the Loglytics AI application.

## 🚀 Quick Start

### Windows Users
```cmd
# 1. Install Ollama
backend\scripts\install_ollama.bat

# 2. Setup Model
backend\scripts\setup_ollama.bat

# 3. Test Installation
backend\scripts\test_ollama.bat
```

### Linux/macOS Users
```bash
# 1. Install Ollama
python backend/scripts/install_ollama.py

# 2. Setup Model
python backend/scripts/setup_ollama.py

# 3. Test Installation
python backend/scripts/test_ollama.py
```

## 📋 What This Setup Does

1. **Installs Ollama** - Local LLM inference server
2. **Downloads Model** - Best model for 16GB RAM systems
3. **Tests Performance** - Verifies model is working correctly
4. **Creates Config** - Saves settings for the application
5. **Validates Setup** - Ensures everything is ready

## 🤖 Recommended Models

| Model | Size | RAM Usage | Best For |
|-------|------|-----------|----------|
| `llama3.2:3b` | ~2.1GB | 4-6GB | ⭐ **General log analysis** |
| `phi3:3.8b` | ~2.3GB | 5-7GB | Structured data analysis |
| `qwen2.5:3b` | ~2.0GB | 4-6GB | Code and technical tasks |

## 🔧 System Requirements

- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 5GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux
- **Python**: 3.10 or higher

## 📁 Files Created

After setup, these files will be created:

```
backend/
├── app/config/llm_config.py          # LLM configuration
├── scripts/
│   ├── setup_ollama.py              # Main setup script
│   ├── test_ollama.py               # Test script
│   ├── install_ollama.py            # Installer script
│   └── README.md                    # Detailed documentation
```

## 🧪 Testing the Setup

The test script will verify:

- ✅ Ollama service is running
- ✅ Model is available and working
- ✅ Log analysis capabilities
- ✅ Chat functionality
- ✅ Anomaly detection
- ✅ Performance benchmarks

## 🚨 Troubleshooting

### Common Issues

#### Ollama Not Starting
```bash
# Check if port is in use
netstat -an | findstr :11434

# Start Ollama manually
ollama serve
```

#### Model Not Found
```bash
# List installed models
ollama list

# Pull specific model
ollama pull llama3.2:3b
```

#### Out of Memory
- Use a smaller model: `llama3.2:1b`
- Close other applications
- Increase virtual memory

#### Slow Performance
- Check system resources
- Use a faster model
- Enable GPU acceleration (if available)

### Debug Commands

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test model directly
ollama run llama3.2:3b "Test message"

# Check system resources
tasklist /FI "IMAGENAME eq ollama.exe"
```

## 📊 Performance Expectations

### Response Times
- **Simple queries**: 1-3 seconds
- **Log analysis**: 3-10 seconds
- **Complex analysis**: 10-30 seconds

### Memory Usage
- **Model loading**: 4-6GB RAM
- **Inference**: 1-2GB additional
- **Total**: 6-8GB RAM

### Quality Scores
- **Log analysis**: 8-9/10
- **Pattern detection**: 7-8/10
- **Anomaly detection**: 8-9/10
- **Chat responses**: 7-8/10

## 🔒 Security & Privacy

- **Local Processing**: All data stays on your machine
- **No External Calls**: No data sent to external services
- **Full Control**: Complete control over data processing
- **Offline Capable**: Works without internet connection

## 📈 Optimization Tips

### 1. Model Selection
```python
# For faster inference
model = "llama3.2:1b"

# For better quality
model = "llama3.2:3b"

# For best quality (if you have 32GB+ RAM)
model = "llama3.2:8b"
```

### 2. System Optimization
```bash
# Windows: Increase virtual memory
# System Properties > Advanced > Performance Settings > Advanced > Virtual Memory

# Linux: Optimize memory usage
echo 'vm.swappiness=10' >> /etc/sysctl.conf
```

### 3. Ollama Configuration
```bash
# Set environment variables
set OLLAMA_NUM_PARALLEL=2
set OLLAMA_MAX_LOADED_MODELS=1
set OLLAMA_MAX_QUEUE=4
```

## 🆘 Getting Help

### Documentation
- [Ollama Docs](https://ollama.ai/docs)
- [Model Library](https://ollama.ai/library)
- [API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)

### Community
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Discord Community](https://discord.gg/ollama)

### Loglytics AI Support
- Check application logs
- Run test scripts
- Verify configuration
- Contact development team

## ✅ Verification Checklist

- [ ] Ollama is installed and running
- [ ] Model is downloaded and available
- [ ] Port 11434 is accessible
- [ ] Sufficient RAM available (8GB+)
- [ ] Python dependencies installed
- [ ] Configuration file created
- [ ] Test script passes all tests
- [ ] Application can connect to Ollama

## 🎯 Next Steps

1. **Run Setup**: Execute the setup script
2. **Test Installation**: Verify everything works
3. **Start Application**: Launch Loglytics AI
4. **Upload Logs**: Test with real log data
5. **Monitor Performance**: Keep an eye on system resources

## 📝 Example Usage

Once set up, you can use the LLM in your application:

```python
from app.services.llm.llm_service import LLMService

# Initialize service
llm_service = LLMService(db)

# Analyze logs
log_entries = [
    {"level": "ERROR", "message": "Database connection failed"},
    {"level": "WARN", "message": "High memory usage detected"}
]

analysis = await llm_service.analyze_logs(log_entries)
print(analysis["content"])
```

---

**Ready to get started?** Run the setup script and follow the prompts!
