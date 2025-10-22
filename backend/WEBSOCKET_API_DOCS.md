# WebSocket API Documentation

This document provides comprehensive documentation for the Loglytics AI WebSocket API, including connection details, message formats, and usage examples.

## Overview

The WebSocket API provides real-time communication for:
- **Chat Streaming**: Real-time chat with LLM response streaming
- **Live Logs**: Real-time log streaming and monitoring
- **Notifications**: Real-time user notifications and alerts

## Authentication

All WebSocket connections require JWT authentication. Include the token in the connection URL:

```
ws://api/v1/chat/ws/{chat_id}?token=<jwt_token>
ws://api/v1/live-logs/ws/{project_id}?token=<jwt_token>
ws://api/v1/notifications/ws?token=<jwt_token>
```

Alternatively, you can include the token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Connection Management

### Connection Lifecycle

1. **Connect**: Client establishes WebSocket connection with authentication
2. **Authenticate**: Server validates JWT token and user permissions
3. **Subscribe**: Client subscribes to specific resources (chat, project, etc.)
4. **Communicate**: Bidirectional message exchange
5. **Disconnect**: Client closes connection or server terminates due to error

### Heartbeat/Ping

Clients should send periodic ping messages to maintain connection:

```json
{
  "type": "ping",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

Server responds with pong:

```json
{
  "type": "pong",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Chat WebSocket API

**Endpoint**: `ws://api/v1/chat/ws/{chat_id}`

### Connection

```javascript
const chatSocket = new WebSocket('ws://api/v1/chat/ws/chat_123?token=your_jwt_token');

chatSocket.onopen = function(event) {
    console.log('Connected to chat');
};

chatSocket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    handleChatMessage(message);
};
```

### Message Types

#### User Message
Send a message to the chat:

```json
{
  "type": "user_message",
  "content": "Hello, how can I analyze my logs?",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Typing Indicator
Indicate when user is typing:

```json
{
  "type": "typing",
  "is_typing": true,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Get Chat History
Request chat history:

```json
{
  "type": "get_chat_history",
  "limit": 50,
  "offset": 0,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Server Messages

#### User Message Broadcast
When a user sends a message:

```json
{
  "type": "user_message",
  "message_id": "msg_123",
  "chat_id": "chat_123",
  "user_id": "user_456",
  "content": "Hello, how can I analyze my logs?",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Assistant Message Start
When LLM starts responding:

```json
{
  "type": "assistant_message_start",
  "message_id": "msg_124",
  "chat_id": "chat_123",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Assistant Message Token
Each token of the LLM response:

```json
{
  "type": "assistant_message_token",
  "message_id": "msg_124",
  "chat_id": "chat_123",
  "token": "I can help you analyze your logs. ",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Assistant Message End
When LLM finishes responding:

```json
{
  "type": "assistant_message_end",
  "message_id": "msg_124",
  "chat_id": "chat_123",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Chat History
Response to get_chat_history:

```json
{
  "type": "chat_history",
  "chat_id": "chat_123",
  "messages": [
    {
      "id": "msg_123",
      "role": "user",
      "content": "Hello, how can I analyze my logs?",
      "timestamp": "2024-01-01T10:00:00Z",
      "user_id": "user_456"
    },
    {
      "id": "msg_124",
      "role": "assistant",
      "content": "I can help you analyze your logs...",
      "timestamp": "2024-01-01T10:00:01Z",
      "user_id": null
    }
  ],
  "has_more": false,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Typing Indicator
When someone is typing:

```json
{
  "type": "typing",
  "chat_id": "chat_123",
  "user_id": "user_456",
  "is_typing": true,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Error Messages
When an error occurs:

```json
{
  "type": "error",
  "message": "Failed to process message",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Live Logs WebSocket API

**Endpoint**: `ws://api/v1/live-logs/ws/{project_id}`

### Connection

```javascript
const logsSocket = new WebSocket('ws://api/v1/live-logs/ws/project_123?token=your_jwt_token');

logsSocket.onopen = function(event) {
    console.log('Connected to live logs');
};

logsSocket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    handleLogMessage(message);
};
```

### Message Types

#### Set Filters
Configure log filtering:

```json
{
  "type": "set_filters",
  "filters": {
    "level": ["ERROR", "WARN"],
    "source": ["application", "database"],
    "time_range": {
      "start": "2024-01-01T00:00:00Z",
      "end": "2024-01-01T23:59:59Z"
    }
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Request Stats
Request real-time statistics:

```json
{
  "type": "request_stats",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Request Recent Logs
Request recent log entries:

```json
{
  "type": "request_logs",
  "limit": 100,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Server Messages

#### Log Entry
New log entry received:

```json
{
  "type": "log_entry",
  "project_id": "project_123",
  "log": {
    "id": "log_456",
    "timestamp": "2024-01-01T10:00:00Z",
    "level": "ERROR",
    "message": "Database connection failed",
    "source": "application",
    "metadata": {
      "request_id": "req_789",
      "user_id": "user_123"
    }
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Stats Update
Real-time statistics:

```json
{
  "type": "stats_update",
  "project_id": "project_123",
  "stats": {
    "total_logs": 1500,
    "error_count": 25,
    "warning_count": 100,
    "log_rate": 10.5,
    "last_update": "2024-01-01T10:00:00Z"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Recent Logs
Response to request_logs:

```json
{
  "type": "recent_logs",
  "project_id": "project_123",
  "logs": [
    {
      "id": "log_456",
      "timestamp": "2024-01-01T10:00:00Z",
      "level": "ERROR",
      "message": "Database connection failed",
      "source": "application"
    }
  ],
  "count": 1,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Alert
Alert triggered:

```json
{
  "type": "alert",
  "project_id": "project_123",
  "alert": {
    "id": "alert_789",
    "type": "error_rate_threshold",
    "message": "Error rate exceeded 5%",
    "severity": "high",
    "timestamp": "2024-01-01T10:00:00Z"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Filters Updated
Confirmation of filter update:

```json
{
  "type": "filters_updated",
  "filters": {
    "level": ["ERROR", "WARN"],
    "source": ["application", "database"]
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Notifications WebSocket API

**Endpoint**: `ws://api/v1/notifications/ws`

### Connection

```javascript
const notificationSocket = new WebSocket('ws://api/v1/notifications/ws?token=your_jwt_token');

notificationSocket.onopen = function(event) {
    console.log('Connected to notifications');
};

notificationSocket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    handleNotification(message);
};
```

### Message Types

#### Mark Read
Mark notification as read:

```json
{
  "type": "mark_read",
  "notification_id": "notif_123",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Mark All Read
Mark all notifications as read:

```json
{
  "type": "mark_all_read",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Get Notifications
Request notification list:

```json
{
  "type": "get_notifications",
  "limit": 50,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Server Messages

#### Notification
New notification received:

```json
{
  "type": "notification",
  "notification_id": "notif_123",
  "title": "New Alert",
  "message": "Error rate exceeded threshold",
  "notification_type": "alert",
  "created_at": "2024-01-01T10:00:00Z",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Notification List
Response to get_notifications:

```json
{
  "type": "notification_list",
  "notifications": [
    {
      "id": "notif_123",
      "title": "New Alert",
      "message": "Error rate exceeded threshold",
      "type": "alert",
      "read": false,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "count": 1,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Task Progress
Long-running task progress update:

```json
{
  "type": "task_progress",
  "task_id": "task_456",
  "progress": 75,
  "message": "Processing log file...",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Marked Read
Confirmation of marking notification as read:

```json
{
  "type": "marked_read",
  "notification_id": "notif_123",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### All Marked Read
Confirmation of marking all notifications as read:

```json
{
  "type": "all_marked_read",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Error Handling

### Connection Errors

- **Authentication Failed**: Invalid or expired JWT token
- **Access Denied**: User doesn't have permission for the resource
- **Rate Limit Exceeded**: Too many messages sent too quickly
- **Invalid Message**: Malformed or invalid message format

### Error Response Format

```json
{
  "type": "error",
  "message": "Error description",
  "error_code": "AUTHENTICATION_FAILED",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Reconnection Strategy

Clients should implement automatic reconnection with exponential backoff:

```javascript
class WebSocketClient {
    constructor(url, token) {
        this.url = url;
        this.token = token;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
    }
    
    connect() {
        this.socket = new WebSocket(`${this.url}?token=${this.token}`);
        
        this.socket.onopen = () => {
            console.log('Connected');
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000;
        };
        
        this.socket.onclose = () => {
            this.handleReconnect();
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
                console.log(`Reconnecting... attempt ${this.reconnectAttempts + 1}`);
                this.reconnectAttempts++;
                this.reconnectDelay *= 2; // Exponential backoff
                this.connect();
            }, this.reconnectDelay);
        }
    }
}
```

## Rate Limiting

### Limits

- **Messages per minute**: 60 messages per connection
- **Connections per user**: 5 concurrent connections
- **Message size**: 1MB maximum per message

### Rate Limit Response

When rate limit is exceeded:

```json
{
  "type": "error",
  "message": "Rate limit exceeded. Please slow down.",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Security

### Message Sanitization

All incoming messages are sanitized to prevent XSS attacks:
- HTML tags are escaped (`<` → `&lt;`, `>` → `&gt;`)
- Script tags are neutralized
- Special characters are properly encoded

### Connection Security

- JWT token validation on every connection
- Resource access verification
- IP-based blocking for suspicious activity
- Connection timeout after 5 minutes of inactivity

## Performance

### Compression

Messages larger than 1KB are automatically compressed using gzip compression.

### Batching

High-frequency messages (like log entries) are batched to improve performance:
- Batch size: 10 messages
- Batch timeout: 100ms

### Backpressure

The system implements backpressure handling to prevent memory issues:
- Maximum queue size: 1000 messages per connection
- Drop threshold: 800 messages
- Automatic cleanup of old messages

## Monitoring

### Connection Statistics

Get WebSocket connection statistics:

```bash
GET /api/v1/ws/stats
```

Response:

```json
{
  "total_connections": 150,
  "total_users": 75,
  "project_subscriptions": 25,
  "chat_subscriptions": 10,
  "redis_connected": true,
  "status": "running"
}
```

### Health Checks

The system includes comprehensive health monitoring:
- Database connectivity
- Redis connectivity
- Worker status
- Memory usage
- Connection counts

## Examples

### Complete Chat Implementation

```javascript
class ChatClient {
    constructor(chatId, token) {
        this.chatId = chatId;
        this.token = token;
        this.socket = null;
        this.messageHistory = [];
    }
    
    connect() {
        this.socket = new WebSocket(`ws://api/v1/chat/ws/${this.chatId}?token=${this.token}`);
        
        this.socket.onopen = () => {
            console.log('Connected to chat');
            this.loadChatHistory();
        };
        
        this.socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.socket.onclose = () => {
            console.log('Disconnected from chat');
            this.reconnect();
        };
    }
    
    sendMessage(content) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'user_message',
                content: content,
                timestamp: new Date().toISOString()
            }));
        }
    }
    
    handleMessage(message) {
        switch (message.type) {
            case 'user_message':
                this.displayUserMessage(message);
                break;
            case 'assistant_message_start':
                this.startAssistantMessage(message);
                break;
            case 'assistant_message_token':
                this.appendAssistantToken(message);
                break;
            case 'assistant_message_end':
                this.endAssistantMessage(message);
                break;
            case 'typing':
                this.showTypingIndicator(message);
                break;
            case 'error':
                this.showError(message);
                break;
        }
    }
    
    loadChatHistory() {
        this.socket.send(JSON.stringify({
            type: 'get_chat_history',
            limit: 50,
            timestamp: new Date().toISOString()
        }));
    }
}
```

### Complete Live Logs Implementation

```javascript
class LiveLogsClient {
    constructor(projectId, token) {
        this.projectId = projectId;
        this.token = token;
        this.socket = null;
        this.filters = {};
    }
    
    connect() {
        this.socket = new WebSocket(`ws://api/v1/live-logs/ws/${this.projectId}?token=${this.token}`);
        
        this.socket.onopen = () => {
            console.log('Connected to live logs');
            this.requestStats();
        };
        
        this.socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
    }
    
    setFilters(filters) {
        this.filters = filters;
        this.socket.send(JSON.stringify({
            type: 'set_filters',
            filters: filters,
            timestamp: new Date().toISOString()
        }));
    }
    
    requestStats() {
        this.socket.send(JSON.stringify({
            type: 'request_stats',
            timestamp: new Date().toISOString()
        }));
    }
    
    handleMessage(message) {
        switch (message.type) {
            case 'log_entry':
                this.displayLogEntry(message.log);
                break;
            case 'stats_update':
                this.updateStats(message.stats);
                break;
            case 'alert':
                this.showAlert(message.alert);
                break;
            case 'filters_updated':
                console.log('Filters updated:', message.filters);
                break;
        }
    }
}
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check if the WebSocket server is running
2. **Authentication Failed**: Verify JWT token is valid and not expired
3. **Access Denied**: Ensure user has permission for the requested resource
4. **Rate Limit Exceeded**: Reduce message frequency or implement client-side throttling
5. **Connection Drops**: Implement reconnection logic with exponential backoff

### Debug Mode

Enable debug logging by setting the log level to DEBUG in your environment:

```bash
export LOG_LEVEL=DEBUG
```

This will provide detailed information about WebSocket connections, message processing, and error handling.

### Support

For additional support or questions about the WebSocket API, please:
1. Check the logs for error messages
2. Review the rate limiting and security sections
3. Test with the provided examples
4. Contact the development team with specific error details
