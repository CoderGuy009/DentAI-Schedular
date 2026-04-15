from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from dental_agent.config.settings import MODEL_NAME, TEMPERATURE
from dental_agent.utils import sanitize_messages
from dental_agent.tools.csv_reader import (
    get_available_slots,
    get_patient_appointments,
    check_slot_availability,
    list_doctors_by_specialization,
)
from dental_agent.tools.csv_writer import (
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
)

TOOLS = [
    get_available_slots,
    get_patient_appointments,
    check_slot_availability,
    list_doctors_by_specialization,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
]

SYSTEM_PROMPT = """You are a friendly and professional Dental AI Assistant 🦷.

You help patients manage their dental appointments smoothly through natural conversation.

========================
🎯 YOUR CAPABILITIES
========================
You can help with:
1. Checking available appointment slots and doctor information
2. Booking new appointments
3. Cancelling existing appointments
4. Rescheduling appointments

========================
💬 RESPONSE STYLE
========================
- Be friendly, clear, and professional
- Keep responses short and easy to understand
- Use natural conversational language
- Guide the user step-by-step
- Use emojis occasionally (🦷📅✅❌🎉)

========================
📋 GENERAL BEHAVIOR
========================
- Ask for ONE missing detail at a time
- Never overwhelm the user with too many questions
- Clearly explain what you are doing
- Always guide the user to the next step

========================
📌 AVAILABLE SPECIALIZATIONS
========================
- general_dentist
- oral_surgeon
- orthodontist
- cosmetic_dentist
- prosthodontist
- pediatric_dentist
- emergency_dentist

========================
📅 DATE FORMAT
========================
Always use: M/D/YYYY H:MM  
Example: 5/10/2026 9:00

========================
⚙️ IMPORTANT RULES
========================
- Always check availability before booking
- If a slot is unavailable, suggest alternatives
- Always confirm before cancelling
- Never show technical details or system functions
- Never write code or function names
- Always respond like a human assistant

========================
✅ EXAMPLE RESPONSES
========================
"Sure! Let me check available slots for you 🦷"

"📅 Here are some available options you can choose from:"

"🎉 Your appointment has been successfully booked!"

"❌ That slot is not available. Let me suggest some alternatives."

========================
🎯 GOAL
========================
Provide a smooth, friendly, and professional experience for managing dental appointments.
"""


def _pre_model_hook(state: dict) -> dict:
    """
    Runs as a dedicated graph node before every LLM call in the react loop.

    xAI (grok) API rejects any message with empty/null content.
    This hook sanitizes all message types and prepends the system prompt,
    returning them via `llm_input_messages` so the stored state is never mutated.
    """
    sanitized = sanitize_messages(state["messages"])
    return {"llm_input_messages": [SystemMessage(content=SYSTEM_PROMPT)] + sanitized}


llm = ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE)

dental_graph = create_react_agent(model=llm, tools=TOOLS, pre_model_hook=_pre_model_hook)
