# 🦙 Ollama Setup Guide for Meal Planning

## Quick Setup Steps

### 1. Install Ollama

#### **macOS:**
```bash
# Option 1: Download from website
# Go to https://ollama.ai and download the installer

# Option 2: Using Homebrew
brew install ollama
```

#### **Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### **Windows:**
Download from https://ollama.ai and run the installer

### 2. Start Ollama Service
```bash
# Start Ollama (runs on localhost:11434)
ollama serve
```

### 3. Download Recommended Models

#### **For Meal Planning (Choose one):**

```bash
# Option 1: Llama 3 Instruct (Recommended - Good balance)
ollama pull llama3:instruct

# Option 2: Qwen2 7B (Excellent for structured JSON)
ollama pull qwen2:7b

# Option 3: Mistral 7B (Fast and efficient)
ollama pull mistral:7b

# Option 4: Larger models (if you have good hardware)
ollama pull llama3:70b
ollama pull qwen2:72b
```

### 4. Test Your Setup
```bash
# Test if Ollama is working
curl http://localhost:11434/api/generate -d '{
  "model": "llama3:instruct",
  "prompt": "Create a simple breakfast recipe in JSON format with calories and ingredients",
  "stream": false
}'
```

## 🔧 Configuration

### Update your .env file:
```env
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Set defaults
DEFAULT_LLM_PROVIDER=ollama
DEFAULT_LLM_MODEL=llama3:instruct
```

## 🚀 Testing with Your API

### **Quick Test Commands:**

#### **1. Test with Llama 3 Instruct:**
```bash
POST /meal-plans/quick-generate?llm_provider=ollama&llm_model=llama3:instruct&regenerate=true
```

#### **2. Test with Qwen2:**
```bash
POST /meal-plans/quick-generate?llm_provider=ollama&llm_model=qwen2:7b&regenerate=true
```

#### **3. Test with Mistral:**
```bash
POST /meal-plans/quick-generate?llm_provider=ollama&llm_model=mistral:7b&regenerate=true
```

#### **4. Test with custom calories:**
```bash
POST /meal-plans/quick-generate?llm_provider=ollama&llm_model=llama3:instruct&custom_calories=2200&regenerate=true
```

## 📊 Model Comparison

### **Llama 3 Instruct** ⭐ **Recommended**
- **Size**: ~4.7GB
- **Speed**: Medium
- **Quality**: Excellent for meal planning
- **JSON**: Very good at structured responses
- **Best for**: Balanced performance and quality

### **Qwen2 7B** ⭐ **Best for JSON**
- **Size**: ~4.4GB  
- **Speed**: Fast
- **Quality**: Excellent
- **JSON**: Outstanding structured responses
- **Best for**: When you need perfect JSON formatting

### **Mistral 7B** ⭐ **Fastest**
- **Size**: ~4.1GB
- **Speed**: Very fast
- **Quality**: Good
- **JSON**: Good structured responses
- **Best for**: Quick testing and development

### **Larger Models (if you have 16GB+ RAM):**
- **llama3:70b**: Best quality but slow
- **qwen2:72b**: Excellent quality and JSON

## 🛠️ Troubleshooting

### **Common Issues:**

#### **1. "Connection refused" error:**
```bash
# Make sure Ollama is running
ollama serve

# Check if it's running
curl http://localhost:11434/api/tags
```

#### **2. Model not found:**
```bash
# List available models
ollama list

# Pull the model if missing
ollama pull llama3:instruct
```

#### **3. Slow responses:**
```bash
# Use smaller models for faster responses
ollama pull mistral:7b

# Or reduce context in the API call
```

#### **4. JSON parsing errors:**
- Try `qwen2:7b` - it's excellent at JSON
- Or add more specific JSON instructions in prompts

### **Performance Tips:**

#### **For Better Speed:**
1. Use smaller models (7B instead of 70B)
2. Ensure you have enough RAM
3. Close other applications
4. Use SSD storage

#### **For Better Quality:**
1. Use larger models if you have the hardware
2. Adjust temperature (lower = more consistent)
3. Use specific prompts

## 🎯 Demo Setup

### **For Interview Demo:**

#### **1. Quick Setup:**
```bash
# Install and start Ollama
ollama serve

# Download recommended model
ollama pull llama3:instruct

# Test it works
curl http://localhost:11434/api/tags
```

#### **2. Test API:**
```bash
# Generate a meal plan
POST /meal-plans/quick-generate?llm_provider=ollama&llm_model=llama3:instruct

# Check the results
GET /meal-plans/today
```

#### **3. Demo Script:**
```bash
# 1. Show model selection flexibility
POST /meal-plans/quick-generate?llm_provider=ollama&llm_model=llama3:instruct&regenerate=true

# 2. Try different model
POST /meal-plans/quick-generate?llm_provider=ollama&llm_model=qwen2:7b&regenerate=true

# 3. Show custom calorie adjustment
POST /meal-plans/quick-generate?llm_provider=ollama&llm_model=llama3:instruct&custom_calories=2500&regenerate=true
```

## 📱 Model Management

### **Useful Ollama Commands:**

```bash
# List downloaded models
ollama list

# Remove a model to save space
ollama rm mistral:7b

# Update a model
ollama pull llama3:instruct

# Show model info
ollama show llama3:instruct

# Run interactive chat (for testing)
ollama run llama3:instruct
```

## 🔍 Monitoring

### **Check Ollama Status:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check model list
curl http://localhost:11434/api/tags | jq

# Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "llama3:instruct",
  "prompt": "Hello",
  "stream": false
}' | jq
```

## 💡 Pro Tips

### **1. Model Selection:**
- **Development**: Use `mistral:7b` for speed
- **Demo**: Use `llama3:instruct` for quality
- **Production**: Use `qwen2:7b` for JSON reliability

### **2. Performance:**
- Keep Ollama running in background
- Pre-load models you'll use
- Monitor RAM usage

### **3. Backup Plan:**
- Keep OpenAI/Anthropic configs ready
- Test multiple models before demo
- Have fallback options

## 🎬 Ready for Demo!

Once you have Ollama running with a model downloaded, you can:

1. **Generate meal plans locally** (no API costs!)
2. **Switch between models** in real-time
3. **Show flexibility** of the system
4. **Demonstrate privacy** (all local processing)

Your meal planning system will work perfectly with Ollama, giving you a cost-effective, private, and flexible AI solution for your interview demo!

## 🆘 Need Help?

If you run into issues:
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Verify model is downloaded: `ollama list`
3. Test with simple prompt first
4. Check system resources (RAM/CPU)
5. Try a smaller model if performance is slow

The system is designed to work seamlessly with any of these models!
