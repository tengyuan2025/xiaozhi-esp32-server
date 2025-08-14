# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

小智后端服务 (Xiaozhi ESP32 Server) is an AI voice interaction system designed for ESP32 hardware devices. It provides comprehensive backend services including voice recognition, text-to-speech, large language model integration, and smart home IoT control capabilities.

## Architecture

This is a multi-component system with the following main parts:

### Core Components

1. **xiaozhi-server** (Python) - Core WebSocket/HTTP server that handles:
   - Voice activity detection (VAD) using SileroVAD
   - Speech recognition (ASR) with FunASR, DoubaoASR, TencentASR, etc.
   - Large language model integration (LLM) supporting ChatGLM, Doubao, OpenAI, etc.
   - Text-to-speech (TTS) with EdgeTTS, DoubaoTTS, AliyunTTS, etc.
   - Vision language models (VLLM) for multimodal interactions
   - Intent recognition and function calling
   - Memory systems (local and mem0ai)
   - Voice print recognition
   - MCP (Model Context Protocol) integration

2. **manager-api** (Java Spring Boot) - Management API backend with:
   - User authentication and authorization using Shiro
   - Device management and OTA updates
   - Configuration management
   - Agent/bot management
   - Voice print management
   - Database operations with MyBatis Plus
   - Redis caching

3. **manager-web** (Vue 2) - Web management interface for:
   - System configuration
   - Device management
   - Model configuration
   - User management
   - OTA management

4. **manager-mobile** (Uni-app) - Mobile management app supporting:
   - Cross-platform deployment (iOS, Android, H5, WeChat Mini Program)
   - Device configuration
   - Voice print management
   - Chat history viewing

## Development Commands

### Python Server (xiaozhi-server)
```bash
# Navigate to server directory
cd main/xiaozhi-server

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py

# Run performance tests
python performance_test_tool.py
python performance_tester_vllm.py
```

### Java API (manager-api)
```bash
# Navigate to API directory
cd main/manager-api

# Build the project
mvn clean compile

# Run tests
mvn test

# Package the application
mvn package

# Run the application
java -jar target/xiaozhi-esp32-api.jar
```

### Web Frontend (manager-web)
```bash
# Navigate to web directory
cd main/manager-web

# Install dependencies
npm install

# Start development server
npm run serve

# Build for production
npm run build

# Analyze bundle size
npm run analyze
```

### Mobile App (manager-mobile)
```bash
# Navigate to mobile directory
cd main/manager-mobile

# Install dependencies
pnpm install

# Start H5 development
pnpm run dev:h5

# Build H5
pnpm run build:h5

# Start WeChat Mini Program development
pnpm run dev:mp-weixin

# Build for Android
pnpm run build:app-android

# Type checking
pnpm run type-check

# Lint and fix code
pnpm run lint:fix
```

## Configuration System

The system uses a layered configuration approach:

1. **Base config**: `main/xiaozhi-server/config.yaml` - Main configuration file
2. **Override config**: `main/xiaozhi-server/data/.config.yaml` - Local overrides (takes precedence)
3. **API config**: `main/xiaozhi-server/config_from_api.yaml` - Configuration from management API

Key configuration sections:
- `server`: Basic server settings (IP, ports, WebSocket settings)
- `selected_module`: Choose which modules to use (VAD, ASR, LLM, TTS, etc.)
- `plugins`: Plugin configurations for weather, news, Home Assistant
- Module-specific configs: `ASR`, `LLM`, `TTS`, `VLLM`, `Memory`, `Intent`

## Key Architectural Patterns

### Provider Pattern
The system uses a provider pattern for all AI services:
- Base classes in `core/providers/*/base.py`
- Implementations in `core/providers/*/[provider_name].py`
- DTO objects for data transfer in `core/providers/*/dto/`

### Plugin System
- Function plugins in `plugins_func/functions/`
- Auto-registration via `plugins_func/register.py`
- Support for IoT control, weather, news, music, etc.

### MCP Integration
Multiple MCP (Model Context Protocol) integration points:
- Device MCP: `core/providers/tools/device_mcp/`
- Server MCP: `core/providers/tools/server_mcp/`
- MCP Endpoint: `core/providers/tools/mcp_endpoint/`

### WebSocket Communication
Main communication is through WebSocket with protocol defined by:
- Connection handling in `core/connection.py`
- Message handlers in `core/handle/`
- Server implementation in `core/websocket_server.py`

## Testing

### Audio Testing
Use `main/xiaozhi-server/test/test_page.html` in Chrome browser to test audio functionality.

### Performance Testing
- ASR/LLM/TTS performance: `python performance_test_tool.py`
- VLLM performance: `python performance_tester_vllm.py`

### Module-specific Testing
Individual test files in `main/xiaozhi-server/performance_text/`:
- `performance_tester_asr.py`
- `performance_tester_llm.py` 
- `performance_tester_tts.py`
- `performance_tester_vllm.py`

## Database

The Java API uses:
- MySQL database with Liquibase migrations in `main/manager-api/src/main/resources/db/changelog/`
- MyBatis Plus for ORM
- Redis for caching

## Security Notes

- JWT authentication in both Python server and Java API
- Shiro-based security in Java API
- Device token authentication for ESP32 connections
- API key management for various AI services

## Docker Support

The project includes Docker configuration:
- `main/xiaozhi-server/docker-compose.yml` - Single service deployment
- `main/xiaozhi-server/docker-compose_all.yml` - Full stack deployment

## Important Files

- `main/xiaozhi-server/app.py` - Main Python server entry point
- `main/manager-api/src/main/java/xiaozhi/AdminApplication.java` - Java API entry point
- `main/xiaozhi-server/config.yaml` - Main configuration file
- `main/manager-api/pom.xml` - Java dependencies
- `main/manager-web/package.json` - Web frontend dependencies
- `main/manager-mobile/package.json` - Mobile app dependencies