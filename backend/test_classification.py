"""
Diagnostic script to test Concentrate API classification.
Run this to see what's happening with the classification step.
"""
import asyncio
import sys
from concentrate_client import ConcentrateClient

async def test_classification():
    """Test the classification endpoint directly."""
    print("=" * 60)
    print("CONCENTRATE API CLASSIFICATION TEST")
    print("=" * 60)
    
    try:
        # Initialize client
        client = ConcentrateClient()
        
        # Test prompts
        test_prompts = [
            "what is 2+2",
            "Write a Python function to sort a list",
            "Summarize the history of France",
            "Write a creative story about a dragon"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n--- Test {i} ---")
            print(f"Prompt: {prompt}")
            
            classification = await client.classify_prompt(prompt)
            
            print(f"\n✅ Result:")
            print(f"   Task Type: {classification.task_type}")
            print(f"   Complexity: {classification.complexity}")
            print(f"   Reasoning: {classification.reasoning}")
        
        await client.close()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has CONCENTRATE_API_KEY")
        print("2. Verify your API key is valid at app.concentrate.ai")
        print("3. Check you have credits in your account")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_classification())