# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is xiaozhi-esp32-server, an open-source intelligent hardware backend service for ESP32 devices. The project provides a comprehensive AI voice assistant server with support for speech recognition (ASR), text-to-speech (TTS), large language models (LLM), and vision language models (VLLM).

## Architecture

The project follows a multi-module architecture:

- **main/xiaozhi-server/**: Python backend service (WebSocket + HTTP server)
- **main/manager-api/**: Java Spring Boot management API
- **main/manager-web/**: Vue.js frontend management interface

### Core Components

1. **WebSocket Server** (`core/websocket_server.py`): Main communication hub for ESP32 devices
2. **HTTP Server** (`core/http_server.py`): Handles OTA updates and vision analysis APIs
3. **Provider System** (`core/providers/`): Modular AI service providers
   - ASR: FunASR, Doubao, Baidu, Tencent, Aliyun, Sherpa
   - LLM: OpenAI-compatible, Ollama, Dify, Gemini, Coze
   - TTS: Edge, Doubao, FishSpeech, GPT-SoVITS, Minimax
   - VLLM: Vision models for image understanding
   - Memory: mem0ai, local memory systems
   - Intent: Function calling and intent recognition
4. **Plugin System** (`plugins_func/`): Extensible functionality plugins
5. **MCP Integration** (`core/mcp/`): Model Context Protocol support

## Development Commands

### Python Backend (main/xiaozhi-server/)

**Prerequisites**: Python virtual environment must be activated

```bash
# Activate virtual environment (REQUIRED)
source venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt

# Run the server
python app.py

# Performance testing
python performance_tester.py
python performance_tester_vllm.py

# Audio interaction testing
# Open main/xiaozhi-server/test/test_page.html in Chrome browser
```

**Common Issues**:
- **Virtual environment**: Always activate with `source venv/bin/activate` before running
- Server runs on port 8000 by default
- Requires configuration in config.yaml or data/.config.yaml

### Vue.js Frontend (main/manager-web/)

```bash
# Install dependencies
npm install

# Development server
npm run serve

# Build for production
npm run build

# Bundle analysis
npm run analyze
```

**Prerequisites**: 
- Node.js 18.x is recommended (compatible with ICU libraries)
- Use nvm for Node.js version management if encountering ICU errors

```bash
# Install nvm (if needed)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install and use Node.js 18.20.0
nvm install 18.20.0
nvm use 18.20.0
```

**Common Issues**:
- **ICU library errors**: Node.js 22.x may have ICU library conflicts on macOS with Homebrew ICU
- **Solution**: Use Node.js 18.20.0 via nvm instead of the Homebrew Node.js version
- Frontend runs on port 8003 and connects to Java backend on port 8002

### Java Backend (main/manager-api/)

**Prerequisites**: 
- Maven must be installed (`brew install maven`)
- Java 21 is required (use `export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home`)

```bash
# Set Java version
export JAVA_HOME=/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home

# Build with Maven
mvn clean package -DskipTests=true

# Run Spring Boot application
mvn spring-boot:run

# Or run built JAR file
java -jar target/xiaozhi-esp32-api.jar --server.port=8002
```

**Common Issues**:
- **Java 24 incompatibility**: Use Java 21 to avoid Lombok compilation errors
- **MyBatis mapping errors**: Ensure all VO classes are properly compiled
- Application starts on port 8002 by default
- Swagger UI available at: http://localhost:8002/xiaozhi/doc.html
- If launch.json fails, ensure Maven is installed and Java 21 is set

## Configuration

### Main Configuration
- **config.yaml**: Main configuration file with AI service settings
- **data/.config.yaml**: Override configuration (gitignored, for secrets)
- **config_from_api.yaml**: API-managed configuration when using management interface

### Key Configuration Sections
- `server`: WebSocket/HTTP server settings
- `selected_module`: Choose which AI providers to use
- `LLM/ASR/TTS/VLLM`: Provider-specific configurations
- `plugins`: Plugin settings for weather, news, Home Assistant integration
- `prompt`: System prompt for the AI assistant character

## Testing

### Test Tools Available
1. **Audio Interaction Test**: `main/xiaozhi-server/test/test_page.html`
2. **Performance Tester**: `performance_tester.py` (ASR/LLM/TTS)
3. **Vision Model Tester**: `performance_tester_vllm.py`

### Common Test Commands
```bash
# Test model performance
cd main/xiaozhi-server
python performance_tester.py

# Test vision models
python performance_tester_vllm.py
```

## Deployment

The project supports multiple deployment methods:
1. **Docker**: Full containerized deployment
2. **Source Code**: Local development deployment
3. **Hybrid**: Mix of Docker and local services

### Docker Deployment
```bash
# Simple server only
docker-compose up

# Full stack with database
docker-compose -f docker-compose_all.yml up
```

## Plugin Development

Plugins are located in `plugins_func/functions/` and follow this structure:
- Each plugin is a Python module with specific function signatures
- Register plugins in the configuration under `Intent.function_call.functions`
- Built-in plugins: weather, news, music playback, Home Assistant integration

## Database

The Java backend uses:
- **MySQL**: Primary database
- **Redis**: Caching and session management
- **Liquibase**: Database migrations (in `main/manager-api/src/main/resources/db/changelog/`)

## Security Notes

- API keys and secrets should be placed in `data/.config.yaml`
- Authentication can be enabled via `server.auth.enabled`
- Device tokens are configured in `server.auth.tokens`
- CORS and XSS protection implemented in Java backend

## Common Issues

1. **Audio Format**: Project uses OPUS format for audio transmission
2. **FFMPEG**: Required for audio processing, automatically checked on startup
3. **Model Downloads**: Local models (FunASR, Silero-VAD) need to be downloaded to `models/` directory
4. **Timezone**: Configure `server.timezone_offset` for correct timestamp handling
5. **Java Version**: Must use Java 21, not Java 24 (Lombok compatibility)
6. **Python Environment**: Always activate venv before running Python services
7. **VS Code Launch**: Requires Maven installation for Java debugging

## File Structure Notes

- `tmp/`: Temporary audio files (auto-cleaned)
- `logs/`: Application logs
- `data/`: User data and override configurations
- `models/`: Local AI models
- `music/`: Music files for playback plugin
- `config/assets/`: Static assets (wake words, notification sounds)