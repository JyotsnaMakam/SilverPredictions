"""
AI-powered chatbot module using OpenAI API
"""
import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

class PrecisousMetalsBot:
    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.getenv("CHATBOT_API_KEY")
        openai.api_key = self.api_key
        
        # System prompt for the bot
        self.system_prompt = """You are an intelligent investment advisor chatbot specializing in precious metals (gold and silver). 
You help users understand:
- Silver (SLV ETF) and gold (GLD ETF) investments
- Current market trends and price movements
- Investment strategies for precious metals
- Gold-to-silver ratios and their significance
- Risk management and diversification tips

Provide concise, accurate, and helpful responses. If asked about topics outside precious metals, politely redirect to metals-related investment advice.
Your responses should be practical and suitable for retail investors."""
        
        self.conversation_history = []
    
    def get_response(self, user_question):
        """Get AI-powered response using OpenAI API"""
        try:
            if not self.api_key:
                return "⚠️ API key not configured. Please add CHATBOT_API_KEY to .env file."
            
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_question
            })
            
            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt}
                ] + self.conversation_history,
                max_tokens=300,
                temperature=0.7
            )
            
            # Extract response
            bot_response = response.choices[0].message.content
            
            # Add bot response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": bot_response
            })
            
            # Keep only last 10 messages to avoid token limits
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return bot_response
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}. Make sure your API key is valid."
    
    def get_suggestions(self):
        """Return suggested questions"""
        return [
            "What is silver and why invest in it?",
            "How does the gold-to-silver ratio work?",
            "What are SLV and GLD ETFs?",
            "Best strategy for precious metals investing?",
            "How to diversify with precious metals?",
            "What's the current market outlook for silver?"
        ]
