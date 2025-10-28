#!/usr/bin/env python3
"""
Comprehensive test for OpenRouter integration with sample log files
"""

import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sample log files for testing
SAMPLE_LOG_FILES = {
    "application.log": """2024-01-15 10:30:15 INFO Application started successfully
2024-01-15 10:30:16 INFO Database connection established
2024-01-15 10:30:17 ERROR Failed to load configuration file config.json
2024-01-15 10:30:18 WARN Using default configuration settings
2024-01-15 10:30:19 INFO Server listening on port 8080
2024-01-15 10:30:20 INFO User authentication service initialized
2024-01-15 10:31:15 ERROR Database connection timeout after 30 seconds
2024-01-15 10:31:16 ERROR Failed to connect to Redis cache server
2024-01-15 10:31:17 WARN Falling back to in-memory cache
2024-01-15 10:31:18 INFO Application running in degraded mode
2024-01-15 10:32:00 ERROR OutOfMemoryError: Java heap space exceeded
2024-01-15 10:32:01 ERROR Application crashed due to memory issues
2024-01-15 10:32:02 INFO Application restarting...
2024-01-15 10:32:03 INFO Application started successfully
2024-01-15 10:32:04 INFO Database connection established
2024-01-15 10:32:05 INFO Server listening on port 8080""",

    "web_server.log": """2024-01-15 14:25:10 INFO Nginx server started on port 80
2024-01-15 14:25:11 INFO SSL certificate loaded successfully
2024-01-15 14:25:12 INFO Load balancer configured with 3 backend servers
2024-01-15 14:26:00 INFO GET /api/users - 200 OK - 45ms
2024-01-15 14:26:01 INFO POST /api/auth/login - 200 OK - 120ms
2024-01-15 14:26:02 WARN GET /api/orders - 404 Not Found - 12ms
2024-01-15 14:26:03 ERROR POST /api/payments - 500 Internal Server Error - 2000ms
2024-01-15 14:26:04 ERROR Database connection pool exhausted
2024-01-15 14:26:05 WARN High memory usage detected: 85%
2024-01-15 14:26:06 INFO GET /api/products - 200 OK - 67ms
2024-01-15 14:26:07 ERROR SSL handshake failed for client 192.168.1.100
2024-01-15 14:26:08 WARN Rate limit exceeded for IP 192.168.1.101
2024-01-15 14:26:09 INFO GET /api/health - 200 OK - 5ms""",

    "database.log": """2024-01-15 09:15:30 INFO PostgreSQL server started
2024-01-15 09:15:31 INFO Database 'loglytics_ai' created successfully
2024-01-15 09:15:32 INFO User 'admin' created with privileges
2024-01-15 09:15:33 INFO Connection pool initialized with 20 connections
2024-01-15 09:16:00 INFO Query executed: SELECT * FROM users WHERE active = true
2024-01-15 09:16:01 INFO Query execution time: 15ms
2024-01-15 09:16:02 WARN Slow query detected: SELECT * FROM logs WHERE timestamp > '2024-01-01'
2024-01-15 09:16:03 WARN Query execution time: 2500ms
2024-01-15 09:16:04 ERROR Connection timeout: Unable to connect to database
2024-01-15 09:16:05 ERROR Deadlock detected in transaction
2024-01-15 09:16:06 ERROR Transaction rolled back due to deadlock
2024-01-15 09:16:07 INFO Database connection restored
2024-01-15 09:16:08 INFO Query executed: SELECT COUNT(*) FROM log_entries
2024-01-15 09:16:09 INFO Query execution time: 8ms"""
}

# Test questions for log analysis
LOG_ANALYSIS_QUESTIONS = [
    "What errors do you see in this log file?",
    "What are the main issues causing problems?",
    "What would you recommend to fix these issues?",
    "Are there any performance bottlenecks?",
    "What patterns do you notice in the error messages?",
    "How would you prioritize these issues for resolution?"
]

# General conversation questions
GENERAL_QUESTIONS = [
    "Hello! How are you today?",
    "Can you tell me a joke?",
    "What's the weather like today?",
    "Can you help me write a Python function to sort a list?",
    "What are some best practices for logging in applications?",
    "Tell me about machine learning algorithms.",
    "What's the difference between SQL and NoSQL databases?",
    "Can you explain what Docker containers are?"
]

async def test_log_analysis():
    """Test log analysis capabilities"""
    print("=" * 80)
    print("TESTING LOG ANALYSIS CAPABILITIES")
    print("=" * 80)
    
    try:
        from app.services.chat_enhanced_service import enhanced_chat_service
        from app.schemas.chat_enhanced import ChatMessage
        
        results = []
        
        for log_name, log_content in SAMPLE_LOG_FILES.items():
            print(f"\nTesting with {log_name}")
            print("-" * 50)
            print(f"Log content preview: {log_content[:100]}...")
            
            # Create conversation history
            conversation_history = [
                ChatMessage(role="user", content=f"Here's a {log_name} file to analyze"),
                ChatMessage(role="assistant", content="I'm ready to analyze your log file. Please share the content.")
            ]
            
            # Test each question
            for i, question in enumerate(LOG_ANALYSIS_QUESTIONS, 1):
                print(f"\nQuestion {i}: {question}")
                
                # Create full message with log content
                full_message = f"{question}\n\nHere's the log file content:\n```\n{log_content}\n```"
                
                try:
                    response = await enhanced_chat_service.chat(
                        message=full_message,
                        conversation_history=conversation_history
                    )
                    
                    print(f"SUCCESS Response: {response}")
                    
                    # Store results
                    results.append({
                        "log_file": log_name,
                        "question": question,
                        "response": response,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Update conversation history
                    conversation_history.append(ChatMessage(role="user", content=question))
                    conversation_history.append(ChatMessage(role="assistant", content=response))
                    
                except Exception as e:
                    print(f"ERROR: {e}")
                    results.append({
                        "log_file": log_name,
                        "question": question,
                        "response": f"Error: {e}",
                        "timestamp": datetime.now().isoformat()
                    })
        
        return results
        
    except Exception as e:
        print(f"ERROR Log analysis test failed: {e}")
        return []

async def test_general_conversation():
    """Test general conversation capabilities"""
    print("\n" + "=" * 80)
    print("TESTING GENERAL CONVERSATION CAPABILITIES")
    print("=" * 80)
    
    try:
        from app.services.chat_enhanced_service import enhanced_chat_service
        from app.schemas.chat_enhanced import ChatMessage
        
        results = []
        conversation_history = []
        
        for i, question in enumerate(GENERAL_QUESTIONS, 1):
            print(f"\nQuestion {i}: {question}")
            
            try:
                response = await enhanced_chat_service.chat(
                    message=question,
                    conversation_history=conversation_history
                )
                
                print(f"SUCCESS Response: {response}")
                
                # Store results
                results.append({
                    "question": question,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update conversation history
                conversation_history.append(ChatMessage(role="user", content=question))
                conversation_history.append(ChatMessage(role="assistant", content=response))
                
            except Exception as e:
                print(f"ERROR: {e}")
                results.append({
                    "question": question,
                    "response": f"Error: {e}",
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
        
    except Exception as e:
        print(f"ERROR General conversation test failed: {e}")
        return []

def save_test_results(log_results, conversation_results):
    """Save test results to file"""
    results = {
        "test_timestamp": datetime.now().isoformat(),
        "log_analysis_results": log_results,
        "general_conversation_results": conversation_results,
        "summary": {
            "total_log_questions": len(log_results),
            "total_conversation_questions": len(conversation_results),
            "successful_log_questions": len([r for r in log_results if not r["response"].startswith("Error:")]),
            "successful_conversation_questions": len([r for r in conversation_results if not r["response"].startswith("Error:")])
        }
    }
    
    with open("openrouter_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest results saved to openrouter_test_results.json")
    return results

async def main():
    """Main test function"""
    print("COMPREHENSIVE OPENROUTER INTEGRATION TEST")
    print("=" * 80)
    print(f"Test started at: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Test log analysis
    log_results = await test_log_analysis()
    
    # Test general conversation
    conversation_results = await test_general_conversation()
    
    # Save results
    results = save_test_results(log_results, conversation_results)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"SUCCESS Log Analysis Questions: {results['summary']['successful_log_questions']}/{results['summary']['total_log_questions']}")
    print(f"SUCCESS General Conversation Questions: {results['summary']['successful_conversation_questions']}/{results['summary']['total_conversation_questions']}")
    print(f"Results saved to: openrouter_test_results.json")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
