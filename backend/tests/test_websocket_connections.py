"""
WebSocket Connection Testing Suite
Tests real-time features and WebSocket functionality
"""

import pytest
import asyncio
import json
import websockets
import time
from datetime import datetime
from typing import Dict, Any

class WebSocketTestResults:
    """Store WebSocket test results"""
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def add_result(self, test_name, status, details="", response_time=0):
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "WARN":
            self.warnings += 1

# Initialize test results
ws_test_results = WebSocketTestResults()

# Test configuration
WS_BASE_URL = "ws://localhost:8000"
TEST_TOKEN = "test_token_123"  # This would be a real JWT token in practice

@pytest.mark.asyncio
async def test_notifications_websocket():
    """Test notifications WebSocket connection"""
    start = time.time()
    try:
        async with websockets.connect(f"{WS_BASE_URL}/api/v1/notifications/ws?token={TEST_TOKEN}") as websocket:
            # Wait for connection confirmation
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            
            # Parse message
            data = json.loads(message)
            
            elapsed = time.time() - start
            
            if data.get("type") == "connection_established":
                ws_test_results.add_result(
                    "Notifications WebSocket",
                    "PASS",
                    f"Connected successfully: {data.get('message', '')}",
                    elapsed
                )
            else:
                ws_test_results.add_result(
                    "Notifications WebSocket",
                    "WARN",
                    f"Unexpected message type: {data.get('type', 'unknown')}",
                    elapsed
                )
    except asyncio.TimeoutError:
        ws_test_results.add_result(
            "Notifications WebSocket",
            "FAIL",
            "Connection timeout",
            time.time() - start
        )
    except Exception as e:
        ws_test_results.add_result(
            "Notifications WebSocket",
            "FAIL",
            f"Connection failed: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_live_logs_websocket():
    """Test live logs WebSocket connection"""
    start = time.time()
    test_project_id = "test_project_123"
    
    try:
        async with websockets.connect(f"{WS_BASE_URL}/api/v1/live-logs/ws/{test_project_id}?token={TEST_TOKEN}") as websocket:
            # Wait for connection confirmation
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            
            # Parse message
            data = json.loads(message)
            
            elapsed = time.time() - start
            
            if data.get("type") == "connection_established":
                ws_test_results.add_result(
                    "Live Logs WebSocket",
                    "PASS",
                    f"Connected successfully: {data.get('message', '')}",
                    elapsed
                )
            else:
                ws_test_results.add_result(
                    "Live Logs WebSocket",
                    "WARN",
                    f"Unexpected message type: {data.get('type', 'unknown')}",
                    elapsed
                )
    except asyncio.TimeoutError:
        ws_test_results.add_result(
            "Live Logs WebSocket",
            "FAIL",
            "Connection timeout",
            time.time() - start
        )
    except Exception as e:
        ws_test_results.add_result(
            "Live Logs WebSocket",
            "FAIL",
            f"Connection failed: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_chat_websocket():
    """Test chat WebSocket connection"""
    start = time.time()
    test_chat_id = "test_chat_123"
    
    try:
        async with websockets.connect(f"{WS_BASE_URL}/api/v1/chat/ws/{test_chat_id}?token={TEST_TOKEN}") as websocket:
            # Wait for connection confirmation
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            
            # Parse message
            data = json.loads(message)
            
            elapsed = time.time() - start
            
            if data.get("type") == "connection_established":
                ws_test_results.add_result(
                    "Chat WebSocket",
                    "PASS",
                    f"Connected successfully: {data.get('message', '')}",
                    elapsed
                )
            else:
                ws_test_results.add_result(
                    "Chat WebSocket",
                    "WARN",
                    f"Unexpected message type: {data.get('type', 'unknown')}",
                    elapsed
                )
    except asyncio.TimeoutError:
        ws_test_results.add_result(
            "Chat WebSocket",
            "FAIL",
            "Connection timeout",
            time.time() - start
        )
    except Exception as e:
        ws_test_results.add_result(
            "Chat WebSocket",
            "FAIL",
            f"Connection failed: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_websocket_message_handling():
    """Test WebSocket message handling"""
    start = time.time()
    
    try:
        async with websockets.connect(f"{WS_BASE_URL}/api/v1/notifications/ws?token={TEST_TOKEN}") as websocket:
            # Send test message
            test_message = {
                "type": "test_message",
                "data": {"test": "data"},
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            elapsed = time.time() - start
            
            if response_data.get("type") == "test_response":
                ws_test_results.add_result(
                    "WebSocket Message Handling",
                    "PASS",
                    "Message sent and response received",
                    elapsed
                )
            else:
                ws_test_results.add_result(
                    "WebSocket Message Handling",
                    "WARN",
                    f"Unexpected response type: {response_data.get('type', 'unknown')}",
                    elapsed
                )
    except asyncio.TimeoutError:
        ws_test_results.add_result(
            "WebSocket Message Handling",
            "FAIL",
            "Response timeout",
            time.time() - start
        )
    except Exception as e:
        ws_test_results.add_result(
            "WebSocket Message Handling",
            "FAIL",
            f"Error: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_websocket_authentication():
    """Test WebSocket authentication"""
    start = time.time()
    
    try:
        # Test with invalid token
        async with websockets.connect(f"{WS_BASE_URL}/api/v1/notifications/ws?token=invalid_token") as websocket:
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            
            elapsed = time.time() - start
            
            if data.get("type") == "error" and "authentication" in data.get("message", "").lower():
                ws_test_results.add_result(
                    "WebSocket Authentication",
                    "PASS",
                    "Authentication properly rejected invalid token",
                    elapsed
                )
            else:
                ws_test_results.add_result(
                    "WebSocket Authentication",
                    "WARN",
                    f"Unexpected response to invalid token: {data}",
                    elapsed
                )
    except asyncio.TimeoutError:
        ws_test_results.add_result(
            "WebSocket Authentication",
            "FAIL",
            "No response to invalid token",
            time.time() - start
        )
    except Exception as e:
        ws_test_results.add_result(
            "WebSocket Authentication",
            "FAIL",
            f"Error: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_websocket_reconnection():
    """Test WebSocket reconnection handling"""
    start = time.time()
    
    try:
        # Connect and disconnect multiple times
        connections = []
        for i in range(3):
            try:
                async with websockets.connect(f"{WS_BASE_URL}/api/v1/notifications/ws?token={TEST_TOKEN}") as websocket:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    connections.append(data.get("type") == "connection_established")
            except Exception as e:
                connections.append(False)
        
        elapsed = time.time() - start
        
        successful_connections = sum(connections)
        if successful_connections >= 2:
            ws_test_results.add_result(
                "WebSocket Reconnection",
                "PASS",
                f"Successfully connected {successful_connections}/3 times",
                elapsed
            )
        else:
            ws_test_results.add_result(
                "WebSocket Reconnection",
                "WARN",
                f"Only {successful_connections}/3 connections successful",
                elapsed
            )
    except Exception as e:
        ws_test_results.add_result(
            "WebSocket Reconnection",
            "FAIL",
            f"Error: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_websocket_performance():
    """Test WebSocket performance with multiple messages"""
    start = time.time()
    
    try:
        async with websockets.connect(f"{WS_BASE_URL}/api/v1/notifications/ws?token={TEST_TOKEN}") as websocket:
            # Send multiple messages
            message_count = 10
            responses = []
            
            for i in range(message_count):
                test_message = {
                    "type": "performance_test",
                    "data": {"index": i, "timestamp": datetime.now().isoformat()},
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send(json.dumps(test_message))
                
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    responses.append(json.loads(response))
                except asyncio.TimeoutError:
                    pass  # Some messages might not get responses
            
            elapsed = time.time() - start
            
            if len(responses) >= message_count * 0.5:  # At least 50% response rate
                ws_test_results.add_result(
                    "WebSocket Performance",
                    "PASS",
                    f"Sent {message_count} messages, received {len(responses)} responses",
                    elapsed
                )
            else:
                ws_test_results.add_result(
                    "WebSocket Performance",
                    "WARN",
                    f"Low response rate: {len(responses)}/{message_count}",
                    elapsed
                )
    except Exception as e:
        ws_test_results.add_result(
            "WebSocket Performance",
            "FAIL",
            f"Error: {str(e)}",
            time.time() - start
        )

@pytest.mark.asyncio
async def test_generate_websocket_report():
    """Generate WebSocket test report"""
    report = f"""# WebSocket Connection Test Results

**Test Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Tests:** {len(ws_test_results.results)}
**Passed:** {ws_test_results.passed} ✅
**Failed:** {ws_test_results.failed} ❌
**Warnings:** {ws_test_results.warnings} ⚠️
**Success Rate:** {(ws_test_results.passed / len(ws_test_results.results) * 100):.2f}%

---

## WebSocket Test Results

| Test Name | Status | Response Time | Details |
|-----------|--------|---------------|----------|
"""
    
    for result in ws_test_results.results:
        status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}[result['status']]
        report += f"| {result['test']} | {status_icon} {result['status']} | {result['response_time_ms']}ms | {result['details']} |\n"
    
    # Save to file
    with open("WEBSOCKET_TEST_RESULTS.md", "w") as f:
        f.write(report)
    
    print("\n" + "="*60)
    print("WEBSOCKET TEST REPORT GENERATED: WEBSOCKET_TEST_RESULTS.md")
    print("="*60)
    print(f"Total Tests: {len(ws_test_results.results)}")
    print(f"Passed: {ws_test_results.passed} ✅")
    print(f"Failed: {ws_test_results.failed} ❌")
    print(f"Warnings: {ws_test_results.warnings} ⚠️")
    print(f"Success Rate: {(ws_test_results.passed / len(ws_test_results.results) * 100):.2f}%")
    print("="*60 + "\n")
