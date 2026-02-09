"""
FastAPI application for AI model routing service.

Architecture:
- POST /chat: Main endpoint that classifies, routes, and completes prompts
- GET /health: Simple health check
- GET /models: List available models

"""
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest, ChatResponse
from concentrate_client import ConcentrateClient
from classifier import PromptClassifier
from router import ModelRouter, MODEL_TIERS


# Global instances (initialized in lifespan)
concentrate_client: ConcentrateClient = None
prompt_classifier: PromptClassifier = None
model_router: ModelRouter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes shared resources on startup, cleans up on shutdown.
    """
    global concentrate_client, prompt_classifier, model_router
    
    # Startup: Initialize components
    try:
        concentrate_client = ConcentrateClient()
        prompt_classifier = PromptClassifier(concentrate_client)
        model_router = ModelRouter()
    except Exception as e:
        
        raise
    
    yield


# Initialize FastAPI app
app = FastAPI(
    title="AI Model Router",
    description="Dynamically routes prompts to optimal LLM models via Concentrate API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
# Allows requests from the React frontend running on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      
        "http://127.0.0.1:3000",      
    ],
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],              
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns service status.
    """
    return {
        "status": "healthy",
        "service": "ai-model-router",
        "version": "1.0.0"
    }


@app.get("/models")
async def list_models() -> Dict:
    """
    List available models organized by tier.
    
    Helpful for debugging and understanding options.
    """
    return {
        "model_tiers": MODEL_TIERS,
        "description": "Models organized by tier and optimization (cost/quality/latency)"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint: classify → route → complete.
    
    Flow:
    1. Classify prompt (task type + complexity)
    2. Route to optimal model based on classification + preference
    3. Generate completion with selected model
    4. Return response with routing transparency

    """
    try:
        # Step 1: Classify the prompt
        # Uses cheap model to determine task characteristics
        classification = await prompt_classifier.classify(request.prompt)
        
        # Step 2: Select optimal model
        # Rule-based routing considering task, complexity, and user preference
        model_name, routing_reason = model_router.select_model(
            classification,
            request.preference
        )
        
        # Step 3: Generate completion with selected model
        # Concentrate's unified API: same interface, different models. We don't need separate clients for each provider.
        response_text = await concentrate_client.complete(
            prompt=request.prompt,
            model=model_name,
            temperature=0.7
        )
        
        # Step 4: Return structured response
        return ChatResponse(
            response=response_text,
            model_used=model_name,
            routing_reason=routing_reason
        )
        
    except ValueError as e:
        # Client-side errors (validation, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except RuntimeError as e:
        # Server-side errors (API failures, etc.)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Completion failed: {str(e)}"
        )
    except Exception as e:
        # Unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for uncaught errors.
    
    Ensures we always return JSON, even for unexpected failures.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )