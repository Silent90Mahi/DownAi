# SHG Backend API

FastAPI backend for the Ooumph SHG Smart Market Linkage Platform - an AI-powered ecosystem for Self-Help Groups.

## Features

- **6 AI Agents**: Vaani, Bazaar Buddhi, Jodi, Samagri, Vishwas, Sampark
- **Voice Processing**: Speech-to-text and text-to-speech via OpenAI
- **Real-time Communication**: WebSocket support for live updates
- **Market Intelligence**: Price trends, demand forecasting
- **Trust System**: Blockchain-based trust coins and verification
- **Payment Integration**: Razorpay payment gateway
- **Government Portal Integration**: GeM, ONDC, eSARAS (stub)

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL (production) or SQLite (development)
- Redis (optional, for caching)
- OpenAI API Key

### Installation

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set required variables:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   ```

4. **Initialize Database**
   ```bash
   python -c "from app.database import init_db; init_db()"
   ```

5. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload --port 6002
   ```

### Docker Setup

```bash
docker build -t ooumph-backend --target development .
docker run -p 6002:6002 --env-file .env ooumph-backend
```

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/token` | Login (OAuth2 password flow) |
| GET | `/me` | Get current user profile |
| PUT | `/me` | Update user profile |

### Chat/Vaani Agent (`/api/chat`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/process` | Process chat message through AI agent |
| POST | `/stream` | Stream AI response (SSE) |
| GET | `/history` | Get chat history |

### Voice Agent (`/api/voice`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transcribe` | Transcribe audio to text (Whisper) |
| POST | `/speak` | Convert text to speech (TTS) |

### Products (`/api/products`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all products |
| GET | `/{id}` | Get product details |
| POST | `/` | Create product (auth required) |
| PUT | `/{id}` | Update product |
| DELETE | `/{id}` | Delete product |

### Orders (`/api/orders`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List orders |
| GET | `/{id}` | Get order details |
| POST | `/` | Create order |
| PUT | `/{id}/status` | Update order status |

### Market Intelligence (`/api/market`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prices` | Get market prices |
| GET | `/trends` | Get price trends |
| GET | `/forecast` | Get demand forecast |

### Buyer Matching (`/api/matching`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/find` | Find matching buyers |
| GET | `/recommendations/{product_id}` | Get buyer recommendations |

### Suppliers/Materials (`/api/suppliers`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List suppliers |
| GET | `/{id}` | Get supplier details |
| GET | `/materials` | List available materials |

### Trust & Compliance (`/api/trust`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/score/{user_id}` | Get user trust score |
| POST | `/verify` | Submit verification documents |
| GET | `/coins/balance` | Get trust coins balance |

### Community (`/api/community`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/posts` | List community posts |
| POST | `/posts` | Create post |
| GET | `/events` | List community events |

### Payments (`/api/payments`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/create-order` | Create Razorpay order |
| POST | `/verify` | Verify payment signature |
| GET | `/history` | Get payment history |

### Analytics (`/api/analytics`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard` | Get dashboard analytics |
| GET | `/sales` | Get sales analytics |
| GET | `/performance` | Get performance metrics |

### Notifications (`/api/notifications`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List notifications |
| PUT | `/{id}/read` | Mark as read |
| WebSocket | `/ws` | Real-time notifications |

### Reports (`/api/reports`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sales` | Generate sales report |
| GET | `/inventory` | Generate inventory report |
| GET | `/export` | Export reports (PDF/Excel) |

### Offline Sync (`/api/sync`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload offline data |
| GET | `/download` | Download sync data |

## AI Agents

### 1. Vaani (Voice & Chat Assistant)
- Natural language processing
- Voice commands and responses
- Multi-language support

### 2. Bazaar Buddhi (Market Intelligence)
- Price trend analysis
- Demand forecasting
- Market recommendations

### 3. Jodi (Buyer Matching)
- Smart buyer-seller matching
- Recommendation engine
- Bulk order aggregation

### 4. Samagri (Supplier/Materials)
- Raw material sourcing
- Supplier verification
- Inventory management

### 5. Vishwas (Trust & Compliance)
- Trust score calculation
- Verification workflows
- Blockchain-based trust coins

### 6. Sampark (Community)
- Community forums
- Event management
- Knowledge sharing

## Development

### Project Structure

```
backend/
├── app/
│   ├── routers/          # API route handlers
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── products.py
│   │   └── ...
│   ├── services/         # Business logic
│   │   ├── agents.py
│   │   ├── market_service.py
│   │   └── ...
│   ├── integrations/     # External API clients
│   │   ├── gem.py
│   │   ├── ondc.py
│   │   └── ...
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database configuration
│   └── main.py           # FastAPI application
├── core/
│   ├── config.py         # Settings management
│   ├── logging.py        # Logging configuration
│   ├── cache.py          # Redis caching
│   └── rate_limit.py     # Rate limiting
├── tests/                # Test files
├── requirements.txt      # Dependencies
└── Dockerfile
```

### Running Tests

```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Code Quality

```bash
black app/ core/ tests/
flake8 app/ core/ tests/
```

### Database Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Testing

### Unit Tests

```bash
pytest tests/ -v
```

### Integration Tests

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

### Test Coverage

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Environment Variables

See [.env.example](./.env.example) for all configuration options.

### Required Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `SECRET_KEY` | JWT secret key |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./ooumph.db` | Database URL |
| `REDIS_URL` | `redis://localhost:6379` | Redis URL |
| `FRONTEND_URL` | `http://localhost:5173` | CORS origin |
| `DEBUG` | `false` | Debug mode |

## Deployment

### Production Build

```bash
docker build --target production -t ooumph-backend .
```

### Health Check

```bash
curl http://localhost:6002/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Ooumph SHG Ecosystem",
  "version": "1.0.0",
  "environment": "production",
  "features": {
    "websocket": true,
    "cache": true,
    "rate_limiting": true
  }
}
```

## Troubleshooting

### Database Connection Issues

```bash
python -c "from app.database import engine; engine.connect()"
```

### Redis Connection

```bash
redis-cli ping
```

### OpenAI API Test

```bash
python -c "import openai; openai.api_key='your_key'; print(openai.models.list())"
```
