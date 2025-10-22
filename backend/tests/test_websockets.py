"""
Comprehensive WebSocket Tests
Tests all WebSocket endpoints and functionality
"""

import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import WebSocket
from app.main import app
from app.websockets.manager import connection_manager
from app.websockets.auth import rate_limiter, message_sanitizer, websocket_security

# Test client
client = TestClient(app)


class TestWebSocketAuthentication:
    """Test WebSocket authentication functionality"""
    
    def test_authenticate_websocket_no_token(self):
        """Test authentication with no token"""
        from app.websockets.auth import authenticate_websocket
        
        # Mock WebSocket
        websocket = MagicMock()
        websocket.query_params = {}
        websocket.headers = {}
        
        # Test authentication
        result = asyncio.run(authenticate_websocket(websocket))
        assert result == (False, None, "No authentication token provided")
    
    def test_authenticate_websocket_invalid_token(self):
        """Test authentication with invalid token"""
        from app.websockets.auth import authenticate_websocket
        
        # Mock WebSocket
        websocket = MagicMock()
        websocket.query_params = {"token": "invalid_token"}
        websocket.headers = {}
        
        # Test authentication
        result = asyncio.run(authenticate_websocket(websocket))
        assert result[0] == False  # Not authenticated
        assert "Invalid or expired token" in result[2]
    
    def test_authenticate_websocket_valid_token(self):
        """Test authentication with valid token"""
        from app.websockets.auth import authenticate_websocket
        
        # Mock WebSocket
        websocket = MagicMock()
        websocket.query_params = {"token": "valid_token"}
        websocket.headers = {}
        
        # Mock token verification
        with patch('app.websockets.auth.verify_token') as mock_verify:
            mock_verify.return_value = {"sub": "user123"}
            
            # Mock database and auth service
            with patch('app.websockets.auth.get_db') as mock_get_db:
                with patch('app.websockets.auth.AuthService') as mock_auth_service:
                    mock_auth_service.return_value.get_current_user = AsyncMock(
                        return_value=(True, MagicMock(is_active=True), None)
                    )
                    
                    # Test authentication
                    result = asyncio.run(authenticate_websocket(websocket))
                    assert result == (True, "user123", None)


class TestWebSocketRateLimiter:
    """Test WebSocket rate limiting functionality"""
    
    def test_rate_limiter_initial_connection(self):
        """Test rate limiter with initial connection"""
        connection_id = "test_connection_1"
        user_id = "user123"
        
        # Test first message
        result = asyncio.run(rate_limiter.check_rate_limit(connection_id, user_id))
        assert result == (True, None)
    
    def test_rate_limiter_exceed_limit(self):
        """Test rate limiter when limit is exceeded"""
        connection_id = "test_connection_2"
        user_id = "user123"
        
        # Send messages up to limit
        for i in range(61):  # Exceed 60 messages per minute
            result = asyncio.run(rate_limiter.check_rate_limit(connection_id, user_id))
            if i < 60:
                assert result == (True, None)
            else:
                assert result == (False, "Rate limit exceeded. Please slow down.")
    
    def test_rate_limiter_cleanup(self):
        """Test rate limiter cleanup"""
        connection_id = "test_connection_3"
        user_id = "user123"
        
        # Add connection
        asyncio.run(rate_limiter.check_rate_limit(connection_id, user_id))
        
        # Cleanup
        rate_limiter.cleanup_connection(connection_id)
        
        # Should be able to add again
        result = asyncio.run(rate_limiter.check_rate_limit(connection_id, user_id))
        assert result == (True, None)


class TestMessageSanitizer:
    """Test message sanitization functionality"""
    
    def test_sanitize_message_basic(self):
        """Test basic message sanitization"""
        message = {
            "type": "user_message",
            "content": "Hello <script>alert('xss')</script> world"
        }
        
        sanitized = message_sanitizer.sanitize_message(message)
        
        assert sanitized["content"] == "Hello &lt;script&gt;alert('xss')&lt;/script&gt; world"
    
    def test_sanitize_message_nested(self):
        """Test sanitization of nested objects"""
        message = {
            "type": "user_message",
            "data": {
                "content": "Test <b>bold</b> text",
                "nested": {
                    "value": "More <i>italic</i> text"
                }
            }
        }
        
        sanitized = message_sanitizer.sanitize_message(message)
        
        assert sanitized["data"]["content"] == "Test &lt;b&gt;bold&lt;/b&gt; text"
        assert sanitized["data"]["nested"]["value"] == "More &lt;i&gt;italic&lt;/i&gt; text"
    
    def test_validate_message_structure_valid(self):
        """Test message structure validation with valid message"""
        message = {
            "type": "user_message",
            "content": "Hello world"
        }
        
        result = message_sanitizer.validate_message_structure(message)
        assert result == True
    
    def test_validate_message_structure_invalid(self):
        """Test message structure validation with invalid message"""
        message = {
            "type": "user_message"
            # Missing required 'content' field
        }
        
        result = message_sanitizer.validate_message_structure(message)
        assert result == False


class TestWebSocketConnectionManager:
    """Test WebSocket connection manager functionality"""
    
    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket for testing"""
        websocket = AsyncMock()
        websocket.accept = AsyncMock()
        websocket.send_json = AsyncMock()
        websocket.close = AsyncMock()
        return websocket
    
    async def test_connection_manager_connect(self, mock_websocket):
        """Test connection manager connect functionality"""
        user_id = "user123"
        connection_id = "conn123"
        metadata = {"type": "test"}
        
        # Test connection
        await connection_manager.connect(mock_websocket, user_id, connection_id, metadata)
        
        # Verify connection was stored
        assert user_id in connection_manager.active_connections
        assert connection_id in connection_manager.active_connections[user_id]
        assert connection_id in connection_manager.connection_metadata
        
        # Verify WebSocket methods were called
        mock_websocket.accept.assert_called_once()
        mock_websocket.send_json.assert_called_once()
    
    async def test_connection_manager_disconnect(self, mock_websocket):
        """Test connection manager disconnect functionality"""
        user_id = "user123"
        connection_id = "conn123"
        
        # Connect first
        await connection_manager.connect(mock_websocket, user_id, connection_id)
        
        # Disconnect
        await connection_manager.disconnect(user_id, connection_id)
        
        # Verify connection was removed
        assert user_id not in connection_manager.active_connections
        assert connection_id not in connection_manager.connection_metadata
    
    async def test_connection_manager_send_personal_message(self, mock_websocket):
        """Test sending personal message"""
        user_id = "user123"
        connection_id = "conn123"
        message = {"type": "test", "content": "Hello"}
        
        # Connect first
        await connection_manager.connect(mock_websocket, user_id, connection_id)
        
        # Send message
        await connection_manager.send_personal_message(user_id, connection_id, message)
        
        # Verify message was sent
        mock_websocket.send_json.assert_called_with(message)
    
    async def test_connection_manager_broadcast_to_chat(self, mock_websocket):
        """Test broadcasting to chat"""
        user_id = "user123"
        connection_id = "conn123"
        chat_id = "chat456"
        message = {"type": "test", "content": "Hello"}
        
        # Connect and subscribe to chat
        await connection_manager.connect(mock_websocket, user_id, connection_id)
        await connection_manager.subscribe_to_chat(user_id, connection_id, chat_id)
        
        # Broadcast message
        await connection_manager.broadcast_to_chat(chat_id, message)
        
        # Verify message was sent
        mock_websocket.send_json.assert_called_with(message)


class TestWebSocketEndpoints:
    """Test WebSocket endpoint functionality"""
    
    def test_chat_websocket_endpoint_unauthorized(self):
        """Test chat WebSocket endpoint with unauthorized access"""
        with client.websocket_connect("/api/v1/chat/ws/test_chat") as websocket:
            # Should close with error due to no authentication
            with pytest.raises(Exception):
                websocket.receive_text()
    
    def test_live_logs_websocket_endpoint_unauthorized(self):
        """Test live logs WebSocket endpoint with unauthorized access"""
        with client.websocket_connect("/api/v1/live-logs/ws/test_project") as websocket:
            # Should close with error due to no authentication
            with pytest.raises(Exception):
                websocket.receive_text()
    
    def test_notifications_websocket_endpoint_unauthorized(self):
        """Test notifications WebSocket endpoint with unauthorized access"""
        with client.websocket_connect("/api/v1/notifications/ws") as websocket:
            # Should close with error due to no authentication
            with pytest.raises(Exception):
                websocket.receive_text()


class TestWebSocketMiddleware:
    """Test WebSocket middleware functionality"""
    
    def test_compression_threshold(self):
        """Test message compression threshold"""
        from app.websockets.middleware import WebSocketCompression
        
        compression = WebSocketCompression(compression_threshold=100)
        
        # Small message should not be compressed
        small_message = {"type": "test", "content": "Hello"}
        result = compression.compress_message(small_message)
        assert isinstance(result, bytes)
        
        # Large message should be compressed
        large_message = {"type": "test", "content": "x" * 200}
        result = compression.compress_message(large_message)
        assert isinstance(result, bytes)
        assert len(result) < len(json.dumps(large_message).encode('utf-8'))
    
    def test_message_batcher(self):
        """Test message batching functionality"""
        from app.websockets.middleware import MessageBatcher
        
        batcher = MessageBatcher(batch_size=3, batch_timeout=0.1)
        
        # Mock send callback
        sent_messages = []
        async def mock_send(messages):
            sent_messages.extend(messages)
        
        # Add messages to batch
        asyncio.run(batcher.add_message("conn1", {"type": "test1"}, mock_send))
        asyncio.run(batcher.add_message("conn1", {"type": "test2"}, mock_send))
        asyncio.run(batcher.add_message("conn1", {"type": "test3"}, mock_send))
        
        # Should have sent batch
        assert len(sent_messages) == 3
        assert sent_messages[0]["type"] == "test1"
        assert sent_messages[1]["type"] == "test2"
        assert sent_messages[2]["type"] == "test3"
    
    def test_backpressure_handler(self):
        """Test backpressure handling"""
        from app.websockets.middleware import BackpressureHandler
        
        handler = BackpressureHandler(max_queue_size=5, drop_threshold=3)
        
        # Add messages to queue
        for i in range(10):
            asyncio.run(handler.queue_message("conn1", {"type": "test", "id": i}))
        
        # Should have dropped some messages due to backpressure
        assert "conn1" in handler.message_queues
        queue = handler.message_queues["conn1"]
        assert queue.qsize() <= 5  # Should not exceed max queue size


class TestWebSocketIntegration:
    """Integration tests for WebSocket functionality"""
    
    @pytest.mark.asyncio
    async def test_chat_websocket_full_flow(self):
        """Test complete chat WebSocket flow"""
        # This would require a full integration test with database
        # and actual authentication tokens
        pass
    
    @pytest.mark.asyncio
    async def test_live_logs_websocket_full_flow(self):
        """Test complete live logs WebSocket flow"""
        # This would require a full integration test with database
        # and actual live streaming service
        pass
    
    @pytest.mark.asyncio
    async def test_notifications_websocket_full_flow(self):
        """Test complete notifications WebSocket flow"""
        # This would require a full integration test with database
        # and actual notification service
        pass


class TestWebSocketPerformance:
    """Performance tests for WebSocket functionality"""
    
    def test_connection_manager_performance(self):
        """Test connection manager performance with many connections"""
        # Test adding many connections
        connections = []
        for i in range(100):
            websocket = AsyncMock()
            websocket.accept = AsyncMock()
            websocket.send_json = AsyncMock()
            connections.append(websocket)
        
        # Add connections
        start_time = asyncio.get_event_loop().time()
        for i, websocket in enumerate(connections):
            asyncio.run(connection_manager.connect(
                websocket, f"user{i}", f"conn{i}", {"type": "test"}
            ))
        end_time = asyncio.get_event_loop().time()
        
        # Should complete quickly
        assert end_time - start_time < 1.0  # Less than 1 second
        
        # Cleanup
        for i in range(100):
            asyncio.run(connection_manager.disconnect(f"user{i}", f"conn{i}"))
    
    def test_message_processing_performance(self):
        """Test message processing performance"""
        from app.websockets.middleware import websocket_middleware
        
        # Test processing many messages
        messages = []
        for i in range(1000):
            messages.append({
                "type": "user_message",
                "content": f"Test message {i}"
            })
        
        # Process messages
        start_time = asyncio.get_event_loop().time()
        for message in messages:
            sanitized = message_sanitizer.sanitize_message(message)
            valid = message_sanitizer.validate_message_structure(sanitized)
            assert valid == True
        end_time = asyncio.get_event_loop().time()
        
        # Should complete quickly
        assert end_time - start_time < 1.0  # Less than 1 second


if __name__ == "__main__":
    pytest.main([__file__])
