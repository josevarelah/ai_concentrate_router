"""
Client for Concentrate AI API.

Concentrate provides a unified API for 50+ LLM models across multiple providers.
"""
import os
import httpx
from typing import Optional
from dotenv import load_dotenv

from models import PromptClassification

# Load environment variables from .env file
load_dotenv()


class ConcentrateClient:
    """
    Client for interacting with Concentrate AI API.
    
    Concentrate provides unified access to 50+ models:
    """
    
    def __init__(self):
        self.api_key = os.getenv("CONCENTRATE_API_KEY")
        self.base_url = os.getenv("CONCENTRATE_BASE_URL", "https://api.concentrate.ai")
        
        if not self.api_key:
            raise ValueError(
                "CONCENTRATE_API_KEY environment variable is required.\n"
                "Get your API key at: https://app.concentrate.ai"
            )
        
        # Build full endpoint URL
        if not self.base_url.startswith("http"):
            self.base_url = f"https://{self.base_url}"
        
        # Remove trailing /v1 if present
        self.base_url = self.base_url.rstrip("/").replace("/v1", "")
        self.endpoint = f"{self.base_url}/v1/responses"
        
        # Initialize async HTTP client
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            timeout=60.0
        )
        
        print(f"Connected to Concentrate AI API")
    
    async def classify_prompt(self, prompt: str) -> PromptClassification:
        """
        Use a cheap/fast model to classify the prompt.

        """
        classification_prompt = f"""Analyze this prompt and classify it:

Prompt: "{prompt}"

Respond in this exact format:
TASK_TYPE: [coding|reasoning|summarization|creative]
COMPLEXITY: [low|medium|high]
REASONING: [one sentence explanation]

Guidelines:
- coding: involves writing, debugging, or explaining code
- reasoning: logic puzzles, analysis, problem-solving
- summarization: condensing or explaining existing content
- creative: storytelling, brainstorming, creative writing
- low: simple, straightforward tasks
- medium: moderate depth or multi-step thinking
- high: complex, nuanced, or expert-level tasks"""

        try:
            # Use a cheap model for classification
            # Try gemini-2.5-flash or fall back to gpt-3.5-turbo
            print(f"Classifying prompt with gemini-2.5-flash...")
            response = await self.client.post(
                self.endpoint,
                json={
                    "model": "gemini-2.5-flash",
                    "input": classification_prompt,
                    "temperature": 0.3,
                    "max_output_tokens": 150
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract text from Concentrate's response format
            # Different models may have slightly different response structures
            try:
                content_text = data["output"][0]["content"][0]["text"]
            except (KeyError, IndexError, TypeError):
                # Try alternative parsing
                content_text = None
                
                if "output" in data and isinstance(data["output"], list):
                    for item in data["output"]:
                        if isinstance(item, dict) and "content" in item:
                            content = item["content"]
                            if isinstance(content, list) and len(content) > 0:
                                first_content = content[0]
                                if isinstance(first_content, dict) and "text" in first_content:
                                    content_text = first_content["text"]
                                    break
                
                if not content_text:
                    raise ValueError("Unable to parse classification response")
            
            # Parse the structured response
            lines = content_text.strip().split('\n')
            
            task_type = None
            complexity = None
            reasoning = None
            
            for line in lines:
                if line.startswith("TASK_TYPE:"):
                    task_type = line.split(":", 1)[1].strip().lower()
                elif line.startswith("COMPLEXITY:"):
                    complexity = line.split(":", 1)[1].strip().lower()
                elif line.startswith("REASONING:"):
                    reasoning = line.split(":", 1)[1].strip()
            
            # Validate and return
            return PromptClassification(
                task_type=task_type,
                complexity=complexity,
                reasoning=reasoning or "Classification completed"
            )
            
        except httpx.HTTPStatusError as e:
            # Fallback classification
            return PromptClassification(
                task_type="reasoning",
                complexity="medium",
                reasoning="Classification fallback due to API error"
            )
        except Exception as e:
            # Fallback classification
            return PromptClassification(
                task_type="reasoning",
                complexity="medium",
                reasoning="Classification fallback due to error"
            )
    
    async def complete(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate completion using specified model through Concentrate.
        
        Available models (examples):
        - OpenAI: gpt-4, gpt-5.2, gpt-3.5-turbo
        - Anthropic: claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5
        - Google: gemini-2.5-pro, gemini-2.5-flash
        - Meta: llama-3-70b, llama-3-8b
        """
        try:
            request_data = {
                "model": model,
                "input": prompt,
                "temperature": temperature
            }
            
            if max_tokens:
                request_data["max_output_tokens"] = max_tokens
            
            
            response = await self.client.post(
                self.endpoint,
                json=request_data
            )
            response.raise_for_status()
            data = response.json()
            
            
            # Extract text from Concentrate's response format
            # Different models may have slightly different response structures
            try:
                # Standard format: {"output": [{"content": [{"text": "..."}]}]}
                return data["output"][0]["content"][0]["text"]
            except (KeyError, IndexError, TypeError) as e:
                # Try alternative parsing if standard format fails
                # Alternative 1: Direct text field
                if "text" in data:
                    return data["text"]
                
                # Alternative 2: Output is a list of text blocks
                if "output" in data and isinstance(data["output"], list):
                    for item in data["output"]:
                        if isinstance(item, dict):
                            # Check for text field
                            if "text" in item:
                                return item["text"]
                            # Check for content with type
                            if "content" in item:
                                content = item["content"]
                                if isinstance(content, list) and len(content) > 0:
                                    first_content = content[0]
                                    if isinstance(first_content, dict):
                                        if "text" in first_content:
                                            return first_content["text"]
                                        # Check for output_text type
                                        if first_content.get("type") == "output_text":
                                            return first_content.get("text", "")
                        elif isinstance(item, str):
                            return item
                
                # If all else fails
                raise RuntimeError(f"Unable to parse response structure from {model}")
            
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            error_detail = e.response.text
            
            # Handle specific error codes
            if status_code == 402:
                raise RuntimeError(f"Insufficient credits - please add funds to your Concentrate account")
            elif status_code == 424:
                raise RuntimeError(f"Provider error with model {model} - the upstream provider may be unavailable")
            else:
                raise RuntimeError(f"API error {status_code} with model {model}: {error_detail}")
                
        except Exception as e:
            raise RuntimeError(f"Completion failed with model {model}: {str(e)}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()