# Loglytics AI

A comprehensive AI-powered log analytics platform built with FastAPI and Next.js 14. Analyze, monitor, and gain insights from your application logs using advanced machine learning and natural language processing.

## Features

### 🔍 **Log Analysis**
- Upload and parse various log formats (JSON, CSV, plain text)
- Intelligent log parsing with automatic field extraction
- Pattern recognition and anomaly detection
- Real-time log streaming and monitoring

### 🤖 **AI-Powered Insights**
- Natural language chat interface for log queries
- RAG (Retrieval-Augmented Generation) for contextual responses
- Automated log analysis and recommendations
- Integration with OpenAI and Anthropic models

### 📊 **Analytics Dashboard**
- Interactive visualizations and charts
- Error rate monitoring and trending
- Performance metrics and statistics
- Customizable dashboards and reports

### 🔄 **Real-time Monitoring**
- Live log streaming with WebSocket support
- Real-time anomaly detection
- Alert notifications and thresholds
- Historical data comparison

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and real-time features
- **SQLAlchemy** - ORM and database management
- **Alembic** - Database migrations
- **OpenAI/Anthropic** - AI/LLM integration
- **FAISS** - Vector similarity search for RAG

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Modern UI components
- **Zustand** - State management
- **Axios** - HTTP client

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-service orchestration
- **Nginx** - Reverse proxy and load balancing

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.10+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd loglytics-ai
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```
   
   Edit the `.env` files with your configuration:
   - Add your OpenAI API key
   - Update database credentials if needed
   - Configure other settings as required

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Database Setup**
   - Install PostgreSQL locally
   - Create database: `loglytics_ai`
   - Update connection string in `backend/.env`

## Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://postgres:Rashan12@localhost:5432/loglytics_ai

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM APIs
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# File Upload
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_DIR=uploads
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret
```

## API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/logs/upload` - Upload log files
- `GET /api/v1/logs` - List log files
- `GET /api/v1/analytics/stats/overview` - Get analytics overview
- `POST /api/v1/chat/sessions/{id}/messages` - Send chat message
- `GET /api/v1/logs/{id}/stream` - Stream live logs

## Project Structure

```
loglytics-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # API endpoints
│   │   ├── models/               # Database models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   └── core/                 # Core utilities
│   ├── alembic/                  # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                  # Next.js app router
│   │   ├── components/           # React components
│   │   ├── services/             # API services
│   │   └── lib/                  # Utilities
│   └── package.json
├── nginx/                        # Nginx configuration
├── docker-compose.yml
└── README.md
```

## Features in Detail

### Log Processing
- Supports multiple log formats (JSON, CSV, plain text)
- Automatic timestamp and log level extraction
- IP address and user agent parsing
- Thread and session ID detection

### AI Integration
- Chat interface for natural language queries
- RAG system for contextual log analysis
- Pattern recognition and anomaly detection
- Automated insights and recommendations

### Real-time Features
- WebSocket-based live log streaming
- Real-time analytics updates
- Live anomaly detection
- Real-time chat responses

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation at `/docs`
- Review the API documentation at `/api/docs`

## Roadmap

- [ ] Advanced log parsing patterns
- [ ] Custom dashboard builder
- [ ] Alert and notification system
- [ ] Multi-tenant support
- [ ] Advanced ML models for anomaly detection
- [ ] Log correlation and tracing
- [ ] Export and reporting features
