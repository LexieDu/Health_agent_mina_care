import os, re
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

from service import symptoms_mapping

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
    otc_candidates: list


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
                    repo_id="Qwen/Qwen2.5-Coder-32B-Instruct",
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
                f"- name: {med.name}; dosage_form: {med.dosage}; count: {med.count}; expires: {med.expiration_date}"
                for med in inventory
            ])

        return f"""You are Mina, a caring health assistant for the MinaCare app.

    User's current medicine inventory:
    {inventory_context}

    Your responsibilities (follow in order):
    1. Listen to the user's symptoms with empathy and acknowledge how they are feeling.
    2. Identify which OTC medicine(s) are typically recommended to help relieve these symptoms
    (be specific and symptom-appropriate; do NOT always default to aspirin or ibuprofen).
    3. Check whether the recommended medicine(s) exist in the user's inventory
    (match by generic or well-known brand names if applicable).
        3.1 If the user HAS a recommended medicine:
        - Suggest a typical OTC adult dose and frequency, only if safe and appropriate.
        3.2 If the user DOES NOT have a recommended medicine:
        - Clearly state what medicine they could buy and what it helps with.
        3.3 If there are important safety considerations (e.g. pregnancy, kidney/liver disease, stomach ulcers, allergies, or medication interactions):
        - Clearly state who should NOT take the medicine or should use extra caution.
    4. Provide general health advice and self-care suggestions related to the symptom.
    5. Always recommend seeing a doctor for serious, persistent, or worsening symptoms.

    Style guidelines:
    - Be warm, caring, and helpful.
    - Use emojis sparingly (at least one for each sentence).
    - Always prioritize user safety.
    - Keep the response under 300 words.
    
    Output format rules (strict):
    - Use ONLY bullet points start with emoji or numbered lists.
    - Do NOT write long paragraphs.
    - Each bullet should be concise (1–2 short sentences max).
    - Group bullets under clear section headers if helpful.
    """

    
    # ========================================================================
    # GRAPH NODES (Steps in the workflow)
    # ========================================================================
    
    def process_input(self, state: AgentState) -> AgentState:
        """Node 1: Process user input"""
        print("🔄 Node 1: Processing input...")
        # Input is already in state, just pass through
        return state
    
    def search_otc_candidates(self, state: AgentState) -> AgentState:
        """
        Node 2: Local 'search' (mapping lookup) for OTC candidates + tips.
        Later we can swap this to real web search without changing Step 3 logic.
        """
        print("🔍 Node 2: Gathering information (local OTC mapping)...")

        user_input = state.get("user_input", "") or ""
        mapping = symptoms_mapping.local_otc_mapping(user_input)

        # Store structured candidates for Step 3
        state["otc_candidates"] = mapping.get("medicines", [])

        # Keep extra info in case you want it later for formatting
        state["web_search_results"] = {
            "self_care": mapping.get("self_care", []),
            "red_flags": mapping.get("red_flags", []),
        }

        # Sources: tell downstream this came from local mapping
        state["sources"] = ["Local OTC mapping v1"]

        return state
    
    def analyze_and_recommend(self, state: AgentState) -> AgentState:
        """Node 3: Recommend symptom-appropriate OTC meds, then check inventory, then dose/buy."""
        print("🧠 Node 3: Analyzing and recommending...")

        if not self.llm:
            state["recommendation"] = "⚠️ AI is not configured. Please set HF_TOKEN in .env file."
            return state

        try:
            # Build system prompt (already updated to enforce logic + bullets)
            system_prompt = self._build_system_prompt(state["medicines_inventory"])

            user_symptom = state.get("user_input", "") or ""

            # From Node 2 (local OTC mapping)
            otc_candidates = state.get("otc_candidates", []) or []

            # Extra tips/red flags from Node 2 (stored in web_search_results dict)
            ws = state.get("web_search_results", {}) or {}
            self_care = ws.get("self_care", []) if isinstance(ws, dict) else []
            red_flags = ws.get("red_flags", []) if isinstance(ws, dict) else []

            # Prepare inventory list in compact form (avoid long prose)
            inventory = state.get("medicines_inventory", []) or []
            inv_lines = []
            for med in inventory:
                inv_lines.append(
                    f"- name: {getattr(med, 'name', '')}; dosage_form: {getattr(med, 'dosage', '')}; "
                    f"count: {getattr(med, 'count', '')}; expires: {getattr(med, 'expiration_date', '')}"
                )
            inventory_text = "\n".join(inv_lines) if inv_lines else "No medicines in inventory."

            # STRICT output contract — this is what fixes the “one big blob”
            user_prompt = f"""
    User’s symptom:
    - {user_symptom}

    Recommended OTC candidates for this symptom (from local mapping):
    {otc_candidates}

    User inventory:
    {inventory_text}

    Self-care suggestions (from local mapping):
    {self_care}

    Red flags (from local mapping):
    {red_flags}

    TASK (follow exactly, no deviation):
    1) Start with an empathy acknowledgment (1–2 bullets).
    2) Decide which 1–2 medicines from "Recommended OTC candidates" best fit the symptom.
    3) Inventory check:
    - If the user has the recommended medicine(s), list them under "You have".
    - If not, list them under "You do NOT have (buy)".
    4) Dose:
    - ONLY provide dosing for medicines that are in the inventory AND not expired (assume adult typical OTC dosing).
    - If a medicine is not in inventory, do NOT give a dose—put it under "What to buy" instead.
    5) Add specific self-care tips and red flags (use the provided lists; do not invent new ones).

    Style guidelines:
    - Be warm, caring, and helpful.
    - Use emojis sparingly (at least one for each sentence).
    - Always prioritize user safety.
    - Keep the response under 300 words.
    
    Formatting rules (STRICT):
    - Each section header must be on its own line, followed by NEWLINE.
    - Each bullet must be on its own line starting with "- ".
    - Do NOT put multiple headers on the same line.
    - Use blank line between sections.
    - Do NOT use markdown bold (**).

    Acknowledgment:
    - ...

    Recommended medicines for your symptom:
    - <medicine>: <purpose>

    Inventory check:
    - You have: ...
    - You do NOT have (buy): ...

    Dose (ONLY for "You have"):
    - <medicine>: <dose + frequency + max daily (if known)>

    What to buy (ONLY if "You have" is empty):
    - <medicine>: <what it helps with>

    Other specific suggestions:
    - ...
    - ...

    When to see a doctor:
    - ...
    - ...

    Word limit: under 300 words. Each bullet start with a emoji.
    """

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]

            print("   Waiting for AI response...")
            response = self.llm.invoke(messages)

            state["recommendation"] = response.content
            print("   ✓ Response received")

            #####
            print(response.content)

        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
            state["recommendation"] = "I'm having trouble analyzing right now. Please try again in a moment. 💙"

        return state

    
    def generate_response(self, state: AgentState) -> AgentState:
        """Node 4: Finalize and enforce readable section formatting."""
        print("✅ Node 4: Finalizing response...")

        rec = (state.get("recommendation") or "").strip()
        if not rec:
            state["recommendation"] = "Acknowledgment:\n- I'm here to help. 💙"
            return state

        # Force headers onto their own lines (fix "bulk one-liner")
        headers = [
            "Acknowledgment:",
            "Recommended medicines for your symptom:",
            "Inventory check:",
            "Dose (ONLY for \"You have\"):",
            "What to buy (ONLY if \"You do NOT have\" is not empty):",
            "Other specific suggestions:",
            "When to see a doctor:",
        ]

        # Ensure each header starts on a new line
        for h in headers:
            rec = rec.replace(f" {h}", f"\n\n{h}")
            rec = rec.replace(f"{h} -", f"{h}\n-")  # if model did "Header: - bullet"

        # Ensure bullets are on separate lines when they appear after text
        rec = re.sub(r"\s-\s", "\n- ", rec)

        # Clean up triple newlines
        rec = re.sub(r"\n{3,}", "\n\n", rec).strip()

        state["recommendation"] = rec
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
        workflow.add_node("search_otc_candidates", self.search_otc_candidates)
        workflow.add_node("analyze_and_recommend", self.analyze_and_recommend)
        workflow.add_node("generate_response", self.generate_response)
        
        # Define edges (workflow flow)
        workflow.set_entry_point("process_input")
        workflow.add_edge("process_input", "search_otc_candidates")
        workflow.add_edge("search_otc_candidates", "analyze_and_recommend")
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
                "sources": [],
                "otc_candidates": []
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
