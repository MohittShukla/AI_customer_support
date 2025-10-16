# LLM Prompts Documentation

This document details all prompts used in the Customer Support Bot and how to customize them.

## 📌 System Prompts Overview

### 1. Main System Prompt

**Location**: `backend/main.py` → `get_system_prompt()` function

**Current Prompt**:
```
You are a professional, empathetic customer support assistant for an e-commerce company.

[FAQ Database inserted here]

INSTRUCTIONS:
1. Answer questions using the FAQ database when applicable
2. Be helpful, professional, and concise (max 2-3 sentences)
3. If you cannot answer from FAQs, acknowledge and suggest escalation
4. Track context from previous messages in the conversation
5. If a customer seems frustrated or has a complex issue, recommend escalation to human support
6. Always be honest - never make up information

ESCALATION TRIGGERS:
- Complex technical issues
- Account security concerns
- Billing disputes
- Customer frustration or anger
- Issues not covered in FAQs after 2 attempts
```

**Purpose**: 
- Defines bot personality and behavior
- Sets response guidelines
- Establishes knowledge boundaries
- Triggers escalation logic

### 2. FAQ Context Prompt

**Location**: `backend/main.py` → `create_faq_context()` function

**Purpose**:
- Automatically includes FAQ data in every API call
- Provides reference material for responses
- Keeps model grounded in accurate information

**Structure**:
```
Available FAQs:

SHIPPING:
- Q: How long does shipping take?
  A: Standard shipping takes 5-7 business days...
  
RETURNS:
- Q: What is your return policy?
  A: We offer 30-day returns on unused items...

[More categories...]
```

## 🎯 Prompt Customization Guide

### Change Bot Personality

**For a more friendly bot:**

```python
def get_system_prompt() -> str:
    return """You are a friendly and enthusiastic customer support assistant! 😊

Your goal is to make every customer feel valued and heard.

[Keep rest of prompt...]
"""
```

**For a formal/professional tone:**

```python
def get_system_prompt() -> str:
    return """You are a professional customer support representative.

Maintain professionalism and accuracy in all responses.

[Keep rest of prompt...]
"""
```

### Add Industry-Specific Guidelines

```python
def get_system_prompt() -> str:
    faq_context = create_faq_context()
    return f"""You are a customer support assistant for [YOUR_INDUSTRY].

{faq_context}

INDUSTRY-SPECIFIC GUIDELINES:
1. Always mention warranty information when relevant
2. Include setup instructions for technical products
3. Reference safety warnings when applicable
4. Provide estimated delivery times for all shipments

[Continue with rest...]
"""
```

### Modify Response Style

**For shorter responses:**
```python
# In the INSTRUCTIONS section:
"Be concise - max 1-2 sentences per response"
```

**For detailed responses:**
```python
# In the INSTRUCTIONS section:
"Provide comprehensive answers with step-by-step guidance when needed"
```

**For action-oriented responses:**
```python
# Add this section:
"RESPONSE FORMAT:
- Start with the answer
- Provide next steps if applicable
- End with how to get more help"
```

## 🔄 Conversation Context

### How Context is Passed

The bot receives the entire conversation history:

```python
chat_history = [
    {"role": "user", "parts": [{"text": "Hello"}]},
    {"role": "model", "parts": [{"text": "Hi there!"}]},
    {"role": "user", "parts": [{"text": "What's your return policy?"}]},
    # Current message...
]
```

### Enhance Context Awareness

Add this to your system prompt:

```python
CONVERSATION_CONTEXT_GUIDELINES:
1. Review previous messages for context
2. Track customer pain points
3. Reference earlier solutions if applicable
4. Avoid repeating information already discussed
5. Build on customer preferences mentioned
```

## 🚨 Escalation Prompts

### When to Show Escalation Message

**Current Logic** (in `check_escalation_needed()`):

```python
escalation_keywords = [
    "frustrated", "angry", "complaint", "manager", "supervisor",
    "urgent", "emergency", "security", "hacked", "billing error",
    "refund not received", "damaged product", "wrong item"
]
```

### Customize Escalation Message

In `backend/main.py`, modify the response when `escalated = True`:

```python
# Current:
response = "I've detected this might need special attention. Let me connect you with a human support specialist..."

# Customize to:
response = f"I understand your frustration, {customer_name}. I'm connecting you with a specialist who can resolve this right away."
```

### Add Emotion Detection

Enhance the system prompt:

```python
EMOTION_DETECTION:
- Detect frustrated tone: Use empathetic language
- Detect confusion: Provide clear step-by-step guidance
- Detect urgency: Prioritize and offer immediate action
- Detect satisfaction: Confirm resolution and thank customer
```

## 📊 Response Generation Parameters

### Temperature (Creativity)

```python
# In call_gemini_api():
generation_config=genai.types.GenerationConfig(
    temperature=0.7,  # Range: 0.0-1.0
    max_output_tokens=300
)
```

**Temperature Guide**:
- `0.0`: Very consistent, factual responses (best for FAQs)
- `0.3-0.5`: Balanced, slightly creative
- `0.7`: Default, natural conversation
- `0.9+`: Very creative, less predictable

**Recommendation for Support Bot**: Keep at 0.5-0.7

### Max Output Tokens

```python
max_output_tokens=300  # Controls response length
```

**Guidelines**:
- FAQ answers: 100-150 tokens
- Complex explanations: 200-300 tokens
- Short confirmations: 50-100 tokens

## 🎓 Few-Shot Prompt Examples

Add examples to your system prompt:

```python
EXAMPLES:

CUSTOMER: How long is shipping?
BOT: Standard shipping takes 5-7 business days. Express shipping is available for 2-3 days. Would you like to know the costs?

CUSTOMER: I received a damaged item
BOT: I'm sorry to hear that! I can help you with this. Could you please share your order number? Once I have that, I'll arrange a replacement or refund right away.

CUSTOMER: Why is my refund taking so long?
BOT: I understand your concern. Refunds typically process within 5-7 business days after we receive the return. Let me connect you with a specialist who can check the status of your specific refund.
```

## 🔍 Testing Prompts

### Test Cases for Validation

**FAQ Coverage Test:**
```
Input: "What's your return policy?"
Expected: Direct answer from FAQ database
```

**Escalation Test:**
```
Input: "I'm extremely frustrated with my order!"
Expected: Escalation detected + human connection offer
```

**Out-of-Scope Test:**
```
Input: "What's the weather today?"
Expected: Honest answer that it's out of scope, offer escalation
```

**Context Test:**
```
Conversation:
- Customer asks about shipping costs
- Customer then asks "What about express?"
Expected: Bot understands context, mentions express from previous answer
```

## 📝 Prompt Engineering Tips

### 1. Be Specific
❌ Bad: "Help with customer service"
✅ Good: "Answer e-commerce customer questions using provided FAQs"

### 2. Use Clear Instructions
❌ Bad: "Be nice"
✅ Good: "Be professional and empathetic. Max 2-3 sentences per response."

### 3. Provide Context
❌ Bad: No context
✅ Good: "You support a clothing e-commerce company. FAQs cover: [topics]"

### 4. Set Boundaries
❌ Bad: "Answer anything"
✅ Good: "Only answer from FAQs. Escalate if unsure."

### 5. Use Examples
❌ Bad: "Sound natural"
✅ Good: "See examples below for tone reference"

## 🔗 Integration with Gemini API

### How Prompts Flow

```
1. Customer Input
   ↓
2. System Prompt Loaded (get_system_prompt())
   ↓
3. FAQ Context Added (create_faq_context())
   ↓
4. Conversation History Attached
   ↓
5. Sent to Gemini API
   ↓
6. Response Generated
   ↓
7. Returned to Frontend
```

### Example API Call

```python
response = model.generate_content(
    contents=chat_history,  # Conversation history
    generation_config=GenerationConfig(
        temperature=0.7,
        max_output_tokens=300
    ),
    system_instruction=get_system_prompt()  # Your prompt
)
```

## 🛠️ Advanced Customizations

### Multi-Language Support

```python
def get_system_prompt_for_language(language: str) -> str:
    prompts = {
        "en": "You are a professional customer support assistant...",
        "es": "Eres un asistente profesional de soporte al cliente...",
        "fr": "Vous êtes un assistant support client professionnel..."
    }
    return prompts.get(language, prompts["en"])
```

### Dynamic Prompts Based on Category

```python
def get_system_prompt_for_category(category: str) -> str:
    if category == "billing":
        return "You are a specialist in billing and payment issues..."
    elif category == "shipping":
        return "You are a specialist in shipping and logistics..."
    else:
        return get_system_prompt()
```

### Sentiment-Based Prompts

```python
def get_system_prompt_based_on_sentiment(sentiment: str) -> str:
    if sentiment == "angry":
        return "The customer is upset. Be extra empathetic and solution-focused..."
    elif sentiment == "confused":
        return "The customer is confused. Provide clear, step-by-step guidance..."
    else:
        return get_system_prompt()
```

## 📊 Monitoring Prompt Performance

### Key Metrics to Track

1. **Response Accuracy**: % of correct FAQ answers
2. **Escalation Rate**: % of conversations escalated
3. **Customer Satisfaction**: Survey scores
4. **Resolution Rate**: % resolved without escalation
5. **Response Time**: Average API latency

### Log Prompts and Responses

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"System Prompt: {get_system_prompt()}")
logger.info(f"Customer Message: {message}")
logger.info(f"Bot Response: {response}")
```

## 🚀 Best Practices

1. **Always include FAQ context** - Grounds responses in accurate data
2. **Test prompt changes** - Use test cases before deploying
3. **Update FAQs regularly** - Keep bot current
4. **Monitor escalations** - Understand what users struggle with
5. **Get user feedback** - Refine prompts based on satisfaction
6. **Version your prompts** - Track changes over time
7. **Document customizations** - Note why you changed anything

## 📞 Common Customization Requests

### Request: Make Bot More Helpful

```python
# Add to INSTRUCTIONS:
"Always suggest next steps or related resources"
"Provide links to FAQs when relevant"
"Offer multiple solution options when available"
```

### Request: Reduce Bot Responses Length

```python
# Change:
"Be concise - max 1-2 sentences"
# Also reduce:
max_output_tokens=150  # Down from 300
```

### Request: Add Product Recommendations

```python
# Add to prompt:
"When relevant, suggest complementary products"
"Reference best-sellers for common questions"
```

### Request: Better Handle Complaints

```python
# Add section:
"COMPLAINT HANDLING:
1. Acknowledge the issue genuinely
2. Apologize for inconvenience
3. Offer immediate solution
4. Follow up when resolved"
```

---

**Need more help? Check the README.md for API details and setup instructions.**
