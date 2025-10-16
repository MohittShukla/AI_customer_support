import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [customerName, setCustomerName] = useState('');
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [escalated, setEscalated] = useState(false);
  const [chatStarted, setChatStarted] = useState(false);
  const [faqs, setFaqs] = useState({});
  const messagesEndRef = useRef(null);

  const API_BASE_URL = 'http://localhost:8000';

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Fetch FAQs on mount
  useEffect(() => {
    fetchFAQs();
  }, []);

  const fetchFAQs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/faqs`);
      const data = await response.json();
      setFaqs(data);
    } catch (error) {
      console.error('Error fetching FAQs:', error);
    }
  };

  const startNewSession = async (e) => {
    e.preventDefault();
    if (!customerName.trim()) {
      alert('Please enter your name');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/chat/new-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_name: customerName })
      });
      const data = await response.json();
      setSessionId(data.session_id);
      setMessages([
        {
          role: 'assistant',
          content: `Hi ${customerName}! 👋 Welcome to our customer support. How can I help you today? I can assist with shipping, returns, products, payments, and account issues.`,
          timestamp: new Date().toISOString()
        }
      ]);
      setChatStarted(true);
    } catch (error) {
      console.error('Error starting session:', error);
      alert('Failed to start chat session');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || !sessionId || loading) return;

    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          customer_name: customerName,
          message: inputValue
        })
      });

      const data = await response.json();

      if (data.escalated) {
        setEscalated(true);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toISOString(),
          escalated: true
        }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleEscalate = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/chat/escalate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          reason: 'Customer requested escalation'
        })
      });

      const data = await response.json();
      setEscalated(true);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.message,
        timestamp: new Date().toISOString(),
        escalated: true
      }]);
    } catch (error) {
      console.error('Error escalating:', error);
    }
  };

  const restartChat = () => {
    setSessionId(null);
    setCustomerName('');
    setMessages([]);
    setInputValue('');
    setEscalated(false);
    setChatStarted(false);
  };

  return (
    <div className="app-container">
      <div className="support-bot">
        <header className="header">
          <h1>💬 Customer Support Bot</h1>
          <p>AI-Powered Support Assistant</p>
        </header>

        {!chatStarted ? (
          <div className="welcome-section">
            <div className="welcome-card">
              <h2>Welcome to Support</h2>
              <p>Start a conversation with our AI assistant. We're here to help!</p>
              
              <form onSubmit={startNewSession} className="welcome-form">
                <input
                  type="text"
                  placeholder="Enter your name"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="name-input"
                />
                <button type="submit" className="start-btn">Start Chat</button>
              </form>

              <div className="faq-preview">
                <h3>📚 We Can Help With:</h3>
                <div className="faq-categories">
                  {Object.keys(faqs).map(category => (
                    <div key={category} className="faq-category-card">
                      <strong>{category.charAt(0).toUpperCase() + category.slice(1)}</strong>
                      <p>{faqs[category]?.length || 0} articles</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="chat-section">
            <div className="messages-container">
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.role} ${msg.escalated ? 'escalated' : ''}`}>
                  <div className="message-badge">{msg.role === 'user' ? '👤' : '🤖'}</div>
                  <div className="message-content">{msg.content}</div>
                  <div className="message-time">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message assistant">
                  <div className="message-badge">🤖</div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <div className="chat-controls">
              {escalated && (
                <div className="escalation-notice">
                  ⚠️ This issue has been escalated to our support team. A representative will contact you shortly.
                </div>
              )}
              
              <form onSubmit={sendMessage} className="message-form">
                <input
                  type="text"
                  placeholder="Type your question..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  disabled={loading || escalated}
                  className="message-input"
                />
                <button 
                  type="submit" 
                  disabled={loading || escalated || !inputValue.trim()}
                  className="send-btn"
                >
                  Send
                </button>
              </form>

              <div className="action-buttons">
                {!escalated && (
                  <button onClick={handleEscalate} className="escalate-btn">
                    Talk to Human Agent
                  </button>
                )}
                <button onClick={restartChat} className="restart-btn">
                  New Chat
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
