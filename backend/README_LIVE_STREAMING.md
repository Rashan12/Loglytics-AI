# Live Log Streaming Service

Real-time log streaming service with cloud provider integrations for AWS CloudWatch, Azure Monitor, and Google Cloud Logging.

## 🚀 Features

### Cloud Provider Integrations
- **AWS CloudWatch**: Real-time log streaming from CloudWatch Logs
- **Azure Monitor**: Log Analytics workspace integration with KQL queries
- **Google Cloud Logging**: Cloud Logging API integration with resource filtering

### Real-Time Processing
- **Stream Management**: Start/stop/pause log streams
- **Live Processing**: Parse, normalize, and store logs in real-time
- **WebSocket Broadcasting**: Real-time log delivery to frontend
- **Alert Engine**: Pattern detection and alert triggering

### Security & Encryption
- **Credential Encryption**: Secure storage of cloud provider credentials
- **Authentication**: JWT-based API authentication
- **Data Isolation**: Project-level data separation

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cloud APIs    │───▶│  Stream Manager  │───▶│  Stream Processor│
│ (AWS/Azure/GCP) │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   WebSocket     │◀───│ WebSocket        │◀───│   Alert Engine  │
│   Clients       │    │ Broadcaster      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   Database      │
                                               │ (TimescaleDB)   │
                                               └─────────────────┘
```

## 📁 File Structure

```
backend/app/services/live_stream/
├── __init__.py
├── stream_manager.py              # Main stream orchestration
├── stream_processor.py            # Real-time log processing
├── alert_engine.py               # Pattern detection and alerts
├── websocket_broadcaster.py      # WebSocket communication
└── cloud_connectors/
    ├── __init__.py
    ├── aws_cloudwatch.py         # AWS CloudWatch integration
    ├── azure_monitor.py          # Azure Monitor integration
    └── gcp_logging.py            # GCP Cloud Logging integration
```

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

```bash
# Credential encryption key (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
CREDENTIAL_ENCRYPTION_KEY=your_encryption_key_here

# Redis configuration
REDIS_URL=redis://localhost:6379

# Database configuration
DATABASE_URL=postgresql://user:password@localhost/loglytics_db
```

### 3. Cloud Provider Setup

#### AWS CloudWatch
```python
# Required permissions:
# - logs:DescribeLogGroups
# - logs:DescribeLogStreams
# - logs:GetLogEvents

credentials = {
    "access_key_id": "AKIA...",
    "secret_access_key": "...",
    "region": "us-east-1",
    "log_group": "/aws/lambda/my-function",
    "log_streams": ["2024/01/01/[$LATEST]abc123"]  # Optional
}
```

#### Azure Monitor
```python
# Required permissions:
# - Log Analytics Reader role

credentials = {
    "workspace_id": "your-workspace-id",
    "tenant_id": "your-tenant-id",
    "client_id": "your-client-id",
    "client_secret": "your-client-secret",
    "query": "AppTraces | where TimeGenerated > ago(1h)"
}
```

#### Google Cloud Logging
```python
# Required permissions:
# - Logs Viewer role

credentials = {
    "project_id": "your-project-id",
    "log_name": "projects/your-project/logs/your-log",
    "resource_type": "gce_instance",
    "credentials_json": {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "...",
        "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
        "client_email": "service-account@your-project.iam.gserviceaccount.com",
        "client_id": "..."
    }
}
```

## 🚀 Usage

### 1. Create Connection

```python
# POST /api/v1/live-logs/connections
{
    "project_id": "your-project-id",
    "connection_name": "AWS Production Logs",
    "cloud_provider": "aws",
    "connection_config": {
        "access_key_id": "AKIA...",
        "secret_access_key": "...",
        "region": "us-east-1",
        "log_group": "/aws/lambda/my-function"
    }
}
```

### 2. Test Connection

```python
# POST /api/v1/live-logs/connections/{connection_id}/test
# Returns: {"status": "success", "message": "Connection test successful"}
```

### 3. Start Streaming

```python
# POST /api/v1/live-logs/connections/{connection_id}/start
# Returns: {"message": "Streaming started successfully"}
```

### 4. WebSocket Connection

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/live-logs/ws/your-project-id?token=your-jwt-token');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'logs') {
        // Handle incoming logs
        console.log('New logs:', data.logs);
    } else if (data.type === 'alert') {
        // Handle alerts
        console.log('Alert:', data.alert);
    }
};
```

## 📊 API Endpoints

### Connection Management
- `POST /api/v1/live-logs/connections` - Create connection
- `GET /api/v1/live-logs/connections/{project_id}` - List connections
- `GET /api/v1/live-logs/connections/{connection_id}` - Get connection details
- `PUT /api/v1/live-logs/connections/{connection_id}` - Update connection
- `DELETE /api/v1/live-logs/connections/{connection_id}` - Delete connection

### Stream Control
- `POST /api/v1/live-logs/connections/{connection_id}/start` - Start streaming
- `POST /api/v1/live-logs/connections/{connection_id}/stop` - Stop streaming
- `POST /api/v1/live-logs/connections/{connection_id}/test` - Test connection

### Live Data
- `GET /api/v1/live-logs/stream/{project_id}` - Get recent live logs
- `GET /api/v1/live-logs/alerts/{project_id}` - Get active alerts
- `POST /api/v1/live-logs/alerts/{alert_id}/read` - Mark alert as read

### WebSocket
- `ws://api/v1/live-logs/ws/{project_id}?token={jwt_token}` - Real-time log stream

## 🚨 Alert Engine

### Alert Types

#### 1. Error Rate Alerts
```python
{
    "type": "error_rate",
    "threshold": 10,  # errors per minute
    "window_minutes": 5,
    "cooldown_minutes": 15
}
```

#### 2. Pattern Match Alerts
```python
{
    "type": "pattern_match",
    "pattern": r"(?i)(database|connection).*?(error|failed)",
    "case_sensitive": false,
    "cooldown_minutes": 10
}
```

#### 3. Log Level Alerts
```python
{
    "type": "log_level",
    "log_levels": ["CRITICAL", "FATAL"],
    "cooldown_minutes": 5
}
```

### Notification Channels
- **In-App**: Stored in database, displayed in UI
- **Email**: SendGrid/Amazon SES integration
- **Slack**: Webhook integration
- **Jira**: Ticket creation

## 🔒 Security

### Credential Encryption
All cloud provider credentials are encrypted using Fernet symmetric encryption:

```python
from app.core.credential_encryption import encrypt_credentials, decrypt_credentials

# Encrypt credentials before storing
encrypted = encrypt_credentials({
    "access_key_id": "AKIA...",
    "secret_access_key": "..."
})

# Decrypt when needed
decrypted = decrypt_credentials(encrypted)
```

### Authentication
- JWT tokens for API authentication
- WebSocket authentication via query parameter
- Project-level data isolation

## 🧪 Testing

### Run Tests
```bash
# Run comprehensive tests
python backend/scripts/test_live_streaming.py

# Run specific connector tests
python -c "
import asyncio
from backend.scripts.test_live_streaming import LiveStreamingTester
tester = LiveStreamingTester()
asyncio.run(tester.test_aws_connector())
"
```

### Test with Real Credentials
```python
# Set up test credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AZURE_TENANT_ID=your_tenant
export GCP_PROJECT_ID=your_project

# Run tests
python backend/scripts/test_live_streaming.py
```

## 📈 Performance

### Optimization Features
- **Batch Processing**: Process logs in batches of 100-500
- **Async Operations**: Non-blocking database and API calls
- **Connection Pooling**: Efficient database connections
- **Redis Pub/Sub**: Multi-instance broadcasting
- **Caching**: Alert rules and connection info caching

### Monitoring
- Stream health checks
- Error rate monitoring
- Connection statistics
- Performance metrics

## 🚀 Deployment

### Docker
```dockerfile
# Add to your Dockerfile
RUN pip install boto3 azure-monitor-query google-cloud-logging cryptography websockets
```

### Environment Setup
```bash
# Production environment variables
export CREDENTIAL_ENCRYPTION_KEY=your_production_key
export REDIS_URL=redis://redis:6379
export DATABASE_URL=postgresql://user:pass@db:5432/loglytics_db
```

### Scaling
- **Horizontal**: Multiple instances with Redis pub/sub
- **Vertical**: Optimize batch sizes and connection limits
- **Database**: Use read replicas for analytics queries

## 🔧 Troubleshooting

### Common Issues

#### 1. Connection Test Failures
```bash
# Check credentials
aws logs describe-log-groups --log-group-name-prefix /aws/lambda

# Check permissions
aws iam get-user
```

#### 2. WebSocket Connection Issues
```javascript
// Check authentication
const token = localStorage.getItem('jwt_token');
const ws = new WebSocket(`ws://localhost:8000/api/v1/live-logs/ws/project-id?token=${token}`);
```

#### 3. High Memory Usage
```python
# Reduce batch size
stream_processor.batch_size = 50

# Increase polling interval
stream_manager.poll_interval = 60  # seconds
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger('app.services.live_stream').setLevel(logging.DEBUG)
```

## 📚 Examples

### Complete Integration Example
```python
import asyncio
from app.services.live_stream.stream_manager import StreamManager

async def main():
    # Initialize stream manager
    stream_manager = StreamManager(db, redis)
    
    # Create connection
    connection_id = "aws-prod-logs"
    success = await stream_manager.start_stream(connection_id)
    
    if success:
        print("Stream started successfully")
        
        # Monitor for 5 minutes
        await asyncio.sleep(300)
        
        # Stop stream
        await stream_manager.stop_stream(connection_id)
        print("Stream stopped")
    else:
        print("Failed to start stream")

asyncio.run(main())
```

### Custom Alert Rule
```python
from app.services.live_stream.alert_engine import AlertRule, AlertType, AlertSeverity

custom_rule = AlertRule(
    id="custom_database_errors",
    project_id="my-project",
    name="Database Connection Errors",
    alert_type=AlertType.PATTERN_MATCH,
    severity=AlertSeverity.HIGH,
    enabled=True,
    conditions={
        "pattern": r"(?i)connection.*?refused|timeout.*?database",
        "case_sensitive": False
    },
    cooldown_minutes=10,
    notification_channels=["in_app", "email"]
)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

