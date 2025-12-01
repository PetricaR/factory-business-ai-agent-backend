"""
FastAPI Application with LIVE AUDIO Streaming Support
Updated with latest ADK practices (October 2025)
FIXED: MCP session initialization timeout issues
ADDED: Google Custom Search (Programmable Search Engine)
"""

import os
import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from google.adk.cli.fast_api import get_fast_api_app
import json
from typing import AsyncIterator
# load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get port from Cloud Run environment
PORT = int(os.getenv("PORT", "8082"))

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure required API keys are set
GOOGLE_MAPS_CONFIGURED = bool(os.getenv("GOOGLE_MAPS_API_KEY"))
CUSTOM_SEARCH_CONFIGURED = bool(
    os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY") and 
    os.getenv("GOOGLE_CUSTOM_SEARCH_CX")
)

if not GOOGLE_MAPS_CONFIGURED:
    logger.warning(
        "GOOGLE_MAPS_API_KEY not set. MCP Google Maps integration will fail. "
        "Please set the environment variable: export GOOGLE_MAPS_API_KEY='your-key-here'"
    )

if not CUSTOM_SEARCH_CONFIGURED:
    logger.warning(
        "Google Custom Search not fully configured. Web search capabilities will be limited."
    )
    if not os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY"):
        logger.warning("  Missing: GOOGLE_CUSTOM_SEARCH_API_KEY")
    if not os.getenv("GOOGLE_CUSTOM_SEARCH_CX"):
        logger.warning("  Missing: GOOGLE_CUSTOM_SEARCH_CX")

# Session service URI (using SQLite for local development)
# ADK automatically manages sessions with Cloud Storage in production
SESSION_SERVICE_URI = "sqlite:///./sessions.db"

# CORS origins - configure based on your deployment
ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "http://localhost:8082",
    "http://localhost:3000",
    "http://127.0.0.1:8081",
    "http://127.0.0.1:8082",
    "http://127.0.0.1:3000",
    "*"  # Remove this in production!
]

# Enable web UI for testing
SERVE_WEB_INTERFACE = True

try:
    # Create FastAPI app with ADK agent
    # ADK automatically configures WebSocket routes for Live API models
    app: FastAPI = get_fast_api_app(
        agents_dir=AGENT_DIR,
        session_service_uri=SESSION_SERVICE_URI,
        allow_origins=ALLOWED_ORIGINS,
        web=SERVE_WEB_INTERFACE,
        trace_to_cloud=True,
    )
    
    logger.info(f"Successfully initialized ADK FastAPI app from {AGENT_DIR}")
    
except Exception as e:
    logger.error(f"Failed to initialize ADK FastAPI app: {e}")
    logger.error(
        "Make sure agent.py exists in the same directory as main.py and "
        "required environment variables are set"
    )
    raise

# Additional CORS configuration for broader compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Factory Finder AI Agent",
        "version": "2.2",
        "status": "running",
        "model": "gemini-2.5-flash-preview",
        "features": [
            "live_audio_streaming",
            "bidirectional_communication",
            "voice_activity_detection",
            "natural_interruptions",
            "mcp_google_maps_integration",
            "location_intelligence",
            "web_search_programmable",
            "custom_search_engine",
            "fixed_mcp_timeout_issue"
        ],
        "integrations": {
            "google_maps": GOOGLE_MAPS_CONFIGURED,
            "custom_search": CUSTOM_SEARCH_CONFIGURED,
            "targetare_api": bool(os.getenv("API_KEY_TARGETARE"))
        },
        "endpoints": {
            "web_ui": f"http://localhost:{PORT}",
            "api_docs": f"http://localhost:{PORT}/docs",
            "health": f"http://localhost:{PORT}/health",
            "info": f"http://localhost:{PORT}/info"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Cloud Run and monitoring.
    Returns detailed status about the agent and its capabilities.
    """
    return {
        "status": "healthy",
        "service": "factory-finder-agent",
        "version": "2.2",
        "api_integrations": {
            "google_maps": {
                "configured": GOOGLE_MAPS_CONFIGURED,
                "capabilities": ["geocoding", "places", "directions", "distance_matrix"] if GOOGLE_MAPS_CONFIGURED else []
            },
            "custom_search": {
                "configured": CUSTOM_SEARCH_CONFIGURED,
                "capabilities": ["web_search", "news_search", "image_search", "site_search"] if CUSTOM_SEARCH_CONFIGURED else []
            },
            "targetare": {
                "configured": bool(os.getenv("API_KEY_TARGETARE")),
                "capabilities": ["company_data", "financial_analysis", "market_intelligence"] if os.getenv("API_KEY_TARGETARE") else []
            }
        },
        "model": {
            "name": "gemini-2.5-flash-preview",
            "type": "live_api",
            "generation": "2.5",
            "capabilities": [
                "audio_input",
                "audio_output",
                "video_input",
                "text_input",
                "text_output",
                "function_calling",
                "code_execution",
                "search_grounding"
            ]
        },
        "streaming": {
            "enabled": True,
            "protocol": "websocket",
            "bidirectional": True,
            "vad_enabled": True,
            "interruption_support": True,
            "sse_streaming": True,
            "async_stream_query": True
        },
        "tools": {
            "mcp_integration": True,
            "google_maps_api": GOOGLE_MAPS_CONFIGURED,
            "custom_search_api": CUSTOM_SEARCH_CONFIGURED,
            "mcp_timeout": "60s"
        }
    }


@app.get("/info")
async def agent_info():
    """
    Information about the agent and its capabilities.
    Useful for debugging and understanding what the agent can do.
    """
    return {
        "agent": {
            "name": "Factory Finder AI",
            "purpose": "Location intelligence + Web research for Romanian entrepreneurs",
            "target_users": "Factory by Raiffeisen Bank applicants",
            "version": "2.2"
        },
        "supported_cities": [
            "București",
            "Cluj-Napoca",
            "Timișoara",
            "Iași",
            "Constanța",
            "Brașov"
        ],
        "capabilities": [
            "Competitor density analysis",
            "Accessibility scoring",
            "Location comparison",
            "Demographic insights",
            "Cost estimation",
            "Real-time voice interaction",
            "Web search & research",
            "Market trend analysis",
            "Industry insights"
        ],
        "search_capabilities": {
            "enabled": CUSTOM_SEARCH_CONFIGURED,
            "types": [
                "General web search",
                "Industry-specific search",
                "Market research",
                "Competitor research",
                "News and trends",
                "Romanian business insights"
            ] if CUSTOM_SEARCH_CONFIGURED else ["Limited - API keys not configured"]
        },
        "data_sources": {
            "location": "Google Maps Platform API" if GOOGLE_MAPS_CONFIGURED else "Not configured",
            "web_search": "Google Programmable Search Engine" if CUSTOM_SEARCH_CONFIGURED else "Not configured",
            "business_data": "Targetare Official API" if os.getenv("API_KEY_TARGETARE") else "Not configured"
        },
        "usage": {
            "voice": "Click microphone in Web UI and speak naturally",
            "text": "Type your query in the chat interface",
            "api": "Use /docs for API documentation"
        },
        "fixes": [
            "MCP session timeout increased to 60 seconds",
            "Better error handling for MCP initialization",
            "Improved WebSocket stability",
            "Added Google Custom Search integration",
            "Implemented SSE streaming with async_stream_query",
            "Added RunConfig for advanced streaming scenarios"
        ],
        "streaming_endpoints": {
            "sse_streaming": "/stream-query",
            "websocket": "/ws (via ADK auto-configuration)",
            "description": "Use /stream-query for text streaming, WebSocket for live audio"
        }
    }


@app.get("/config")
async def config_status():
    """
    Configuration status endpoint - shows what's configured and what's missing.
    Helpful for troubleshooting deployment issues.
    """
    config_status = {
        "environment": os.getenv("K_SERVICE", "local"),
        "required_keys": {
            "GOOGLE_MAPS_API_KEY": {
                "configured": GOOGLE_MAPS_CONFIGURED,
                "required_for": "Location intelligence, maps integration"
            },
            "API_KEY_TARGETARE": {
                "configured": bool(os.getenv("API_KEY_TARGETARE")),
                "required_for": "Romanian company data, financial analysis"
            }
        },
        "optional_keys": {
            "GOOGLE_CUSTOM_SEARCH_API_KEY": {
                "configured": bool(os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")),
                "required_for": "Web search, market research"
            },
            "GOOGLE_CUSTOM_SEARCH_CX": {
                "configured": bool(os.getenv("GOOGLE_CUSTOM_SEARCH_CX")),
                "required_for": "Custom search engine ID"
            }
        },
        "recommendations": []
    }
    
    # Add recommendations for missing configurations
    if not GOOGLE_MAPS_CONFIGURED:
        config_status["recommendations"].append({
            "severity": "high",
            "message": "Set GOOGLE_MAPS_API_KEY for location features",
            "action": "export GOOGLE_MAPS_API_KEY='your-api-key'"
        })
    
    if not os.getenv("API_KEY_TARGETARE"):
        config_status["recommendations"].append({
            "severity": "high",
            "message": "Set API_KEY_TARGETARE for business intelligence",
            "action": "export API_KEY_TARGETARE='your-api-key'"
        })
    
    if not CUSTOM_SEARCH_CONFIGURED:
        config_status["recommendations"].append({
            "severity": "medium",
            "message": "Set Google Custom Search keys for web research",
            "action": "export GOOGLE_CUSTOM_SEARCH_API_KEY='your-key' && export GOOGLE_CUSTOM_SEARCH_CX='your-cx-id'"
        })
    
    return config_status


@app.post("/stream-query")
async def stream_query(request: Request):
    """
    Streaming query endpoint using Server-Sent Events (SSE).
    
    This endpoint streams responses in real-time as they are generated,
    instead of waiting for the complete response.
    
    Request body:
        {
            "user_id": "unique-user-id",
            "message": "Your question here",
            "session_id": "optional-session-id"
        }
    
    Response format: Server-Sent Events (SSE)
        event: message
        data: {"type": "text", "content": "streaming text..."}
        
        event: done
        data: {"type": "complete"}
    
    Example usage:
        curl -N -X POST http://localhost:8082/stream-query \
             -H "Content-Type: application/json" \
             -d '{"user_id": "test-user", "message": "Research coffee shop trends in Romania"}'
    
    Cloud Run deployment:
        curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
             -H "Content-Type: application/json" \
             https://LOCATION-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/reasoningEngines/RESOURCE_ID:streamQuery?alt=sse \
             -d '{
               "class_method": "async_stream_query",
               "input": {
                 "user_id": "USER_ID",
                 "message": "Your question"
               }
             }'
    """
    try:
        # Import here to avoid circular imports
        from agent_factory_ai.agent import create_streaming_app
        
        # Parse request body
        body = await request.json()
        user_id = body.get("user_id", "anonymous")
        message = body.get("message")
        session_id = body.get("session_id", None)
        
        if not message:
            return {"error": "Missing 'message' in request body"}
        
        # Create streaming app
        streaming_app = create_streaming_app()
        
        async def event_generator() -> AsyncIterator[str]:
            """Generate SSE events from agent responses."""
            try:
                # Stream query results
                async for event in streaming_app.async_stream_query(
                    user_id=user_id,
                    message=message,
                    session_id=session_id
                ):
                    # Format as SSE
                    event_data = {
                        "type": "event",
                        "content": str(event)
                    }
                    yield f"event: message\n"
                    yield f"data: {json.dumps(event_data)}\n\n"
                
                # Send completion event
                yield f"event: done\n"
                yield f"data: {{\"type\": \"complete\"}}\n\n"
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                error_data = {
                    "type": "error",
                    "content": str(e)
                }
                yield f"event: error\n"
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )
        
    except Exception as e:
        logger.error(f"Stream query error: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎤 Factory Finder Agent - LIVE AUDIO + SSE STREAMING")
    print("   Enhanced with Programmable Search Engine (October 2025)")
    print("=" * 70)
    print(f"\n📍 Endpoints:")
    print(f"   🌐 Web UI:      http://localhost:{PORT}")
    print(f"   📚 API Docs:    http://localhost:{PORT}/docs")
    print(f"   ❤️  Health:      http://localhost:{PORT}/health")
    print(f"   ℹ️  Info:        http://localhost:{PORT}/info")
    print(f"   ⚙️  Config:      http://localhost:{PORT}/config")
    print(f"   🌊 Streaming:   http://localhost:{PORT}/stream-query")
    
    print(f"\n🎙️  Audio Features:")
    print(f"   ✓ Bidirectional streaming (WebSocket)")
    print(f"   ✓ Voice Activity Detection (VAD)")
    print(f"   ✓ Natural interruptions")
    print(f"   ✓ Low-latency responses")
    
    print(f"\n🌊 Text Streaming (NEW):")
    print(f"   ✓ Server-Sent Events (SSE)")
    print(f"   ✓ Real-time response streaming")
    print(f"   ✓ async_stream_query support")
    print(f"   ✓ Cloud Run compatible")
    
    print(f"\n🗺️  Location Intelligence:")
    if GOOGLE_MAPS_CONFIGURED:
        print(f"   ✓ Google Maps via MCP")
        print(f"   ✓ Competitor analysis")
        print(f"   ✓ Accessibility scoring")
        print(f"   ✓ Multi-location comparison")
    else:
        print(f"   ✗ Google Maps NOT configured")
        print(f"   → Set GOOGLE_MAPS_API_KEY environment variable")
    
    print(f"\n🔍 Web Search & Research:")
    if CUSTOM_SEARCH_CONFIGURED:
        print(f"   ✓ Google Programmable Search Engine")
        print(f"   ✓ Market research capabilities")
        print(f"   ✓ Industry insights & trends")
        print(f"   ✓ Competitor intelligence")
        print(f"   ✓ News and updates")
    else:
        print(f"   ✗ Custom Search NOT fully configured")
        if not os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY"):
            print(f"   → Set GOOGLE_CUSTOM_SEARCH_API_KEY")
        if not os.getenv("GOOGLE_CUSTOM_SEARCH_CX"):
            print(f"   → Set GOOGLE_CUSTOM_SEARCH_CX")
    
    print(f"\n📊 Business Intelligence:")
    if os.getenv("API_KEY_TARGETARE"):
        print(f"   ✓ Targetare API integration")
        print(f"   ✓ Romanian company data")
        print(f"   ✓ Financial analysis")
    else:
        print(f"   ✗ Targetare API NOT configured")
        print(f"   → Set API_KEY_TARGETARE environment variable")
    
    print(f"\n🔧 System Status:")
    print(f"   ✓ MCP timeout: 60s (optimized)")
    print(f"   ✓ Better error handling")
    print(f"   ✓ Improved session management")
    print(f"   ✓ Multi-source intelligence")
    
    print("=" * 70)
    print("\n💡 Quick Start:")
    print("   1. Configure ALL API keys (check /config endpoint)")
    print("   2. Open http://localhost:{} in your browser".format(PORT))
    print("   3. Click the microphone icon 🎤")
    print("   4. Grant microphone permissions")
    print("   5. Start speaking about your business idea!")
    
    print("\n💬 Enhanced query examples:")
    print("   • 'I want to open a coffee shop in Cluj-Napoca'")
    print("   • 'Research current coffee shop trends in Romania'")
    print("   • 'What's the competition like in București?'")
    print("   • 'Find latest news about restaurant industry'")
    print("   • 'Compare locations in Timișoara with market data'")
    print("   • 'Search for Romanian startup success stories'")
    
    # Display warnings for missing configurations
    warnings = []
    if not GOOGLE_MAPS_CONFIGURED:
        warnings.append("GOOGLE_MAPS_API_KEY")
    if not os.getenv("API_KEY_TARGETARE"):
        warnings.append("API_KEY_TARGETARE")
    if not CUSTOM_SEARCH_CONFIGURED:
        if not os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY"):
            warnings.append("GOOGLE_CUSTOM_SEARCH_API_KEY")
        if not os.getenv("GOOGLE_CUSTOM_SEARCH_CX"):
            warnings.append("GOOGLE_CUSTOM_SEARCH_CX")
    
    if warnings:
        print("\n⚠️  WARNING: Missing configuration!")
        for key in warnings:
            print(f"   ✗ {key} not set")
        print("\n   Some features will not work. Set missing keys with:")
        print("   export KEY_NAME='your-value'")
        print("\n   Or create .env file with all keys")
    else:
        print("\n✅ All API keys configured! Full functionality available.")
    
    print("=" * 70 + "\n")
    
    # Start server with optimized settings for Live API
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        # WebSocket configuration for stable connections
        ws_ping_interval=20,  # Keep connections alive
        ws_ping_timeout=20,
        # Performance optimization
        timeout_keep_alive=75,
    )