# 🚀 Live Logs System - Complete Implementation Guide

## Overview

The Live Logs system is a comprehensive real-time log monitoring and analysis platform that provides AI-powered insights, multi-platform support, and instant notifications. This system allows users to stream logs from various cloud platforms and Docker hosts, analyze them in real-time, and receive intelligent alerts.

## 🏗️ Architecture

### Backend Components

```
backend/
├── app/
│   ├── models/
│   │   └── live_log_connection.py          # Database models
│   ├── services/
│   │   └── live_logs/
│   │       ├── api_key_service.py          # API key management
│   │       ├── ai_analyzer.py              # AI analysis engine
│   │       └── background_tasks.py         # Background processing
│   ├── api/v1/endpoints/
│   │   └── live_logs.py                   # REST API endpoints
│   └── main.py                            # Background tasks integration
```

### Frontend Components

```
frontend/
├── src/
│   ├── app/dashboard/live-logs/
│   │   ├── page.tsx                       # Connection management
│   │   └── [connectionId]/page.tsx         # Log viewer
│   ├── components/live-logs/
│   │   └── alert-bell.tsx                 # Notification component
│   ├── hooks/
│   │   └── use-websocket-logs.ts          # WebSocket hook
│   ├── store/
│   │   └── live-logs-store.ts             # State management
│   └── services/
│       └── live-logs-service.ts           # API service
```

## 🚀 Features

### ✅ Core Features Implemented

1. **Multi-Platform Support**
   - AWS EKS/ECS
   - Azure AKS/Container Instances
   - Google Cloud GKE/Cloud Run
   - Docker Hosts

2. **Real-time Log Streaming**
   - WebSocket-based real-time updates
   - Historical log retrieval
   - Live log filtering and search

3. **AI-Powered Analysis**
   - Rule-based quick analysis
   - Deep AI analysis using LLM
   - Error and anomaly detection
   - Intelligent alert generation

4. **Notification System**
   - Real-time in-app notifications
   - Severity-based alerting
   - Unread count tracking
   - Mark as read functionality

5. **API Key Management**
   - Secure API key generation
   - Tenant-based isolation
   - Connection authentication

## 📊 Database Schema

### LiveLogConnection Model
```python
class LiveLogConnection(Base):
    __tablename__ = "live_log_connections"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    name = Column(String(255), nullable=False)
    platform = Column(Enum(CloudProvider), nullable=False)
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.INACTIVE)
    api_key_hash = Column(String(255), nullable=False)
    api_key_prefix = Column(String(20), nullable=False)
    tenant_id = Column(String(36), nullable=False)
    config = Column(JSON, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    total_logs_received = Column(Integer, default=0)
    logs_per_minute = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### LiveLog Model
```python
class LiveLog(Base):
    __tablename__ = "live_logs"
    
    id = Column(String(36), primary_key=True)
    connection_id = Column(String(36), ForeignKey("live_log_connections.id"))
    timestamp = Column(DateTime, nullable=False)
    log_level = Column(String(20), nullable=True)
    message = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    is_error = Column(Boolean, default=False)
    is_anomaly = Column(Boolean, default=False)
    analyzed = Column(Boolean, default=False)
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### LiveLogAlert Model
```python
class LiveLogAlert(Base):
    __tablename__ = "live_log_alerts"
    
    id = Column(String(36), primary_key=True)
    log_id = Column(String(36), ForeignKey("live_logs.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## 🔌 API Endpoints

### Connection Management
- `POST /api/v1/live-logs/connections` - Create new connection
- `GET /api/v1/live-logs/connections` - List user connections
- `GET /api/v1/live-logs/connections/{id}` - Get connection details
- `DELETE /api/v1/live-logs/connections/{id}` - Delete connection
- `POST /api/v1/live-logs/connections/{id}/test` - Test connection

### Log Ingestion
- `POST /api/v1/live-logs/ingest` - Ingest logs from agents
- `GET /api/v1/live-logs/ingest/test` - Test ingestion endpoint

### Real-time Streaming
- `WebSocket /api/v1/live-logs/ws/{connection_id}` - Real-time log stream
- `GET /api/v1/live-logs/connections/{id}/logs` - Get historical logs

### Alerts & Notifications
- `GET /api/v1/live-logs/alerts` - Get user alerts
- `PATCH /api/v1/live-logs/alerts/{id}/read` - Mark alert as read
- `GET /api/v1/live-logs/alerts/unread-count` - Get unread count

## 🤖 AI Analysis Engine

### Quick Analysis (Rule-based)
The system performs fast rule-based analysis to identify:
- **Error Detection**: Keywords like "error", "exception", "fatal", "failed"
- **Anomaly Detection**: Patterns like "timeout", "high latency", "out of memory"
- **Severity Classification**: Critical, High, Medium, Low

### Deep AI Analysis
For significant events, the system uses your LLM service to:
- Generate intelligent summaries
- Provide context-aware insights
- Suggest potential actions
- Create detailed alert descriptions

### Background Processing
- Analyzes logs every 10 seconds
- Processes unanalyzed logs in batches of 20
- Creates alerts for errors and anomalies
- Updates log analysis status

## 🔐 Security Features

### API Key Management
- SHA-256 hashed API keys
- Tenant-based isolation
- Secure key generation using secrets module
- Prefix-based key identification

### Authentication
- JWT-based user authentication
- User-specific data isolation
- Connection ownership validation
- Secure WebSocket connections

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL database
- Redis (optional, for caching)

### Backend Setup

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Database Migration**
```bash
# Run Alembic migrations
alembic upgrade head
```

3. **Start Backend Server**
```bash
cd backend
$env:PYTHONPATH = "."
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Start Development Server**
```bash
npm run dev
```

## 📱 Usage Guide

### 1. Creating a Connection

1. Navigate to **Live Logs** in the dashboard
2. Click **"+ New Connection"**
3. Select platform (AWS/Azure/GCP/Docker)
4. Enter connection name
5. Copy the generated API key and setup instructions

### 2. Configuring Log Forwarding

#### Docker Host Setup
```bash
# Create Fluent Bit config
cat > /etc/fluent-bit/fluent-bit.conf << EOF
[SERVICE]
    Flush 1
    Daemon Off
    Log_Level info

[INPUT]
    Name tail
    Path /var/lib/docker/containers/*/*.log
    Parser docker
    Tag docker.*

[OUTPUT]
    Name http
    Match *
    Host localhost
    Port 8000
    URI /api/v1/live-logs/ingest
    Header Authorization Bearer YOUR_API_KEY
    Header X-Tenant-ID YOUR_TENANT_ID
    Format json_lines
EOF

# Start Fluent Bit
fluent-bit -c /etc/fluent-bit/fluent-bit.conf
```

#### AWS EKS Setup
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: log-collector
---
apiVersion: v1
kind: Secret
metadata:
  name: ingest-credentials
  namespace: log-collector
type: Opaque
data:
  api-key: YOUR_BASE64_ENCODED_API_KEY
  tenant-id: YOUR_BASE64_ENCODED_TENANT_ID
```

### 3. Monitoring Logs

1. **Real-time View**: Click on any connection to view live logs
2. **Filtering**: Use level filters (ERROR, WARN, INFO)
3. **Search**: Search through log messages
4. **Pause/Play**: Control log streaming

### 4. Managing Alerts

1. **Notifications**: Check the bell icon in the top bar
2. **Alert Details**: Click on alerts to view details
3. **Mark as Read**: Click alerts to mark them as read
4. **Severity Levels**: 
   - 🔴 Critical: Fatal errors requiring immediate attention
   - 🟠 High: Errors that need prompt resolution
   - 🟡 Medium: Warnings and anomalies
   - 🔵 Low: Informational alerts

## 🔧 Configuration

### Environment Variables

#### Backend
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/loglytics

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Service
OLLAMA_BASE_URL=http://localhost:11434
OPENROUTER_API_KEY=your-openrouter-key
```

#### Frontend
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🧪 Testing

### Manual Testing

1. **Create Connection**
   - Go to Live Logs page
   - Create a Docker connection
   - Note the API key and tenant ID

2. **Send Test Logs**
```bash
curl -X POST http://localhost:8000/api/v1/live-logs/ingest \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "X-Tenant-ID: YOUR_TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "time": "2024-01-01T10:00:00Z",
      "log": "ERROR: Database connection failed",
      "level": "ERROR",
      "source": "api-server"
    }
  ]'
```

3. **Check Analysis**
   - Wait 10-15 seconds for AI analysis
   - Check the bell icon for notifications
   - View logs in the log viewer

### Automated Testing

The system includes comprehensive error handling and logging for monitoring:
- Background task health monitoring
- Database connection error handling
- WebSocket connection management
- API endpoint error responses

## 📈 Performance Considerations

### Backend Optimization
- Batch processing of logs (20 per batch)
- Async database operations
- Connection pooling
- Background task optimization

### Frontend Optimization
- WebSocket connection management
- Efficient state updates
- Debounced search and filtering
- Lazy loading of log entries

### Scalability
- Horizontal scaling support
- Database indexing optimization
- Redis caching (optional)
- Load balancer compatibility

## 🐛 Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check CORS configuration
   - Verify WebSocket URL
   - Check authentication token

2. **Background Tasks Not Running**
   - Verify server startup logs
   - Check database connectivity
   - Monitor background task logs

3. **Alerts Not Appearing**
   - Check AI analysis logs
   - Verify alert creation
   - Monitor unread count endpoint

4. **Log Ingestion Failed**
   - Verify API key and tenant ID
   - Check authentication headers
   - Monitor ingest endpoint logs

### Debug Mode

Enable debug logging:
```python
# In backend/app/main.py
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Updates and Maintenance

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Background Task Monitoring
- Monitor background task logs
- Check AI analysis performance
- Monitor alert generation rates

### Performance Monitoring
- Database query performance
- WebSocket connection counts
- API response times
- Background task execution times

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Fluent Bit Documentation](https://docs.fluentbit.io/)

### Support
- Check server logs for detailed error information
- Monitor background task execution
- Verify database connectivity
- Test API endpoints individually

## 🎯 Future Enhancements

### Planned Features
- [ ] Custom alert rules
- [ ] Log aggregation and metrics
- [ ] Dashboard analytics
- [ ] Multi-tenant support
- [ ] Log retention policies
- [ ] Export functionality
- [ ] Mobile notifications
- [ ] Advanced filtering options

### Integration Opportunities
- [ ] Slack notifications
- [ ] Email alerts
- [ ] PagerDuty integration
- [ ] Grafana dashboards
- [ ] Prometheus metrics

---

## 📄 License

This implementation is part of the Loglytics AI platform. All rights reserved.

## 🤝 Contributing

For contributions to the Live Logs system:
1. Follow the existing code structure
2. Add comprehensive tests
3. Update documentation
4. Ensure backward compatibility

---

**Last Updated**: October 28, 2025  
**Version**: 1.0.0  
**Status**: Production Ready ✅
