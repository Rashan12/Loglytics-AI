"""
Prompt templates for LLM tasks
"""

import json
from typing import Dict, List, Any

class PromptTemplates:
    """Prompt templates for different LLM tasks"""
    
    def __init__(self):
        self.templates = {
            "log_analysis": {
                "system": "You are a log analysis expert. Analyze log data and provide insights about system behavior, errors, and performance.",
                "few_shot": "Example: Analyze these logs and identify the main issues.",
                "structured_output": "Provide analysis in JSON format with fields: summary, errors, warnings, recommendations."
            },
            "error_detection": {
                "system": "You are an error detection specialist. Identify and categorize errors in log data.",
                "few_shot": "Example: Find all errors in these logs and categorize them by severity.",
                "structured_output": "Provide error analysis in JSON format."
            },
            "root_cause_analysis": {
                "system": "You are a root cause analysis expert. Identify the underlying causes of issues in log data.",
                "few_shot": "Example: Analyze these logs to find the root cause of the problem.",
                "structured_output": "Provide root cause analysis in JSON format."
            },
            "anomaly_detection": {
                "system": "You are an anomaly detection specialist. Identify unusual patterns in log data.",
                "few_shot": "Example: Find anomalies in these logs.",
                "structured_output": "Provide anomaly detection results in JSON format."
            },
            "natural_query": {
                "system": "You are a natural language query processor for log data. Help users ask questions about their logs.",
                "few_shot": "Example: Answer questions about log data in plain English.",
                "structured_output": "Provide query results in JSON format."
            },
            "summarization": {
                "system": "You are a log summarization expert. Create concise summaries of log data.",
                "few_shot": "Example: Summarize these logs highlighting key events.",
                "structured_output": "Provide summary in JSON format."
            },
            "chat": {
                "system": "You are Loglytics AI, a helpful assistant for log analysis and system monitoring.",
                "few_shot": "Example: Help users understand their logs and troubleshoot issues.",
                "structured_output": "Provide chat response in JSON format."
            }
        }
    
    def get_system_prompt(self, task: str) -> str:
        """Get system prompt for a specific task"""
        return self.templates.get(task, {}).get("system", "You are a helpful assistant.")
    
    def get_few_shot_examples(self, task: str) -> str:
        """Get few-shot examples for a specific task"""
        return self.templates.get(task, {}).get("few_shot", "")
    
    def get_structured_output_prompt(self, task: str) -> str:
        """Get structured output prompt for a specific task"""
        return self.templates.get(task, {}).get("structured_output", "")
    
    def create_prompt(self, task: str, user_input: str, **kwargs) -> str:
        """Create a complete prompt for a task"""
        system_prompt = self.get_system_prompt(task)
        few_shot = self.get_few_shot_examples(task)
        structured_output = self.get_structured_output_prompt(task)
        
        prompt = f"{system_prompt}\n\n"
        
        if few_shot:
            prompt += f"{few_shot}\n\n"
        
        if structured_output:
            prompt += f"{structured_output}\n\n"
        
        prompt += f"User Input: {user_input}"
        
        return prompt