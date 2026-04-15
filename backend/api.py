import sys
import os

sys.path.append(os.getcwd())

from fastapi import FastAPI
from pydantic import BaseModel
from dental_agent.agent import dental_graph

from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="DentAI Scheduler API 🦷")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 In-memory chat history
chat_history = []

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def home():
    return {"message": "🦷 DentAI Scheduler API is running!"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        global chat_history

        # ✅ Add user message to history
        chat_history.append({
            "role": "user",
            "content": req.message
        })

        # 🔥 Send full conversation to agent
        response = dental_graph.invoke({
            "messages": chat_history
        })

        # ✅ Extract reply safely
        reply = response.get("final_response")

        if not reply:
            messages = response.get("messages", [])
            if messages:
                last_msg = messages[-1]
                reply = getattr(last_msg, "content", str(last_msg))
            else:
                reply = "🤖 Working on your request..."

        # ✅ Add AI reply to history
        chat_history.append({
            "role": "assistant",
            "content": reply
        })

        return {"reply": reply}

    except Exception as e:
        return {"reply": f"❌ Error: {str(e)}"}