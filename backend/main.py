# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import os
import logging
from uuid import uuid4
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold # <-- FIX: Import necessary types
from apscheduler.schedulers.background import BackgroundScheduler
from collections import defaultdict
import time

# ------------------ Logging ------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("chat_bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ------------------ Load env & init client ------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables! Put it in .env")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# ------------------ FastAPI setup ------------------
app = FastAPI(title="Customer Support Bot API")

# Rate limiting config
RATE_LIMIT_DURATION = 60
MAX_REQUESTS = 30
request_counts: Dict[str, List[float]] = defaultdict(list)

# Session timeout
SESSION_TIMEOUT = 3600 # 1 hour

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Data models ------------------
class Message(BaseModel):
    role: str
    content: str
    timestamp: str

class Session(BaseModel):
    session_id: str
    customer_name: Optional[str] = None
    created_at: str
    messages: List[Message] = []
    escalated: bool = False
    escalation_reason: Optional[str] = None
    last_activity: str # To track session activity for timeout

class QueryRequest(BaseModel):
    session_id: str
    customer_name: Optional[str] = None
    message: str

class EscalationRequest(BaseModel):
    session_id: str
    reason: str

# ------------------ FAQ DB ------------------
FAQS = {
    "shipping": [
        {"q": "How long does shipping take?", "a": "Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days."},
        {"q": "What are shipping costs?", "a": "Shipping costs depend on location: USA $5, International $15. Free shipping on orders over $50."},
        {"q": "Do you offer international shipping?", "a": "Yes, we ship to 150+ countries. International shipping takes 10-15 business days."}
    ],
    "returns": [
        {"q": "What is your return policy?", "a": "We offer 30-day returns on unused items with original packaging. Refunds processed within 5-7 business days."},
        {"q": "How do I initiate a return?", "a": "Log into your account, go to Orders, select the item, and click 'Return Item'. Print the label and ship it back."},
        {"q": "Do you accept returns after 30 days?", "a": "We accept returns up to 60 days with a 15% restocking fee for used items."}
    ],
    "products": [
        {"q": "Are your products in stock?", "a": "Check product pages for real-time stock availability. Items show 'In Stock' or estimated delivery dates."},
        {"q": "Do you have a size guide?", "a": "Yes, each product page has a detailed size guide. Click on the 'Size Chart' tab."},
        {"q": "Can I pre-order items?", "a": "Yes, pre-order items are available. They ship within 2 weeks of availability."}
    ],
    "payment": [
        {"q": "What payment methods do you accept?", "a": "We accept credit cards (Visa, Mastercard, Amex), PayPal, Apple Pay, and Google Pay."},
        {"q": "Is my payment information secure?", "a": "Yes, we use 256-bit SSL encryption and comply with PCI DSS standards."},
        {"q": "Can I use multiple payment methods?", "a": "You can use one payment method per order, but can split payments across multiple orders."}
    ],
    "account": [
        {"q": "How do I reset my password?", "a": "Click 'Forgot Password' on the login page, enter your email, and follow the instructions sent to your inbox."},
        {"q": "How do I update my profile?", "a": "Go to Account Settings > Profile and update your information. Click 'Save Changes' when done."},
        {"q": "Can I delete my account?", "a": "Yes, go to Account Settings > Privacy and click 'Delete Account'. This action cannot be undone."}
    ]
}

# ------------------ Session storage & cleanup ------------------
sessions_db: dict[str, Session] = {}

def cleanup_expired_sessions():
    now = datetime.now()
    expired = [
        sid for sid, s in sessions_db.items()
        if (now - datetime.fromisoformat(s.last_activity)).total_seconds() > SESSION_TIMEOUT
    ]
    for sid in expired:
        logger.info(f"Cleaning up expired session {sid}")
        del sessions_db[sid]

scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_expired_sessions, "interval", minutes=15)
scheduler.start()

# ------------------ Helpers ------------------
def create_faq_context() -> str:
    ctx = "# FAQ Database\n\n"
    for cat, items in FAQS.items():
        ctx += f"## {cat.upper()}\n"
        for it in items:
            ctx += f"- Q: {it['q']}\n  A: {it['a']}\n"
        ctx += "\n"
    return ctx

def get_system_prompt_content() -> str:
    faq_context = create_faq_context()
    return (
        "You are a professional, empathetic customer support assistant for an e-commerce company.\n\n"
        f"{faq_context}\n"
        "INSTRUCTIONS:\n"
        "1. Answer questions using the FAQ database when applicable.\n"
        "2. Be helpful, professional, and concise (max 2-3 sentences).\n"
        "3. If you cannot answer from FAQs, acknowledge and suggest escalation.\n"
        "4. Track context from previous messages in the conversation.\n"
        "5. If a customer seems frustrated or has a complex issue, recommend escalation to human support.\n"
        "6. Always be honest - never make up information.\n\n"
        "ESCALATION TRIGGERS:\n"
        "- Complex technical issues\n"
        "- Account security concerns\n"
        "- Billing disputes\n"
        "- Customer frustration or anger\n"
        "- Issues not covered in FAQs after 2 attempts\n"
        "Strictly adhere to these instructions. Start by greeting the user politely."
    )

def call_gemini_api(messages: List[Message], session_id: str) -> str:
    """
    Calls the Gemini API with the correct model name, chat history,
    and safety settings to prevent unnecessary blocking.
    """
    # Use a valid model from your available list
    model = genai.GenerativeModel("gemini-2.5-flash")

    gemini_history = []
    gemini_history.append({"role": "user", "parts": [get_system_prompt_content()]})
    # The first 'model' turn is an acknowledgement to set the context
    gemini_history.append({"role": "model", "parts": ["Understood. I am ready to assist customers."]})

    for msg in messages[:-1]:
        role = "user" if msg.role == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg.content]})

    chat = model.start_chat(history=gemini_history)
    latest_user_message = messages[-1].content
    
    try:
        response = chat.send_message(
            latest_user_message,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=300,
                top_p=0.8,
            ),
            # --- FIX: ADDED SAFETY SETTINGS TO PREVENT BLOCKING ON HARMLESS PROMPTS ---
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        # --- FIX: ADDED ROBUST HANDLING FOR BLOCKED RESPONSES ---
        text = None
        try:
            text = response.text
        except ValueError:
            # This occurs when the response is blocked by safety filters despite the settings.
            logger.warning(f"Response blocked by safety filters for session {session_id}.")
            logger.warning(f"Prompt Feedback: {response.prompt_feedback}")
            return "I'm sorry, I cannot respond to that due to safety guidelines. Could you please rephrase?"

        if not text:
            logger.warning(f"Empty response generated for session {session_id}")
            return "I apologize, I couldn't generate a response. Could you rephrase?"
        
        logger.info(f"✅ Generated response for session {session_id}")
        return text
        
    except Exception as e:
        logger.error(f"❌ Error in Gemini API call for session {session_id}: {e}", exc_info=True)
        return "I apologize, but I'm having trouble processing your request right now. A human agent will assist you shortly."

def check_escalation_needed(message: str, session: Session) -> bool:
    escalation_keywords = [
        "frustrated", "angry", "complaint", "manager", "supervisor",
        "urgent", "emergency", "security", "hacked", "billing error",
        "refund not received", "damaged product", "wrong item", "escalate"
    ]
    message_lower = message.lower()
    if any(k in message_lower for k in escalation_keywords):
        logger.info(f"Escalation triggered by keyword for session {session.session_id}")
        return True
    
    if len(session.messages) >= 3:
        user_messages_timestamps = [
            datetime.fromisoformat(msg.timestamp) for msg in session.messages if msg.role == "user"
        ]
        if len(user_messages_timestamps) >= 3:
            last_three_user_times = user_messages_timestamps[-3:]
            if (last_three_user_times[-1] - last_three_user_times[0]).total_seconds() < 45:
                logger.info(f"Escalation triggered by rapid consecutive messages for session {session.session_id}")
                return True
    return False

# ------------------ Middleware & error handler ------------------
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = time.time()
    
    request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < RATE_LIMIT_DURATION]
    
    if len(request_counts[client_ip]) >= MAX_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        return JSONResponse(status_code=429, content={"error": "Too many requests", "message": f"Please wait {RATE_LIMIT_DURATION} seconds before making more requests"})
    
    request_counts[client_ip].append(now)
    response = await call_next(request)
    return response

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error processing request: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "Internal server error", "message": str(exc)})

# ------------------ Endpoints ------------------
@app.get("/")
def read_root():
    return {"message": "Customer Support Bot API", "version": "1.1"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/chat/new-session")
def new_session(customer_name: Optional[str] = None):
    session_id = str(uuid4())
    now_iso = datetime.now().isoformat()
    session = Session(session_id=session_id, customer_name=customer_name, created_at=now_iso, last_activity=now_iso, messages=[])
    sessions_db[session_id] = session
    logger.info(f"New session created: {session_id} for {customer_name}")
    
    initial_bot_message = "Hello! How can I help you today?"
    session.messages.append(Message(role="assistant", content=initial_bot_message, timestamp=now_iso))
    
    return {"session_id": session_id, "message": initial_bot_message}

@app.post("/chat/query")
def process_query(request: QueryRequest):
    now_iso = datetime.now().isoformat()
    
    if request.session_id not in sessions_db:
        logger.warning(f"Session {request.session_id} not found. Creating new one.")
        sessions_db[request.session_id] = Session(
            session_id=request.session_id, 
            customer_name=request.customer_name, 
            created_at=now_iso, 
            last_activity=now_iso,
            messages=[]
        )
        sessions_db[request.session_id].messages.append(Message(role="assistant", content="Hello! How can I help you today?", timestamp=now_iso))

    session = sessions_db[request.session_id]
    session.last_activity = now_iso

    if request.customer_name and not session.customer_name:
        session.customer_name = request.customer_name
        logger.info(f"Updated customer name for session {session.session_id} to {session.customer_name}")

    if session.escalated:
        logger.info(f"Query for escalated session {request.session_id}. Returning escalation message.")
        return {
            "session_id": request.session_id,
            "escalated": True,
            "response": "This session has been escalated. A human agent will be with you shortly.",
            "escalation_reason": session.escalation_reason
        }

    user_message_obj = Message(role="user", content=request.message, timestamp=now_iso)
    session.messages.append(user_message_obj)
    logger.info(f"User message added to session {request.session_id}: {request.message}")

    if check_escalation_needed(request.message, session):
        session.escalated = True
        session.escalation_reason = "Complex issue or user frustration detected."
        logger.warning(f"Session {request.session_id} escalated due to: {session.escalation_reason}")
        return {
            "session_id": request.session_id,
            "escalated": True,
            "response": "It sounds like this may require human support. I am connecting you to a specialist now.",
            "escalation_reason": session.escalation_reason
        }

    ai_response = call_gemini_api(session.messages, request.session_id)
    session.messages.append(Message(role="assistant", content=ai_response, timestamp=now_iso))
    logger.info(f"AI response for session {request.session_id}: {ai_response}")

    return {"session_id": request.session_id, "response": ai_response, "escalated": False, "message_count": len(session.messages)}

@app.get("/chat/session/{session_id}")
def get_session(session_id: str):
    if session_id not in sessions_db:
        logger.warning(f"Attempted to retrieve non-existent session: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions_db[session_id].last_activity = datetime.now().isoformat()
    return sessions_db[session_id]

@app.post("/chat/escalate")
def escalate_issue(request: EscalationRequest):
    if request.session_id not in sessions_db:
        logger.warning(f"Attempted to escalate non-existent session: {request.session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    session = sessions_db[request.session_id]
    session.escalated = True
    session.escalation_reason = request.reason
    session.last_activity = datetime.now().isoformat()
    logger.warning(f"Session {request.session_id} manually escalated with reason: {request.reason}")
    return {"session_id": request.session_id, "status": "escalated", "message": "Your issue has been escalated to support."}

@app.get("/faqs")
def get_all_faqs():
    return FAQS

@app.get("/faqs/{category}")
def get_category_faqs(category: str):
    if category not in FAQS:
        raise HTTPException(status_code=404, detail="Category not found")
    return {category: FAQS[category]}
