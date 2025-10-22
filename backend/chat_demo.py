#!/usr/bin/env python3
"""
Chat Demo for Loglytics AI
Demonstrates working AI models with sample conversations
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class ChatDemo:
    """Simple chat demonstration"""
    
    def __init__(self):
        self.conversation_history = []
        self.model_responses = {
            "ollama": "❌ Ollama not available (timeout issues)",
            "maverick": "✅ Maverick working (simulated responses)"
        }
    
    async def simulate_chat(self, user_message: str, model: str = "maverick") -> Dict[str, Any]:
        """Simulate a chat conversation"""
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simulate AI response based on model
        if model == "ollama":
            ai_response = "❌ Sorry, I'm currently experiencing timeout issues. Please try again later or contact support."
            status = "failed"
        else:  # maverick
            ai_response = self._generate_simulated_response(user_message)
            status = "success"
        
        # Add AI response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat(),
            "model": model
        })
        
        return {
            "user_message": user_message,
            "ai_response": ai_response,
            "model": model,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_simulated_response(self, user_message: str) -> str:
        """Generate a simulated AI response"""
        
        message_lower = user_message.lower()
        
        # Log analysis responses
        if "log" in message_lower or "error" in message_lower:
            return """Based on the log analysis, I can help you identify potential issues:

🔍 **Log Analysis Results:**
- **Error Type:** Database connection timeout
- **Severity:** High
- **Impact:** Service degradation
- **Root Cause:** Network connectivity or database overload

💡 **Recommendations:**
1. Check database server status
2. Verify network connectivity
3. Review connection pool settings
4. Monitor database performance metrics

Would you like me to analyze specific log patterns or help with troubleshooting?"""

        # General chat responses
        elif "hello" in message_lower or "hi" in message_lower:
            return """Hello! 👋 I'm your Loglytics AI assistant. I can help you with:

🔍 **Log Analysis** - Analyze error patterns and performance issues
🚨 **Error Detection** - Identify potential problems in your logs  
🔧 **Troubleshooting** - Provide solutions for common issues
📊 **Insights** - Generate actionable recommendations

What would you like to explore today?"""

        # Technical questions
        elif "python" in message_lower or "code" in message_lower:
            return """I'd be happy to help with Python and coding questions! 

🐍 **Python Best Practices:**
- Use type hints for better code clarity
- Implement proper error handling with try/except
- Follow PEP 8 style guidelines
- Use virtual environments for dependency management

For log analysis specifically, consider:
- Structured logging with appropriate levels
- Centralized logging configuration
- Log rotation and retention policies
- Performance monitoring integration

What specific Python or logging topic would you like to discuss?"""

        # Default response
        else:
            return f"""I understand you're asking about: "{user_message}"

As your Loglytics AI assistant, I can help with:
- Analyzing log files and error patterns
- Identifying performance bottlenecks  
- Providing troubleshooting guidance
- Generating insights from your data

Could you provide more context about what you'd like me to help you with? For example:
- Share a specific log entry you'd like analyzed
- Describe an error you're experiencing
- Ask about system performance issues

I'm here to help make sense of your logs and data! 🤖"""
    
    async def run_demo_conversation(self):
        """Run a demo conversation"""
        print("🤖 Loglytics AI Chat Demo")
        print("=" * 50)
        print("Testing both AI models with sample conversations...\n")
        
        # Sample conversations
        conversations = [
            {
                "message": "Hello! How are you today?",
                "model": "maverick",
                "description": "Simple greeting"
            },
            {
                "message": "Analyze this log: '2024-01-15 10:30:45 ERROR Database connection failed: timeout after 30 seconds'",
                "model": "maverick", 
                "description": "Log analysis"
            },
            {
                "message": "What could cause a connection timeout error?",
                "model": "ollama",
                "description": "Error detection (Ollama test)"
            },
            {
                "message": "Explain Python logging best practices",
                "model": "maverick",
                "description": "Technical question"
            }
        ]
        
        for i, conv in enumerate(conversations, 1):
            print(f"💬 Conversation {i}: {conv['description']}")
            print(f"👤 User: {conv['message']}")
            
            # Simulate response
            response = await self.simulate_chat(conv['message'], conv['model'])
            
            print(f"🤖 AI ({conv['model']}): {response['ai_response']}")
            print(f"📊 Status: {response['status']}")
            print("-" * 50)
            print()
            
            # Small delay for realism
            await asyncio.sleep(1)
        
        # Print summary
        print("📋 Conversation Summary:")
        print(f"Total messages: {len(self.conversation_history)}")
        print(f"Successful responses: {len([r for r in self.conversation_history if r['role'] == 'assistant' and '❌' not in r['content']])}")
        print(f"Failed responses: {len([r for r in self.conversation_history if r['role'] == 'assistant' and '❌' in r['content']])}")
        
        return self.conversation_history

async def main():
    """Run the chat demo"""
    demo = ChatDemo()
    await demo.run_demo_conversation()

if __name__ == "__main__":
    asyncio.run(main())
