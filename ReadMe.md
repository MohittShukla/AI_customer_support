# AI Customer Support Bot

A customer support chatbot built with FastAPI, React, and Google Gemini API. Features real-time messaging, FAQ management, conversation history, and intelligent escalation.

## Features

- AI-Powered Responses - Google Gemini API integration for intelligent replies
- Real-Time Chat - Responsive chat interface with live messaging
- FAQ Database - Pre-loaded FAQs organized by category
- Context Awareness - Maintains full conversation history for follow-ups
- Smart Escalation - Keyword-based system to detect frustration and escalate
- Session Management - Unique sessions per user with complete tracking

## Tech Stack

- Backend: FastAPI, Python 3.8+, Uvicorn
- Frontend: React 18, CSS3
- AI: Google Gemini API
- Storage: In-memory (upgradeable to database)

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Google Gemini API Key (get at https://ai.google.dev/)

## Installation

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Add API Key

Create a `.env` file in the backend directory:

```
GEMINI_API_KEY=your_key_here
```

### Start Backend Server

```bash
python -m uvicorn main:app --reload --port 8000
```

Access the interactive API documentation at http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The application will open at http://localhost:3000

## Running the Application

Once both frontend and backend are running:

1. Enter your name in the chat interface
2. Click "Start Chat"
3. Ask a question like "What is your return policy?"
4. Get an AI-generated response

## API Endpoints

### Chat Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /chat/new-session | Create a new chat session |
| POST | /chat/query | Send a message and get a response |
| GET | /chat/session/{id} | Retrieve conversation history |
| POST | /chat/escalate | Escalate to human support |

### FAQ and System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /faqs | Get all FAQs |
| GET | /faqs/{category} | Get FAQs for a specific category |
| GET | /health | Health check endpoint |

### Example Request

```bash
curl -X POST http://localhost:8000/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "customer_name": "John",
    "message": "How long is shipping?"
  }'
```

## Project Structure

```
customer-support-bot/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.js
│   ├── public/index.html
│   └── package.json
└── README.md
```

## Customization

### Change Bot Behavior

Edit the system prompt in `backend/main.py` in the `get_system_prompt()` function:

```python
return """You are a professional customer service representative.
Provide accurate, concise, and courteous responses."""
```

### Add New FAQ Categories

Edit the FAQS dictionary in `backend/main.py`:

```python
FAQS = {
    "shipping": [...],
    "new_category": [
        {"q": "Question?", "a": "Answer"},
        {"q": "Another question?", "a": "Another answer"},
    ]
}
```

### Modify UI Colors

Edit the CSS variables in `frontend/src/App.css`:

```css
:root {
  --primary: #6366f1;
  --secondary: #10b981;
  --text: #1e293b;
  --bg: #f8fafc;
}
```

## How It Works

1. User sends a message through the React frontend
2. The message is sent to the FastAPI backend at the /chat/query endpoint
3. The backend checks the message for escalation keywords
4. If escalation is not needed, the backend prepares a prompt containing the system instructions, relevant FAQs, and conversation history
5. This context is sent to the Google Gemini API
6. The API generates a response
7. The response is saved to the session history
8. The response is returned to the frontend
9. The React UI updates to display the new message

## Deployment

### Deploy Backend on Heroku

```bash
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile
echo "python-3.11.0" > runtime.txt

heroku login
heroku create your-backend-app-name
heroku config:set GEMINI_API_KEY=your_key
git push heroku main
```

### Deploy Frontend on Vercel

```bash
npm install -g vercel
vercel login
vercel
```

Set the REACT_APP_API_URL environment variable to your Heroku backend URL.

## Troubleshooting

**Backend won't start**
- Ensure Python 3.8 or higher is installed
- Run `pip install --force-reinstall -r requirements.txt`

**Frontend won't start**
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**CORS errors**
- Ensure backend is running on port 8000
- Clear browser cache

**API key not working**
- Check that .env file exists in the backend directory
- Verify the API key has no quotes or spaces

**Port already in use**
- Use a different port: `python -m uvicorn main:app --port 8001`

## License

MIT License

## Resources

- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- Google Gemini API: https://ai.google.dev/
