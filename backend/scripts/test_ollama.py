#!/usr/bin/env python3
"""
Test script for Ollama LLM integration
This script tests the Ollama model with various log analysis scenarios
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, List

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.config.llm_config import get_ollama_config, get_log_analysis_prompts

class OllamaTester:
    def __init__(self):
        self.config = get_ollama_config()
        self.prompts = get_log_analysis_prompts()
        self.ollama_url = self.config["base_url"]
        
    def test_basic_inference(self) -> bool:
        """Test basic model inference"""
        print("🧪 Testing basic inference...")
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.config["model_name"],
                    "prompt": "Hello, can you help me analyze logs?",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Basic inference successful: {data['response'][:100]}...")
                return True
            else:
                print(f"❌ Basic inference failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error in basic inference: {e}")
            return False
    
    def test_log_analysis(self) -> bool:
        """Test log analysis capabilities"""
        print("🔍 Testing log analysis...")
        
        sample_logs = [
            "[ERROR] Database connection failed: timeout after 30s",
            "[WARN] High memory usage: 85% of available memory",
            "[INFO] User login successful: user_id=12345",
            "[CRITICAL] Application crashed: null pointer exception"
        ]
        
        log_entries = "\n".join([f"- {log}" for log in sample_logs])
        prompt = self.prompts["analysis_prompt"].format(log_entries=log_entries)
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.config["model_name"],
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config["temperature"],
                        "top_p": self.config["top_p"]
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Log analysis successful!")
                print("📝 Analysis result:")
                print("-" * 50)
                print(data['response'])
                print("-" * 50)
                return True
            else:
                print(f"❌ Log analysis failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error in log analysis: {e}")
            return False
    
    def test_chat_functionality(self) -> bool:
        """Test chat functionality"""
        print("💬 Testing chat functionality...")
        
        context = "Recent logs show database connection issues and high memory usage."
        question = "What should I do to fix these issues?"
        
        prompt = self.prompts["chat_prompt"].format(
            context=context,
            question=question
        )
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.config["model_name"],
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Chat functionality successful!")
                print("📝 Chat response:")
                print("-" * 50)
                print(data['response'])
                print("-" * 50)
                return True
            else:
                print(f"❌ Chat functionality failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error in chat functionality: {e}")
            return False
    
    def test_anomaly_detection(self) -> bool:
        """Test anomaly detection"""
        print("🔍 Testing anomaly detection...")
        
        log_entries = """
- [INFO] Normal operation: CPU 45%
- [INFO] Normal operation: CPU 48%
- [ERROR] Database timeout: 5s
- [ERROR] Database timeout: 8s
- [ERROR] Database timeout: 12s
- [CRITICAL] System overload: CPU 95%
- [CRITICAL] System overload: CPU 98%
- [CRITICAL] System overload: CPU 99%
"""
        
        prompt = self.prompts["anomaly_detection"].format(log_entries=log_entries)
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.config["model_name"],
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Anomaly detection successful!")
                print("📝 Anomaly analysis:")
                print("-" * 50)
                print(data['response'])
                print("-" * 50)
                return True
            else:
                print(f"❌ Anomaly detection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error in anomaly detection: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🚀 Starting Ollama LLM Tests")
        print("=" * 50)
        
        tests = [
            ("Basic Inference", self.test_basic_inference),
            ("Log Analysis", self.test_log_analysis),
            ("Chat Functionality", self.test_chat_functionality),
            ("Anomaly Detection", self.test_anomaly_detection)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅' if success else '❌'} {test_name}: {'PASSED' if success else 'FAILED'}")
        
        # Summary
        print("\n📊 Test Summary:")
        print("=" * 50)
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Ollama LLM is ready for production.")
        else:
            print("⚠️ Some tests failed. Please check the configuration.")
        
        return passed == total

def main():
    """Main function"""
    try:
        tester = OllamaTester()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
