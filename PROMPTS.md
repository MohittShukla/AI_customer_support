# PROMPTS.md - LLM Customization Guide

This document explains how the bot's prompts work and how to customize them.

## System Prompt

The main system prompt is in `backend/main.py` in the `get_system_prompt()` function. This is what tells the AI how to behave.

Current prompt:

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

## Changing Bot Behavior

You can change how the bot responds by editing the system prompt. For example, if you want a friendlier bot:

```python
def get_system_prompt() -> str:
    return """You are a friendly and helpful customer support assistant.

Your goal is to make customers feel heard and help them solve their problems.

[Keep rest of the prompt...]
"""
```

Or if you want it more formal:

```python
def get_system_prompt() -> str:
    return """You are a professional customer service representative.

Maintain professionalism and accuracy in all responses.

[Keep rest...]
"""
```

## Adding FAQ Context

The FAQ database is automatically included in every API call. The `create_faq_context()` function formats all FAQs like this:

```
Available FAQs:

SHIPPING:
- Q: How long does shipping take?
  A: Standard shipping takes 5-7 business days...
  
RETURNS:
- Q: What is your return policy?
  A: We offer 30-day returns on unused items...
```

This context is what keeps the bot grounded in accurate information instead of making things up.

## Conversation History

The bot receives the entire conversation history with each request. This allows it to understand follow-up questions and maintain context. For example:

Customer: "How much is shipping?"
Bot: "Shipping is $5 for standard, $15 for international."
Customer: "What about express?"
Bot: Understands they're asking about express shipping costs (context from previous message)

If the bot isn't understanding context, you may need to adjust how messages are passed or increase the temperature (see below).

## Response Parameters

In the `call_gemini_api()` function, you can adjust:

```python
generation_config=GenerationConfig(
    temperature=0.7,
    max_output_tokens=300
)
```

Temperature controls how creative the responses are:
- 0.0 to 0.3: Very factual, consistent
- 0.5 to 0.7: Balanced, natural conversation (recommended)
- 0.8 to 1.0: More creative, less predictable

Max tokens controls response length. 300 is good for customer support. Lower it to 150 if responses are too long.

## Escalation Triggers

The escalation logic is in `check_escalation_needed()`. Currently it looks for these keywords:

```python
escalation_keywords = [
    "frustrated", "angry", "complaint", "manager", "supervisor",
    "urgent", "emergency", "security", "hacked", "billing error",
    "refund not received", "damaged product", "wrong item"
]
```

You can add or remove keywords as needed. When a message contains any of these, the conversation gets escalated to human support.

## Customizing Escalation Messages

When escalation happens, the bot returns this message:

```python
response = "I've detected this might need special attention. Let me connect you with a human support specialist..."
```

You can change this to something else. For example:

```python
response = f"I understand your frustration, {customer_name}. I'm connecting you with a specialist who can help immediately."
```

## Testing Your Changes

To test prompt changes:

1. Modify the prompt in `get_system_prompt()`
2. Restart the backend server
3. Test with a few questions

Good test cases:
- FAQ question: "What is your return policy?" - should give accurate answer
- Follow-up: Ask follow-up to check context understanding
- Escalation: Type something frustrating to trigger escalation
- Out of scope: Ask something not in FAQs to see how it handles it

## Adding Industry-Specific Instructions

If you want the bot to behave differently for your specific industry, add it to the prompt:

```python
def get_system_prompt() -> str:
    faq_context = create_faq_context()
    return f"""You are a customer support assistant for a tech company.

{faq_context}

IMPORTANT:
- Always mention warranty when discussing products
- Include setup instructions for technical issues
- Be extra helpful with error messages

[Rest of prompt...]
"""
```

## Response Format Control

You can control the format of responses by being specific in the prompt:

For shorter responses:
```
Be very concise - max 1-2 sentences per response
```

For structured responses:
```
RESPONSE FORMAT:
- Start with the direct answer
- Provide next steps if needed
- End with a question if appropriate
```

## Handling Common Issues

If the bot is giving bad responses:

1. Check if it's a FAQ question - if yes, it should know the answer
2. If not in FAQs, it might be making things up - this is normal for LLMs
3. Add the answer to FAQs if it's something you want it to know
4. Escalation is your fallback for anything too complex

If the bot escalates too much:
- Review the escalation keywords, maybe remove some
- Or adjust the system prompt to be more confident

If responses are too long:
- Reduce max_output_tokens from 300 to 150 or 200
- Add to prompt: "Be concise - max 2 sentences"

If responses are too short:
- Increase max_output_tokens
- Add to prompt: "Provide helpful details"

## About Temperature

Don't change temperature too much. For customer support, 0.5-0.7 is good. Higher temps make responses less predictable (bad for support). Lower temps make them robotic (also bad).

If you want more variety in responses, increase to 0.8. If you want consistency, lower to 0.5.

## Monitoring What Works

Pay attention to:
- Are escalations happening at the right times?
- Do follow-up questions work correctly?
- Are FAQ answers accurate?
- Do customers get frustrated because of bot responses?

If you notice patterns, adjust the prompt accordingly.

## FAQ Updates

The fastest way to improve the bot is to add more FAQs. If customers keep asking the same question and the bot doesn't have a good answer, add it to the FAQS dictionary in main.py.

If you add a FAQ, restart the server so it picks up the new context.

## Notes

- The prompt is sent with every API call, so changes take effect immediately (after restart)
- The FAQ context is automatically formatted, so adding new FAQs happens automatically
- Conversation history helps the bot understand context, but very long conversations might hurt performance
- The bot only knows what's in the FAQs and system prompt - it won't invent information (hopefully)
