"""
Pydantic models for request validation and response serialization.
"""
from enum import Enum
from pydantic import BaseModel, Field


class UserPreference(str, Enum):
    """User's routing preference."""
    COST = "cost"
    QUALITY = "quality"
    LATENCY = "latency"


class TaskType(str, Enum):
    """Classified task category."""
    CODING = "coding"
    REASONING = "reasoning"
    SUMMARIZATION = "summarization"
    CREATIVE = "creative"


class Complexity(str, Enum):
    """Task complexity level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ChatRequest(BaseModel):
    """Incoming chat request from client."""
    prompt: str = Field(..., min_length=1, description="User's prompt to route and complete")
    preference: UserPreference = Field(
        default=UserPreference.QUALITY,
        description="Routing preference: optimize for cost, quality, or latency"
    )


class PromptClassification(BaseModel):
    """Result of prompt analysis."""
    task_type: TaskType
    complexity: Complexity
    reasoning: str


class ChatResponse(BaseModel):
    """Final response returned to client."""
    
    model_config = {"protected_namespaces": ()}
    
    response: str = Field(..., description="Model's completion output")
    model_used: str = Field(..., description="Which LLM model was selected")
    routing_reason: str = Field(..., description="Human-readable explanation of routing logic")