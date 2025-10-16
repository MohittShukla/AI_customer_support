AI Customer Support Bot
This project is a customer support chatbot built using FastAPI for the backend, React for the frontend, and the Google Gemini API for generating responses. It features real-time messaging, FAQ management, and conversation history.

Project Features
AI-Powered Responses: Uses the Google Gemini API to generate conversational responses.
Real-Time Chat Interface: A simple and responsive chat UI for user interaction.
FAQ Database: Comes pre-loaded with common questions and answers organized into categories.
Context Awareness: The bot maintains the context of the current conversation to answer follow-up questions.
Escalation Logic: A simple keyword-based system to detect user frustration and suggest escalating to a human agent.
Session Management: Each user conversation is tracked in a unique session.
Technology Stack
Backend: Python, FastAPI, Uvicorn
Frontend: React 18, CSS
AI Model: Google Gemini API
Data Storage: In-memory dictionary (can be replaced with a database)
Deployment: Instructions included for Docker, Heroku, and Vercel.
Local Setup and Installation
Prerequisites
Python 3.8 or higher
Node.js 14 or higher
A Google Gemini API Key
Installation Steps
1. Clone the repository

Bash
git clone <your-repo>
cd customer-support-bot
2. Set up the Backend

Bash
cd backend
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
pip install -r requirements.txt
3. Add your Gemini API Key Create a new file named .env inside the backend directory and add your API key to it.

Bash
# backend/.env
GEMINI_API_KEY=your_key_here
4. Start the Backend Server

Bash
python -m uvicorn main:app --reload --port 8000
You can view the interactive API documentation at http://localhost:8000/docs.

5. Set up the Frontend (in a new terminal)

Bash
cd frontend
npm install
npm start
The application will open in your browser at http://localhost:3000.

Running the Application
Once both the frontend and backend are running, you can interact with the chatbot in your browser. Enter your name, start a chat, and ask a question like, "What is your return policy?" to see the AI response.

API Endpoints
Chat Operations
Method	Endpoint	Purpose
POST	/chat/new-session	Creates a new chat session for a user.
POST	/chat/query	Sends a user message and gets an AI response.
GET	/chat/session/{id}	Retrieves the full conversation history for a session.
POST	/chat/escalate	Manually flags a session for escalation.
FAQ & System
Method	Endpoint	Purpose
GET	/faqs	Retrieves all FAQs from the database.
GET	/faqs/{category}	Retrieves FAQs for a specific category.
GET	/health	A simple health check endpoint for the server.
Example curl Request:

Bash
curl -X POST http://localhost:8000/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "customer_name": "John",
    "message": "How long is shipping?"
  }'
Project Structure
customer-support-bot/
├── backend/
│   ├── main.py              # Main FastAPI application file
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # For API key storage (not committed)
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css          # Component styling
│   │   └── index.js         # React entry point
│   ├── public/index.html    # Base HTML file
│   └── package.json         # Frontend dependencies
└── README.md
Customization
Modifying the Bot's Personality
You can change how the bot behaves by editing the system prompt.
File: backend/main.py
Function: get_system_prompt()
Example:
Python
# To make the bot more direct and professional
return """You are a professional customer service representative.
Provide accurate, concise, and courteous responses..."""
Adding New FAQs
To add more questions and answers to the bot's knowledge base, edit the FAQS dictionary.
File: backend/main.py
Variable: FAQS
Example:
Python
FAQS = {
    "shipping": [...],
    "new_category": [
        {"q": "First new question?", "a": "First new answer."},
        {"q": "Second new question?", "a": "Second new answer."},
    ]
}
Changing UI Colors
The primary colors for the user interface can be changed by editing the CSS variables.
File: frontend/src/App.css
Selector: :root
Example:
CSS
:root {
  --primary: #007bff;   /* Change main brand color */
  --text: #333;         /* Change text color */
  --bg: #ffffff;         /* Change background color */
}
How It Works
A user sends a message from the React frontend.
The FastAPI backend receives the message at the /chat/query endpoint.
The backend checks the message for any keywords that might require escalating the chat.
If no escalation is needed, the backend constructs a prompt containing the system instructions, relevant FAQs, and the recent conversation history.
This complete context is sent to the Google Gemini API.
The Gemini API generates a response.
The response is saved to the in-memory session history and sent back to the frontend.
The React UI updates to display the new message.
Deployment
Backend on Heroku
Bash
# Create a Procfile in the backend directory
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Create a runtime.txt file
echo "python-3.11.0" > runtime.txt

# Deploy using the Heroku CLI
heroku login
heroku create your-backend-app-name
heroku config:set GEMINI_API_KEY=your_key
git push heroku main
Frontend on Vercel
Bash
# Install the Vercel CLI
npm install -g vercel

# Deploy from the frontend directory
vercel login
vercel

# When prompted, set the REACT_APP_API_URL environment variable
# to the URL of your deployed Heroku backend.
