# 🤖 AI Customer Support Bot

An intelligent customer support chatbot built with **FastAPI**, **React**, and **Google Gemini API**. Features real-time messaging, FAQ management, automatic escalation, and full conversation context.

**[Live Demo](#quick-start)** • **[API Docs](#-api-endpoints)** • **[Setup Guide](#-setup)** • **[Customization](#-customization)**

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Responses** | Powered by Google Gemini API with custom prompts |
| 💬 **Chat Interface** | Real-time messaging with typing indicators |
| 📚 **FAQ Database** | 6 categories with 18 pre-loaded Q&As |
| 🧠 **Context Aware** | Remembers full conversation history |
| 🚨 **Smart Escalation** | Auto-detects frustrated customers & complex issues |
| 📱 **Responsive UI** | Works perfectly on desktop and mobile |
| 🔐 **Session Management** | Unique sessions with full message tracking |

---

## 🛠️ Tech Stack

```
Backend:   FastAPI (Python) + Uvicorn
Frontend:  React 18 + CSS3 Animations
AI:        Google Gemini API
Storage:   In-Memory (upgradeable to PostgreSQL/MongoDB)
Deploy:    Docker-ready
```

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- Node.js 14+
- Gemini API Key (get free at https://ai.google.dev/)

### Installation

**1. Clone & Navigate**
```bash
git clone <your-repo>
cd customer-support-bot
```

**2. Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Add API Key**
```bash
# Create backend/.env file
echo "GEMINI_API_KEY=your_key_here" > .env
```

**4. Start Backend**
```bash
python -m uvicorn main:app --reload --port 8000
# Visit: http://localhost:8000/docs (interactive API docs)
```

**5. Frontend Setup (New Terminal)**
```bash
cd frontend
npm install
npm start
# Opens: http://localhost:3000
```

**6. Test It!**
- Enter your name
- Click "Start Chat"
- Ask: "What is your return policy?"
- Get an AI response! ✅

---

## 📡 API Endpoints

### Chat Operations

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/chat/new-session` | Create new chat session |
| `POST` | `/chat/query` | Send message & get response |
| `GET` | `/chat/session/{id}` | View conversation history |
| `POST` | `/chat/escalate` | Escalate to human support |

### FAQ & System

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/faqs` | Get all FAQs |
| `GET` | `/faqs/{category}` | Get FAQs by category |
| `GET` | `/health` | Health check |

**Example Request:**
```bash
curl -X POST http://localhost:8000/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "customer_name": "John",
    "message": "How long is shipping?"
  }'
```

---

## 📁 Project Structure

```
customer-support-bot/
├── backend/
│   ├── main.py              # FastAPI app (430+ lines)
│   ├── requirements.txt     # Python packages
│   └── .env                 # API key (you add this)
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # React component
│   │   ├── App.css          # Styling
│   │   └── index.js         # Entry point
│   ├── public/index.html    # HTML template
│   └── package.json         # Dependencies
├── README.md
└── PROMPTS.md               # LLM customization guide
```

---

## 🎨 Customization

### Change Bot Personality

**File:** `backend/main.py` → Find `get_system_prompt()`

```python
# Example: Make it friendly
return """You are a friendly and enthusiastic customer support assistant!
Always greet customers warmly and be helpful..."""

# Example: Make it professional
return """You are a professional customer service representative.
Provide accurate, concise, and courteous responses..."""
```

### Add FAQ Categories

**File:** `backend/main.py` → Update `FAQS` dictionary

```python
FAQS = {
    "shipping": [...],
    "returns": [...],
    "your_category": [
        {"q": "Question 1?", "a": "Answer 1"},
        {"q": "Question 2?", "a": "Answer 2"},
    ]
}
```

### Customize Escalation Triggers

**File:** `backend/main.py` → Function `check_escalation_needed()`

```python
escalation_keywords = [
    "frustrated", "angry", "complaint",  # existing
    "your_keyword", "another_keyword"    # add more
]
```

### Change UI Colors

**File:** `frontend/src/App.css` → `:root` variables

```css
:root {
  --primary: #6366f1;        /* Main brand color */
  --secondary: #10b981;      /* Success color */
  --warning: #f59e0b;        /* Escalate button */
  --text: #1e293b;           /* Text color */
  --bg: #f8fafc;             /* Background */
}
```

---

## 🧪 Testing

### Test the API

```bash
# 1. Create session
curl -X POST http://localhost:8000/chat/new-session \
  -H "Content-Type: application/json" \
  -d '{"customer_name":"Test"}'

# 2. Copy session_id from response, then:
curl -X POST http://localhost:8000/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"YOUR_SESSION_ID",
    "customer_name":"Test",
    "message":"What is your return policy?"
  }'

# 3. Check FAQs
curl http://localhost:8000/faqs
```

### Test in Browser

1. Open http://localhost:3000
2. **Test FAQ Query**: "How long does shipping take?"
3. **Test Context**: Follow-up with "What about international?"
4. **Test Escalation**: Type "I'm very frustrated!"
5. **Test Out-of-Scope**: Ask "What's the weather?"

---

##  Troubleshooting

| Issue | Solution |
|-------|----------|
| **Backend won't start** | Check Python 3.8+, run `pip install --force-reinstall -r requirements.txt` |
| **Frontend won't start** | Run `npm cache clean --force && rm -rf node_modules && npm install` |
| **CORS error** | Ensure backend running on 8000, clear browser cache (Ctrl+Shift+Del) |
| **API key error** | Check `.env` file exists in `backend/`, verify key has no quotes |
| **Port 8000 in use** | Use: `python -m uvicorn main:app --port 8001` |

---

##  Deployment

### Deploy Backend (Heroku)

```bash
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
echo "python-3.11.0" > runtime.txt

# Deploy
heroku login
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your_key
git push heroku main
```

### Deploy Frontend (Vercel)

```bash
npm install -g vercel
vercel login
vercel
# Set REACT_APP_API_URL to your Heroku backend URL
```

---

##  How It Works

```
User Input
    ↓
React UI sends to API
    ↓
Backend checks for escalation keywords
    ↓ (escalation detected) → Return escalation message
    ↓ (normal query)
Backend builds system prompt + FAQ context
    ↓
Calls Gemini API with conversation history
    ↓
Gemini generates intelligent response
    ↓
Backend saves to session storage
    ↓
Returns response to frontend
    ↓
React displays with animations ✨
```

---

## 🔐 Security

- ✅ API key stored in `.env` (never committed)
- ✅ Input validation with Pydantic
- ✅ CORS enabled (configure for production)
- ✅ No sensitive data in error messages
- ✅ Session isolation per customer

---

##  Documentation

- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Detailed step-by-step setup
- **[PROMPTS.md](./PROMPTS.md)** - LLM customization & prompt engineering
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Copy-paste file guide
- **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - Architecture & features

---

##  Performance Tips

- Keep FAQ answers concise (faster AI responses)
- Use `max_output_tokens: 300` to limit response length
- Deploy to CDN for faster frontend delivery
- Use production React build: `npm run build`
- Cache common questions on frontend

---

##  Learning Outcomes

By building this, you'll learn:

✅ **Backend**: REST APIs, session management, LLM integration  
✅ **Frontend**: React hooks, API communication, real-time UI  
✅ **Full-Stack**: Architecture, debugging, deployment  
✅ **AI/ML**: Prompt engineering, API integration, context management  
✅ **DevOps**: Environment variables, Docker, deployment platforms  

---

##  FAQ

**Q: Can I use a different AI model?**  
A: Yes! Replace the `call_gemini_api()` function with OpenAI, Claude, or any API.

**Q: How do I persist data?**  
A: See **[Upgrade to PostgreSQL/MongoDB](#-customization)** in PROMPTS.md

**Q: Can I deploy this?**  
A: Yes! See **[Deployment](#-deployment)** section above.

**Q: How do I modify the bot's behavior?**  
A: Edit the system prompt or FAQ database (see **[Customization](#-customization)**).

---

##  License

MIT License - Free to use, modify, and distribute

---

## What's Next?

1. ✅ Run the bot locally
2. ✅ Test all features
3. ✅ Customize for your needs
4. ✅ Record a demo video
5. ✅ Deploy to production
6. ✅ Share with the world!

---

## 📞 Support

- 💬 Check the docs above
- 🐛 See troubleshooting section
- 📖 Review SETUP_GUIDE.md
- 🔧 Check PROMPTS.md for customization

