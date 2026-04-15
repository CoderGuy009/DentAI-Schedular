from langchain_xai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dental_agent.config.settings import MODEL_NAME, TEMPERATURE
from dental_agent.models.state import AppointmentState, RouteTarget
from dental_agent.utils import sanitize_messages


class SupervisorDecision(BaseModel):
    """Routing decision produced by the supervisor."""
    intent: str = Field(
        description="Classified intent. One of: get_info, book, cancel, reschedule, unknown, end."
    )
    next_agent: RouteTarget = Field(
        description=(
            "The agent to route to. One of: info_agent, booking_agent, "
            "cancellation_agent, rescheduling_agent, end."
        )
    )
    reasoning: str = Field(description="Brief explanation of the routing decision.")


SUPERVISOR_SYSTEM = """You are an intelligent supervisor for a Dental AI Assistant 🦷.

Your ONLY job is to understand the user's intent and route the request to the correct agent.

========================
🎯 YOUR ROLE
========================
- Analyze the user's latest message carefully
- Identify the PRIMARY intent
- Route to the correct agent
- DO NOT respond to the user directly

========================
🔀 ROUTING RULES
========================
- get_info      → info_agent  
  (User is asking about availability, doctors, schedules, or general queries)

- book          → booking_agent  
  (User wants to create or schedule a NEW appointment)

- cancel        → cancellation_agent  
  (User wants to cancel an existing appointment)

- reschedule    → rescheduling_agent  
  (User wants to change/move an existing appointment)

- end           → end  
  (User says thanks, goodbye, or conversation is complete)

- unknown       → info_agent  
  (Unclear intent → default to info_agent)

========================
🧠 INTENT DETECTION HINTS
========================
- "book", "schedule", "appointment" → booking_agent  
- "cancel", "remove", "delete" → cancellation_agent  
- "reschedule", "change time", "move" → rescheduling_agent  
- "available", "slots", "doctors", "what", "which" → info_agent  
- "thanks", "ok", "bye", "done" → end  

========================
⚠️ IMPORTANT RULES
========================
- DO NOT answer the user
- DO NOT explain your reasoning
- ONLY return routing decision
- If multiple intents exist, choose the PRIMARY one
- If conversation is already complete → route to end

========================
📤 OUTPUT FORMAT (STRICT)
========================
Return ONLY valid JSON:

{
  "intent": "<intent_name>",
  "agent": "<agent_name>"
}
"""

SUPERVISOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", SUPERVISOR_SYSTEM),
    ("placeholder", "{messages}"),
])


def supervisor_node(state: AppointmentState) -> dict:
    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=TEMPERATURE,
    ).with_structured_output(SupervisorDecision)

    chain = SUPERVISOR_PROMPT | llm

    try:
        decision: SupervisorDecision = chain.invoke({
            "messages": sanitize_messages(state["messages"])
        })

        # ✅ Safe extraction
        intent = getattr(decision, "intent", "unknown")
        next_agent = getattr(decision, "next_agent", "info_agent")

        return {
            "intent": intent,
            "next_agent": next_agent,
        }

    except Exception as e:
        # ✅ Fallback to prevent crash
        print("Supervisor Error:", e)

        return {
            "intent": "unknown",
            "next_agent": "info_agent",
        }