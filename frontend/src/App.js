import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import "./App.css";

const QUICK_REPLIES = ["Book appointment", "Check availability", "Our services"];

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hello! I'm your dental scheduling assistant. I can help you book appointments, check availability, or answer questions about our services.",
      time: getTime(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  function getTime() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const formatResponse = (text) => {
  const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);

  // Converts **text** to <strong>text</strong> anywhere in a string
  const parseBold = (str) =>
    str.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  return lines.map((line, idx) => {
    // Numbered list: "1. something"
    if (/^\d+\.\s/.test(line)) {
      const content = line.replace(/^\d+\.\s/, "");
      return (
        <div key={idx} className="line list-item numbered">
          <span className="list-marker">{line.match(/^\d+/)[0]}.</span>
          <span dangerouslySetInnerHTML={{ __html: parseBold(content) }} />
        </div>
      );
    }
    // Bullet list: "- something" or "• something"
    if (/^[-•*]\s/.test(line)) {
      const content = line.replace(/^[-•*]\s/, "");
      return (
        <div key={idx} className="line list-item">
          <span className="list-marker">•</span>
          <span dangerouslySetInnerHTML={{ __html: parseBold(content) }} />
        </div>
      );
    }
    // Any other line — parse bold inline
    return (
      <div
        key={idx}
        className="line"
        dangerouslySetInnerHTML={{ __html: parseBold(line) }}
      />
    );
  });
};

  const sendMessage = async (text = input) => {
    if (!text.trim()) return;
    const newMessages = [...messages, { role: "user", text, time: getTime() }];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", { message: text });
      setMessages([...newMessages, { role: "assistant", text: res.data.reply, time: getTime() }]);
    } catch {
      setMessages([
        ...newMessages,
        { role: "assistant", text: "Sorry, I couldn't connect to the server. Please try again.", time: getTime() },
      ]);
    }
    setLoading(false);
  };

  return (
    <div className="app">
      <div className="header">
        <div className="logo">🦷</div>
        <div className="header-text">
          <h1>DentAI Scheduler</h1>
          <p>AI-powered appointment assistant</p>
        </div>
        <div className="status-dot" title="Online" />
      </div>

      <div className="chat-box">
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              className={`msg-row ${msg.role === "user" ? "user" : ""}`}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
            >
              <div className={`avatar ${msg.role === "user" ? "user" : "ai"}`}>
                {msg.role === "user" ? "You" : "AI"}
              </div>
              <div>
                <div className={`bubble ${msg.role === "user" ? "user" : "ai"}`}>
                  {msg.role === "assistant" ? formatResponse(msg.text) : msg.text}
                </div>
                <div className="msg-time">{msg.time}</div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {messages.length === 1 && (
          <div className="chip-row">
            {QUICK_REPLIES.map((q) => (
              <span key={q} className="chip" onClick={() => sendMessage(q)}>
                {q}
              </span>
            ))}
          </div>
        )}

        {loading && (
          <motion.div className="msg-row" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="avatar ai">AI</div>
            <div className="typing-bubble">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </motion.div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="input-area">
        <div className="input-wrap">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask about appointments..."
            autoFocus
          />
          <button className="send-btn" onClick={() => sendMessage()} title="Send">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
        <p className="input-hint">Press Enter to send</p>
      </div>
    </div>
  );
}

export default App;