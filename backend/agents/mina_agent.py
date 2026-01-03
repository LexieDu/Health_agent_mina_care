import os
from datetime import datetime
from typing import TypedDict, Sequence
from langchain_huggingface import HuggingFaceEndpoint
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langchain_huggingface import HuggingFaceEndpoint
from langchain_huggingface import ChatHuggingFace
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()


# ============================================================================
# STATE DEFINITION
# ============================================================================
class AgentState(TypedDict):
    """State of the Mina agent"""
    messages: Sequence[BaseMessage]
    user_input: str
    medicines_inventory: list
    web_search_results: str
    recommendation: str
    sources: list


# ============================================================================
# MINA AGENT CLASS
# ============================================================================
class MinaAgent:
    """
    Mina AI Agent using LangGraph
    Multi-step workflow: Input → Web Search → Analyze → Recommend → Respond
    """
    
    def __init__(self):
        """Initialize Mina agent with HuggingFace model"""
        self.api_key = os.getenv("HF_TOKEN", "")
        
        if not self.api_key:
            print("⚠️  Warning: HF_TOKEN not found in .env file")
            print("Please create backend/.env with: HF_TOKEN=your_token_here")
            self.llm = None
        else:
            try:
                # Initialize HuggingFace LLM
                hf_endpoint = HuggingFaceEndpoint(
                    repo_id="HuggingFaceH4/zephyr-7b-beta",
                    huggingfacehub_api_token=self.api_key,
                    temperature=0.7,
                    max_new_tokens=512,
                )

                # Chat wrapper (THIS makes it conversational)
                self.llm = ChatHuggingFace(llm=hf_endpoint)

                print("✅ HuggingFace model initialized successfully")
            except Exception as e:
                print(f"❌ Error initializing HuggingFace: {e}")
                self.llm = None
        
        # Build the agent graph
        self.graph = self._build_graph()
    
    def _build_system_prompt(self, inventory: list) -> str:
        """Build system prompt with user's medicine inventory"""
        if not inventory:
            inventory_context = "No medicines in inventory."
        else:
            inventory_context = "\n".join([
                f"- {med.name} ({med.dosage}), Count: {med.count}, Expires: {med.expiration_date}"
                for med in inventory
            ])
        
        return f"""You are Mina, a caring health assistant for the MinaCare app.

User's current medicine inventory:
{inventory_context}

Your role:
1. Listen to the user's symptoms with empathy
2. Suggest medicines from their inventory if applicable
3. Provide general health advice
4. Always recommend seeing a doctor for serious symptoms

Be warm, caring, and helpful. Use emojis to be friendly. Always prioritize user safety.
Keep your response under 200 words."""
    
    # ========================================================================
    # GRAPH NODES (Steps in the workflow)
    # ========================================================================
    
    def process_input(self, state: AgentState) -> AgentState:
        """Node 1: Process user input"""
        print("🔄 Node 1: Processing input...")
        # Input is already in state, just pass through
        return state
    
    def search_web(self, state: AgentState) -> AgentState:
        """Node 2: Simulate web search (real search can be added later)"""
        print("🔍 Node 2: Gathering information...")
        
        # For now, simulate web search
        # In production, you could integrate real web search APIs
        state["web_search_results"] = f"Medical information search for: {state['user_input']}"
        state["sources"] = ["Medical knowledge base"]
        
        return state
    
    def analyze_and_recommend(self, state: AgentState) -> AgentState:
        """Node 3: Analyze symptoms and recommend from inventory"""
        print("🧠 Node 3: Analyzing and recommending...")
        
        if not self.llm:
            state["recommendation"] = "⚠️ AI is not configured. Please set HF_TOKEN in .env file."
            return state
        
        try:
            # Build comprehensive prompt
            system_prompt = self._build_system_prompt(state["medicines_inventory"])
            
            user_prompt = f"""User's symptoms: {state['user_input']}

Please provide:
1. A caring response acknowledging their symptoms
2. Medicine recommendations from their inventory (if applicable)
3. General health advice
4. Whether they should see a doctor

Be empathetic and use emojis. Keep it concise."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]

            print("   Waiting for AI response...")
            response = self.llm.invoke(messages)

            state["recommendation"] = response.content
            print("   ✓ Response received")
            
        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
            state["recommendation"] = "I'm having trouble analyzing right now. Please try again in a moment. 💙"
        
        return state
    
    def generate_response(self, state: AgentState) -> AgentState:
        """Node 4: Generate final response"""
        print("✅ Node 4: Finalizing response...")
        
        # Ensure we have a recommendation
        if not state.get("recommendation") or state["recommendation"].strip() == "":
            state["recommendation"] = "I'm here to help! Could you tell me more about how you're feeling? 💙"
        
        return state
    
    # ========================================================================
    # GRAPH BUILDING
    # ========================================================================
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("process_input", self.process_input)
        workflow.add_node("search_web", self.search_web)
        workflow.add_node("analyze_and_recommend", self.analyze_and_recommend)
        workflow.add_node("generate_response", self.generate_response)
        
        # Define edges (workflow flow)
        workflow.set_entry_point("process_input")
        workflow.add_edge("process_input", "search_web")
        workflow.add_edge("search_web", "analyze_and_recommend")
        workflow.add_edge("analyze_and_recommend", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    # ========================================================================
    # MAIN CHAT INTERFACE
    # ========================================================================
    
    async def chat(self, user_message: str, medicines_inventory: list) -> dict:
        """
        Process user message through the LangGraph workflow
        
        Args:
            user_message: User's input message
            medicines_inventory: List of Medicine objects from user's inventory
            
        Returns:
            dict with 'reply', 'timestamp', and 'sources'
        """
        
        if not self.api_key:
            return {
                "reply": "⚠️ AI is not configured. Please set HF_TOKEN in .env file.",
                "timestamp": datetime.now().isoformat(),
                "sources": []
            }
        
        try:
            # Initialize state
            initial_state = {
                "messages": [],
                "user_input": user_message,
                "medicines_inventory": medicines_inventory,
                "web_search_results": "",
                "recommendation": "",
                "sources": []
            }
            
            # Run through the graph
            print(f"\n{'='*60}")
            print(f"🤖 Mina Agent Processing: {user_message}")
            print(f"{'='*60}")
            
            final_state = self.graph.invoke(initial_state)
            
            print(f"{'='*60}\n")
            
            return {
                "reply": final_state.get("recommendation", "I'm here to help! 💙"),
                "timestamp": datetime.now().isoformat(),
                "sources": final_state.get("sources", [])
            }
            
        except Exception as e:
            print(f"❌ Error in Mina agent: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "reply": "I'm having trouble connecting right now. Please try again in a moment. 💙",
                "timestamp": datetime.now().isoformat(),
                "sources": []
            }


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