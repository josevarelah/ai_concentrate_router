"""
Prompt classification logic.

Uses a cheap model to analyze incoming prompts and categorize them
by task type and complexity.
"""
from models import PromptClassification
from concentrate_client import ConcentrateClient


class PromptClassifier:
    """
    Classifies prompts into task type and complexity.
    
    Design choice: Use LLM-based classification rather than heuristics.
    """
    
    def __init__(self, client: ConcentrateClient):
        self.client = client
    
    async def classify(self, prompt: str) -> PromptClassification:
        """
        Classify the prompt using Concentrate API.
        
        Delegates to the client which uses a cheap model for classification.
        This keeps the classifier focused on logic rather than API details.
        """
        return await self.client.classify_prompt(prompt)