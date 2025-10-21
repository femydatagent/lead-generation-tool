# 🏗️ Architecture Documentation

This document provides a comprehensive overview of the Lead Generation Tool's architecture, design patterns, and technical decisions.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Technology Stack](#technology-stack)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Database Design](#database-design)
- [API Design](#api-design)
- [Security Architecture](#security-architecture)
- [Scalability Considerations](#scalability-considerations)
- [Design Patterns](#design-patterns)

---

## 🌐 System Overview

The Lead Generation Tool is a full-stack web application that automates the process of finding and enriching business leads. It combines web scraping, AI-powered semantic analysis, and data enrichment from multiple sources to provide high-quality, actionable business intelligence.

### Key Capabilities

1. **Automated Data Collection**: Scrapes Google Maps for business information
2. **AI Semantic Analysis**: Uses intelligent algorithms to extract Instagram profiles and CNPJ numbers
3. **Multi-Source Enrichment**: Integrates with DataStone and Apify for additional data
4. **Real-Time Progress Tracking**: Asynchronous job processing with live status updates
5. **Export Functionality**: CSV download of enriched lead data

---

## 🎨 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Single Page Application (HTML/CSS/JavaScript)           │   │
│  │  - Form input (business type, location)                  │   │
│  │  - Real-time progress bar                                │   │
│  │  - Results display                                        │   │
│  │  - CSV download                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/REST API
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Flask Backend (Python)                                  │   │
│  │  ┌────────────────┐  ┌─────────────────┐                │   │
│  │  │ Leads Blueprint│  │  User Blueprint │                │   │
│  │  │ - Generate     │  │  - CRUD Ops     │                │   │
│  │  │ - Status       │  │                 │                │   │
│  │  │ - Download     │  │                 │                │   │
│  │  └────────────────┘  └─────────────────┘                │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
│ External APIs   │ │  Database   │ │ Supabase Backend │
├─────────────────┤ ├─────────────┤ ├──────────────────┤
│ • SerpApi       │ │ SQLite      │ │ Edge Functions:  │
│   (Google Maps) │ │ - Users     │ │ • process-leads  │
│                 │ │ - Jobs      │ │ • job-status     │
│ • DataStone     │ │ - Leads     │ │ • export-leads   │
│   (CNPJ Data)   │ │             │ │                  │
│                 │ │ PostgreSQL  │ │ PostgreSQL DB:   │
│ • Apify         │ │ (Supabase)  │ │ • profiles       │
│   (Instagram)   │ │ - Profiles  │ │ • api_keys       │
│                 │ │ - API Keys  │ │ • lead_jobs      │
│                 │ │ - Lead Jobs │ │ • leads          │
│                 │ │ - Leads     │ │ • usage_logs     │
└─────────────────┘ └─────────────┘ └──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Processing Pipeline                        │
│                                                                 │
│  1. Google Maps Search (25%)                                   │
│     ↓                                                           │
│  2. AI Semantic Analysis (50%)                                 │
│     ├─ Instagram Extraction (confidence scoring)               │
│     └─ CNPJ Extraction (pattern matching)                      │
│     ↓                                                           │
│  3. Data Enrichment (75%)                                      │
│     ├─ DataStone API (company data)                            │
│     └─ Apify API (Instagram details)                           │
│     ↓                                                           │
│  4. Results & Export (100%)                                    │
│     └─ CSV Generation                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technology Stack

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients and animations
- **Vanilla JavaScript**: ES6+ for dynamic functionality
- **Font Awesome**: Icon library
- **Google Fonts**: Poppins font family

### Backend - Flask
- **Python 3.11+**: Core programming language
- **Flask 3.1+**: Web framework
- **Flask-SQLAlchemy**: ORM for database operations
- **SerpApi Client**: Google search integration
- **Requests**: HTTP client for API calls

### Backend - Supabase
- **PostgreSQL 15**: Relational database
- **Deno**: JavaScript/TypeScript runtime
- **Supabase Auth**: User authentication
- **Edge Functions**: Serverless compute
- **Row-Level Security**: Data isolation

### External Services
- **SerpApi**: Google Maps and Search scraping
- **DataStone**: Brazilian CNPJ company data
- **Apify**: Instagram profile scraping

### Development Tools
- **Git**: Version control
- **Python venv**: Virtual environment management
- **dotenv**: Environment variable management

---

## 🧩 Component Architecture

### 1. Frontend Components

#### User Interface
```
index.html
├── Header Section
│   └── Title and branding
├── Input Form
│   ├── Business type input
│   └── Location input
├── Progress Tracker
│   ├── Progress bar
│   └── Status message
└── Results Display
    ├── Statistics cards
    └── Download button
```

#### JavaScript Modules
- **Event Handlers**: Form submission, button clicks
- **API Client**: Fetch calls to backend
- **UI Updater**: DOM manipulation for real-time updates
- **Progress Poller**: Periodic status checks

### 2. Backend Components (Flask)

#### Route Blueprints

**Leads Blueprint** (`src/routes/leads_smart.py`)
- `POST /api/leads/generate`: Initiate lead generation
- `GET /api/leads/status/{job_id}`: Get job status
- `GET /api/leads/download/{job_id}`: Download CSV

**User Blueprint** (`src/routes/user.py`)
- `GET /api/users`: List all users
- `POST /api/users`: Create user
- `GET /api/users/{id}`: Get user
- `PUT /api/users/{id}`: Update user
- `DELETE /api/users/{id}`: Delete user

#### Core Services

**Data Collection Service**
```python
def buscar_google_maps(tipo_negocio, localizacao):
    """Search Google Maps using SerpApi"""
    # Returns list of businesses with basic info

def buscar_instagram(nome_loja, cidade):
    """Search for Instagram profile using Google Search"""
    # Returns Instagram URLs with confidence scores

def buscar_cnpj(nome_loja, snippet):
    """Extract CNPJ from search results"""
    # Returns CNPJ numbers with confidence scores
```

**AI Analysis Service**
```python
def normalizar_texto(texto):
    """Normalize text for comparison"""
    # Removes accents, special chars, converts to lowercase

def calcular_similaridade(texto1, texto2):
    """Calculate text similarity using SequenceMatcher"""
    # Returns similarity ratio 0.0-1.0

def analisar_relevancia_resultado(nome_loja, cidade, resultado):
    """Analyze search result relevance"""
    # Composite scoring: name (40%) + city (30%) + keywords (30%)

def extrair_instagram_inteligente(nome_loja, cidade):
    """Intelligent Instagram extraction"""
    # Multi-factor confidence scoring

def extrair_cnpj_inteligente(nome_loja, localizacao):
    """Intelligent CNPJ extraction"""
    # Pattern matching with validation
```

**Enrichment Service**
```python
def consultar_cnpj_datastone(cnpj):
    """Query DataStone API for company data"""
    # Returns company status, owners, contacts

def consultar_instagram_apify(instagram_url):
    """Query Apify API for Instagram data"""
    # Returns bio, followers, posts, photos
```

### 3. Supabase Components

#### Edge Functions

**process-leads** (`supabase/functions/process-leads/`)
- TypeScript-based serverless function
- Handles async lead processing
- Updates job status in real-time
- Stores results in PostgreSQL

**job-status** (`supabase/functions/job-status/`)
- Retrieves current job status
- Calculates statistics
- Returns enrichment metrics

**export-leads** (`supabase/functions/export-leads/`)
- Generates CSV from database
- Applies user-specific filters (RLS)
- Returns downloadable file

---

## 🔄 Data Flow

### Lead Generation Flow

```
User Input (Frontend)
    ↓
POST /api/leads/generate
    ↓
Create Job Record (UUID, status: iniciando)
    ↓
┌─────────────────────────────────────┐
│  Phase 1: Google Maps Search (25%)  │
│  - Query SerpApi                    │
│  - Parse business data              │
│  - Store basic info                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Phase 2: AI Analysis (50%)         │
│  For each business:                 │
│  ├─ Search for Instagram            │
│  │  ├─ Google Search API            │
│  │  ├─ Relevance scoring            │
│  │  └─ Confidence calculation       │
│  └─ Search for CNPJ                 │
│     ├─ Pattern matching             │
│     ├─ Format validation            │
│     └─ Confidence calculation       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Phase 3: Enrichment (75%)          │
│  If CNPJ found:                     │
│  ├─ Query DataStone API             │
│  ├─ Get company status              │
│  ├─ Get owners/partners             │
│  └─ Get corporate contacts          │
│                                     │
│  If Instagram found:                │
│  ├─ Query Apify API (optional)      │
│  ├─ Get bio and followers           │
│  └─ Get contact info                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Phase 4: Finalization (100%)       │
│  - Calculate quality scores         │
│  - Deduplicate results              │
│  - Update job status                │
│  - Store final results              │
└─────────────────────────────────────┘
    ↓
GET /api/leads/status/{job_id} (polling every 2s)
    ↓
GET /api/leads/download/{job_id} (when complete)
    ↓
CSV Download (Frontend)
```

---

## 🗄️ Database Design

### Flask SQLite Schema

```sql
-- Users table (basic authentication/tracking)
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Supabase PostgreSQL Schema

```sql
-- User profiles (extends auth.users)
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    plan TEXT DEFAULT 'free', -- free, pro, enterprise
    api_credits INTEGER DEFAULT 1000,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- API keys (encrypted storage)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    service_name TEXT NOT NULL, -- serpapi, datastone, apify
    api_key_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, service_name)
);

-- Lead generation jobs
CREATE TABLE lead_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    job_name TEXT,
    business_type TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, running, completed, failed, cancelled
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    message TEXT,
    total_leads_found INTEGER DEFAULT 0,
    leads_with_instagram INTEGER DEFAULT 0,
    leads_with_cnpj INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Individual leads
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES lead_jobs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,

    -- Basic data from Google Maps
    business_name TEXT NOT NULL,
    address TEXT,
    phone_maps TEXT,
    website TEXT,
    rating_maps DECIMAL(2,1),
    reviews_count INTEGER,

    -- Instagram data
    instagram_url TEXT,
    instagram_confidence DECIMAL(3,2) CHECK (instagram_confidence >= 0 AND instagram_confidence <= 1),
    instagram_bio TEXT,
    instagram_followers INTEGER,
    instagram_posts_count INTEGER,
    instagram_business_email TEXT,
    instagram_business_phone TEXT,
    instagram_photos_urls TEXT[], -- Array of photo URLs

    -- CNPJ data
    cnpj TEXT,
    cnpj_confidence DECIMAL(3,2) CHECK (cnpj_confidence >= 0 AND cnpj_confidence <= 1),
    cnpj_status TEXT,
    company_owners TEXT,
    company_email TEXT,
    company_phone TEXT,

    -- Quality metrics
    extraction_quality_score DECIMAL(3,2) CHECK (extraction_quality_score >= 0 AND extraction_quality_score <= 1),

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- API usage tracking
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    job_id UUID REFERENCES lead_jobs(id) ON DELETE SET NULL,
    service_name TEXT NOT NULL, -- serpapi, datastone, apify
    api_calls_count INTEGER DEFAULT 0,
    credits_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Indexes

```sql
-- Performance optimization indexes
CREATE INDEX idx_leads_job_id ON leads(job_id);
CREATE INDEX idx_leads_user_id ON leads(user_id);
CREATE INDEX idx_lead_jobs_user_id ON lead_jobs(user_id);
CREATE INDEX idx_lead_jobs_status ON lead_jobs(status);
CREATE INDEX idx_usage_logs_user_id ON usage_logs(user_id);
```

---

## 🔌 API Design

### RESTful Principles

The API follows REST conventions:
- **Resource-based URLs**: `/api/leads`, `/api/users`
- **HTTP methods**: GET, POST, PUT, DELETE
- **Status codes**: 200, 201, 400, 404, 500
- **JSON format**: Request and response bodies

### Endpoint Design

**Pattern**: `/{resource}/{action}/{identifier}`

Examples:
- `POST /api/leads/generate` - Action on collection
- `GET /api/leads/status/{job_id}` - Get specific resource state
- `GET /api/leads/download/{job_id}` - Action on specific resource

### Response Format

**Success Response**:
```json
{
  "job_id": "uuid",
  "status": "string",
  "progress": 0-100,
  "message": "string",
  "data": {}
}
```

**Error Response**:
```json
{
  "error": "error_type",
  "message": "Human-readable message",
  "details": "Additional context"
}
```

---

## 🔒 Security Architecture

### Authentication

**Supabase Backend**:
- JWT-based authentication
- Secure token storage in client
- Token refresh mechanism
- Password hashing with bcrypt

**Flask Backend**:
- Currently no authentication (development)
- TODO: Implement API key authentication

### Authorization

**Row-Level Security (RLS)**:
```sql
-- Users can only see their own data
CREATE POLICY "Users can view own leads"
ON leads FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own leads"
ON leads FOR INSERT
WITH CHECK (auth.uid() = user_id);
```

### Data Protection

- **API Key Encryption**: All API keys stored encrypted
- **HTTPS Only**: All communication over SSL/TLS
- **Environment Variables**: Sensitive config externalized
- **No Credentials in Code**: Strict gitignore rules

### Input Validation

- **Type checking**: All inputs validated
- **SQL injection prevention**: ORM with parameterized queries
- **XSS prevention**: Output encoding
- **CSRF protection**: Token-based validation

---

## 📈 Scalability Considerations

### Current Limitations

1. **In-Memory Job Storage**: Jobs stored in Python dict
2. **Synchronous Processing**: Blocks thread during scraping
3. **Single Server**: No horizontal scaling
4. **No Caching**: Repeated searches not cached

### Scalability Roadmap

#### Phase 1: Immediate Improvements
- ✅ Move to Supabase async jobs
- ⬜ Implement Redis caching
- ⬜ Add rate limiting

#### Phase 2: Medium-term
- ⬜ Background job queues (Celery)
- ⬜ Load balancing (multiple workers)
- ⬜ Database connection pooling

#### Phase 3: Long-term
- ⬜ Microservices architecture
- ⬜ Kubernetes deployment
- ⬜ Global CDN for frontend
- ⬜ Distributed caching (Redis Cluster)

---

## 🎯 Design Patterns

### 1. Blueprint Pattern (Flask)
Modular route organization for maintainability.

```python
# Separate concerns into blueprints
user_bp = Blueprint('users', __name__)
leads_bp = Blueprint('leads', __name__)
```

### 2. Repository Pattern
Database access abstraction (partially implemented).

```python
class UserRepository:
    def find_by_id(id):
        return User.query.get(id)

    def save(user):
        db.session.add(user)
        db.session.commit()
```

### 3. Strategy Pattern
Different enrichment strategies based on data source.

```python
class EnrichmentStrategy:
    def enrich(self, lead): pass

class DataStoneEnrichment(EnrichmentStrategy):
    def enrich(self, lead):
        # Use DataStone API

class ApifyEnrichment(EnrichmentStrategy):
    def enrich(self, lead):
        # Use Apify API
```

### 4. Observer Pattern
Job status updates notify interested parties.

```python
# Frontend polls for status changes
function pollJobStatus(jobId) {
    setInterval(() => {
        checkStatus(jobId).then(status => {
            updateUI(status);
        });
    }, 2000);
}
```

### 5. Facade Pattern
Simplified interface to complex subsystems.

```python
class LeadGenerationFacade:
    def generate_leads(tipo_negocio, localizacao):
        # Coordinates: search, analyze, enrich, store
        results = buscar_google_maps(...)
        enriched = analisar_e_enriquecer(results)
        return salvar_resultados(enriched)
```

---

## 🧪 Testing Strategy

### Unit Tests
- Individual function testing
- Mock external API calls
- Test edge cases

### Integration Tests
- API endpoint testing
- Database operations
- External service integration

### End-to-End Tests
- Full user workflow
- Browser automation
- Performance testing

---

## 📊 Monitoring & Logging

### Current Implementation
- Flask debug mode logging
- Supabase function logs
- Console error tracking

### Future Enhancements
- Structured logging (JSON format)
- Centralized log aggregation (ELK stack)
- Application performance monitoring (APM)
- Error tracking (Sentry)
- Analytics dashboard

---

## 🚀 Deployment Architecture

### Development
```
Local Machine
├── Python venv
├── SQLite database
└── Flask dev server
```

### Production (Current)
```
Manus Cloud Platform
├── Flask application
├── Static file serving
└── Supabase backend
    ├── PostgreSQL database
    ├── Edge Functions
    └── Authentication
```

### Production (Recommended)
```
Cloud Infrastructure
├── Frontend: CDN (Cloudflare/Vercel)
├── Backend: Container platform (Docker)
├── Database: Managed PostgreSQL (Supabase)
├── Cache: Redis cluster
└── Load Balancer: Nginx/HAProxy
```

---

## 📚 Additional Resources

- [API Documentation](API_DOCUMENTATION.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Supabase Backend Docs](supabase/README.md)
- [Main README](README.md)

---

**Last Updated**: 2025-01-21
**Architecture Version**: 1.0
**Document Maintainer**: Development Team
