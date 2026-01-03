# ============================================================================
# TESTING (Optional - for standalone testing)
# ============================================================================
if __name__ == "__main__":
    """Test the agent standalone"""
    import asyncio
    
    # Mock medicine for testing
    class MockMedicine:
        def __init__(self, name, dosage, count, expiration_date):
            self.name = name
            self.dosage = dosage
            self.count = count
            self.expiration_date = expiration_date
    
    async def test_agent():
        print("\n" + "="*60)
        print("TESTING MINA AGENT")
        print("="*60 + "\n")
        
        agent = MinaAgent()
        
        if not agent.llm:
            print("❌ Cannot test: HF_TOKEN not configured")
            print("Please create backend/.env with:")
            print("HF_TOKEN=your_huggingface_token")
            return
        
        test_inventory = [
            MockMedicine("Aspirin", "500mg", 20, "2026-12-31"),
            MockMedicine("Ibuprofen", "200mg", 30, "2025-08-15")
        ]
        
        # Test case 1
        print("\n📝 Test Case 1: Headache")
        result = await agent.chat("I have a headache", test_inventory)
        print("\n" + "="*60)
        print("TEST RESULT:")
        print("="*60)
        print(f"Reply: {result['reply']}")
        print(f"Sources: {result['sources']}")
        print(f"Timestamp: {result['timestamp']}")
        
        # Test case 2
        print("\n\n📝 Test Case 2: Fever")
        result2 = await agent.chat("I have a fever and feel tired", test_inventory)
        print("\n" + "="*60)
        print("TEST RESULT:")
        print("="*60)
        print(f"Reply: {result2['reply']}")
        print(f"Sources: {result2['sources']}")
        
        print("\n✅ Testing complete!\n")
    
    asyncio.run(test_agent())