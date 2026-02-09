"""
Model selection router with rule-based heuristics.

Core routing philosophy:
1. Task type determines model capability needs
2. Complexity determines model tier
3. User preference acts as final tie-breaker/optimizer
"""
from models import PromptClassification, TaskType, Complexity, UserPreference


# Model inventory organized by tier
# Based on actual Concentrate API models and pricing
# Optimized for cost, quality, and latency trade-offs
MODEL_TIERS = {
    "premium": {
        "cost": "claude-opus-4-5",           
        "quality": "gpt-5.2",              
        "latency": "claude-sonnet-4-5"
    },
    "standard": {
        "cost": "gpt-4o-mini",               
        "quality": "claude-sonnet-4-5",      
        "latency": "gpt-5-nano"              
    },
    "economy": {
        "cost": "ibm-granite-micro",         
        "quality": "claude-haiku-4-5",       
        "latency": "gemini-2.5-flash"        
    }
}


class ModelRouter:
    """
    Selects the optimal model based on classification and user preference.
    
    Design: Rule-based rather than ML-based for predictability and debuggability.
    """
    
    def select_model(
        self,
        classification: PromptClassification,
        preference: UserPreference
    ) -> tuple[str, str]:
        """
        Select model and generate human-readable routing explanation.
        
        Returns:
            (model_name, routing_reason)
        
        Routing strategy:
        1. Determine tier from complexity + task type
        2. Select model variant based on user preference
        3. Generate explanation for transparency
        """
        # Step 1: Determine base tier
        tier = self._determine_tier(classification)
        
        # Step 2: Apply task-specific overrides
        tier = self._apply_task_overrides(tier, classification.task_type)
        
        # Step 3: Select model variant based on preference
        model = MODEL_TIERS[tier][preference.value]
        
        # Step 4: Generate explanation
        reason = self._generate_routing_reason(
            tier, model, classification, preference
        )
        
        return model, reason
    
    def _determine_tier(self, classification: PromptClassification) -> str:
        """
        Map complexity to model tier.
        
        Heuristic: Complexity is the primary driver of model capability needs.
        """
        complexity_to_tier = {
            Complexity.LOW: "economy",
            Complexity.MEDIUM: "standard",
            Complexity.HIGH: "premium"
        }
        return complexity_to_tier[classification.complexity]
    
    def _apply_task_overrides(self, base_tier: str, task_type: TaskType) -> str:
        """
        Apply task-specific adjustments to tier selection.
        
        """
        # Coding tasks: bump up one tier (unless already premium)
        if task_type == TaskType.CODING and base_tier == "economy":
            return "standard"
        
        # High-stakes reasoning: ensure at least standard tier
        if task_type == TaskType.REASONING and base_tier == "economy":
            return "standard"
        
        # Summarization: can downgrade from premium to standard for cost savings
        if task_type == TaskType.SUMMARIZATION and base_tier == "premium":
            return "standard"
        
        return base_tier
    
    def _generate_routing_reason(
        self,
        tier: str,
        model: str,
        classification: PromptClassification,
        preference: UserPreference
    ) -> str:
        """
        Generate human-readable explanation of routing decision.
        
        Transparency is key: users should understand why they got a specific model.
        """
        reason_parts = [
            f"Selected {tier} tier model ({model})",
            f"based on {classification.task_type.value} task",
            f"with {classification.complexity.value} complexity,",
            f"optimized for {preference.value}"
        ]
        
        # Add classification reasoning as context
        if classification.reasoning:
            reason_parts.append(f"[{classification.reasoning}]")
        
        return " ".join(reason_parts)