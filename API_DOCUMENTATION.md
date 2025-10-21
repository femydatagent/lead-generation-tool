# 📡 API Documentation

Complete API reference for the Lead Generation Tool.

## 🌐 Base URLs

### Flask Backend (Local Development)
```
http://localhost:5000
```

### Production (Deployed)
```
https://xlhyimcdz5jj.manus.space
```

### Supabase Edge Functions
```
https://zhlhstsnsovvtkqwubha.supabase.co/functions/v1
```

---

## 🔐 Authentication

### Flask API
Currently, the Flask API does not require authentication for testing purposes.

### Supabase API
Requires JWT authentication via Authorization header:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

To obtain a JWT token:
```javascript
const { data } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password'
})
// Use data.session.access_token
```

---

## 📊 Lead Generation Endpoints

### 1. Generate Leads (Flask)

Start a new lead generation job.

**Endpoint**: `POST /api/leads/generate`

**Request Body**:
```json
{
  "tipo_negocio": "restaurante",
  "localizacao": "São Paulo, SP"
}
```

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tipo_negocio` | string | Yes | Type of business to search for |
| `localizacao` | string | Yes | Location (city, state) |

**Response** (202 Accepted):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "iniciando",
  "progress": 0,
  "message": "Processamento iniciado"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `job_id` | string (UUID) | Unique job identifier |
| `status` | string | Current job status |
| `progress` | integer | Progress percentage (0-100) |
| `message` | string | Human-readable status message |

**Example (cURL)**:
```bash
curl -X POST http://localhost:5000/api/leads/generate \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_negocio": "padaria",
    "localizacao": "Rio de Janeiro, RJ"
  }'
```

**Example (Python)**:
```python
import requests

response = requests.post(
    'http://localhost:5000/api/leads/generate',
    json={
        'tipo_negocio': 'restaurante',
        'localizacao': 'São Paulo, SP'
    }
)

job_data = response.json()
job_id = job_data['job_id']
```

**Example (JavaScript)**:
```javascript
const response = await fetch('/api/leads/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    tipo_negocio: 'cafeteria',
    localizacao: 'Belo Horizonte, MG'
  })
});

const data = await response.json();
console.log('Job ID:', data.job_id);
```

**Status Codes**:
- `202 Accepted`: Job started successfully
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server error

---

### 2. Check Job Status

Get the current status and progress of a lead generation job.

**Endpoint**: `GET /api/leads/status/{job_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | string (UUID) | Job ID from generate endpoint |

**Response** (200 OK):
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "concluido",
  "progress": 100,
  "message": "Concluído! 25 leads gerados com análise inteligente.",
  "results_count": 25,
  "stats": {
    "total_leads": 25,
    "leads_with_instagram": 18,
    "leads_with_cnpj": 12,
    "high_quality_leads": 15,
    "avg_quality_score": 0.72,
    "quality_percentage": 60
  }
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `job_id` | string | Job identifier |
| `status` | string | Job status (see statuses below) |
| `progress` | integer | Progress percentage (0-100) |
| `message` | string | Status message |
| `results_count` | integer | Number of leads found |
| `stats` | object | Detailed statistics (optional) |

**Job Statuses**:
- `iniciando` (0-25%): Starting the search
- `buscando` (25-50%): Searching Google Maps
- `enriquecendo` (50-75%): Enriching with Instagram/CNPJ
- `finalizando` (75-100%): Finalizing results
- `concluido` (100%): Completed successfully
- `erro`: Error occurred
- `cancelado`: Job cancelled

**Example (cURL)**:
```bash
curl http://localhost:5000/api/leads/status/550e8400-e29b-41d4-a716-446655440000
```

**Example (Python)**:
```python
import requests
import time

job_id = '550e8400-e29b-41d4-a716-446655440000'

# Poll until complete
while True:
    response = requests.get(f'http://localhost:5000/api/leads/status/{job_id}')
    data = response.json()

    print(f"Progress: {data['progress']}% - {data['message']}")

    if data['status'] == 'concluido':
        print(f"Found {data['results_count']} leads!")
        break
    elif data['status'] == 'erro':
        print("Job failed!")
        break

    time.sleep(2)  # Wait 2 seconds before next check
```

**Example (JavaScript)**:
```javascript
async function pollJobStatus(jobId) {
  while (true) {
    const response = await fetch(`/api/leads/status/${jobId}`);
    const data = await response.json();

    console.log(`${data.progress}% - ${data.message}`);

    if (data.status === 'concluido') {
      console.log(`Found ${data.results_count} leads!`);
      return data;
    }

    if (data.status === 'erro') {
      throw new Error('Job failed');
    }

    await new Promise(r => setTimeout(r, 2000)); // Wait 2s
  }
}
```

**Status Codes**:
- `200 OK`: Status retrieved successfully
- `404 Not Found`: Job ID not found
- `500 Internal Server Error`: Server error

---

### 3. Download Results (CSV)

Download the generated leads as a CSV file.

**Endpoint**: `GET /api/leads/download/{job_id}`

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | string (UUID) | Job ID from generate endpoint |

**Response**: CSV file download

**CSV Columns**:
```csv
nome,endereco,telefone,website,instagram,instagram_confianca,cnpj,cnpj_confianca,avaliacao,num_avaliacoes,score_qualidade
```

**Column Descriptions**:
| Column | Description |
|--------|-------------|
| `nome` | Business name |
| `endereco` | Full address |
| `telefone` | Phone number from Maps |
| `website` | Website URL |
| `instagram` | Instagram URL (if found) |
| `instagram_confianca` | Instagram confidence (0.0-1.0) |
| `cnpj` | CNPJ number (if found) |
| `cnpj_confianca` | CNPJ confidence (0.0-1.0) |
| `avaliacao` | Average rating |
| `num_avaliacoes` | Number of reviews |
| `score_qualidade` | Overall quality score |

**Example (cURL)**:
```bash
curl http://localhost:5000/api/leads/download/550e8400-e29b-41d4-a716-446655440000 \
  -o leads.csv
```

**Example (Python)**:
```python
import requests

job_id = '550e8400-e29b-41d4-a716-446655440000'
response = requests.get(f'http://localhost:5000/api/leads/download/{job_id}')

# Save to file
with open('leads.csv', 'wb') as f:
    f.write(response.content)

print('Downloaded leads.csv')
```

**Example (JavaScript)**:
```javascript
async function downloadCSV(jobId) {
  const response = await fetch(`/api/leads/download/${jobId}`);
  const blob = await response.blob();

  // Create download link
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `leads_${jobId}.csv`;
  a.click();
}
```

**Status Codes**:
- `200 OK`: CSV file returned
- `404 Not Found`: Job not found or no results
- `500 Internal Server Error`: Server error

---

## 👤 User Management Endpoints

### 1. List Users

Get all users (development/testing only).

**Endpoint**: `GET /api/users`

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  {
    "id": 2,
    "username": "jane_smith",
    "email": "jane@example.com"
  }
]
```

**Example (cURL)**:
```bash
curl http://localhost:5000/api/users
```

---

### 2. Create User

Create a new user.

**Endpoint**: `POST /api/users`

**Request Body**:
```json
{
  "username": "new_user",
  "email": "user@example.com"
}
```

**Response** (201 Created):
```json
{
  "id": 3,
  "username": "new_user",
  "email": "user@example.com"
}
```

**Example (cURL)**:
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com"
  }'
```

---

### 3. Get User

Get a specific user by ID.

**Endpoint**: `GET /api/users/{id}`

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

---

### 4. Update User

Update user information.

**Endpoint**: `PUT /api/users/{id}`

**Request Body**:
```json
{
  "username": "updated_username",
  "email": "updated@example.com"
}
```

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "updated_username",
  "email": "updated@example.com"
}
```

---

### 5. Delete User

Delete a user.

**Endpoint**: `DELETE /api/users/{id}`

**Response** (200 OK):
```json
{
  "message": "User deleted successfully"
}
```

---

## 🚀 Supabase Edge Functions

### 1. Process Leads (Supabase)

Start asynchronous lead processing with Supabase backend.

**Endpoint**: `POST /functions/v1/process-leads`

**Headers**:
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body**:
```json
{
  "business_type": "restaurante",
  "location": "São Paulo, SP",
  "job_name": "Restaurantes SP - Jan 2025"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Lead generation started"
}
```

**Example (JavaScript with Supabase)**:
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Login first
const { data: authData } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password'
})

// Process leads
const { data, error } = await supabase.functions.invoke('process-leads', {
  body: {
    business_type: 'cafeteria',
    location: 'Rio de Janeiro, RJ',
    job_name: 'Cafeterias RJ'
  }
})

console.log('Job ID:', data.job_id)
```

---

### 2. Job Status (Supabase)

Get job status from Supabase backend.

**Endpoint**: `GET /functions/v1/job-status/{job_id}`

**Headers**:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response** (200 OK):
```json
{
  "success": true,
  "job": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "progress": 100,
    "message": "Completed! Found 25 leads",
    "total_leads_found": 25,
    "leads_with_instagram": 18,
    "leads_with_cnpj": 12,
    "started_at": "2025-01-15T10:00:00Z",
    "completed_at": "2025-01-15T10:05:00Z",
    "stats": {
      "total_leads": 25,
      "high_quality_leads": 15,
      "avg_quality_score": 0.72,
      "quality_percentage": 60
    }
  }
}
```

---

### 3. Export Leads (Supabase)

Export leads as CSV from Supabase.

**Endpoint**: `GET /functions/v1/export-leads/{job_id}`

**Headers**:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response**: CSV file

---

## 📊 Data Models

### Lead Object

```json
{
  "id": "uuid",
  "job_id": "uuid",
  "business_name": "Restaurante Exemplo",
  "address": "Rua Exemplo, 123 - São Paulo, SP",
  "phone_maps": "+55 11 1234-5678",
  "website": "https://exemplo.com.br",
  "rating_maps": 4.5,
  "reviews_count": 150,
  "instagram_url": "https://instagram.com/exemplo",
  "instagram_confidence": 0.85,
  "instagram_bio": "Restaurante italiano autêntico",
  "instagram_followers": 5000,
  "instagram_posts_count": 250,
  "cnpj": "12.345.678/0001-90",
  "cnpj_confidence": 0.92,
  "cnpj_status": "ATIVA",
  "company_owners": "João Silva, Maria Santos",
  "company_email": "contato@exemplo.com.br",
  "company_phone": "+55 11 9876-5432",
  "extraction_quality_score": 0.88,
  "created_at": "2025-01-15T10:05:00Z"
}
```

---

## 🔍 Confidence Scores

### Instagram Confidence

Score from 0.0 to 1.0 based on:
- **40%** Name similarity
- **30%** Location mention
- **30%** Keyword coverage

**Minimum threshold**: 0.30 (30%)

### CNPJ Confidence

Score from 0.0 to 1.0 based on:
- Format validation
- Context analysis
- Pattern matching

**Minimum threshold**: 0.40 (40%)

### Quality Score

Overall lead quality from 0.0 to 1.0 based on:
- Data completeness
- Confidence scores
- Verification results

**High quality**: >= 0.70

---

## ⚠️ Error Responses

All endpoints may return error responses:

### 400 Bad Request
```json
{
  "error": "Invalid parameters",
  "message": "tipo_negocio and localizacao are required"
}
```

### 404 Not Found
```json
{
  "error": "Not found",
  "message": "Job ID not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred",
  "details": "Error details for debugging"
}
```

---

## 🚦 Rate Limiting

Currently, there are no rate limits on the Flask API. However, external APIs have their own limits:

- **SerpApi**: 100 searches/month (free tier)
- **DataStone**: 100 queries/month (free tier)
- **Apify**: $5 credits/month (free tier)

---

## 📝 Best Practices

### 1. Polling for Job Status

Use exponential backoff when polling:

```javascript
async function pollWithBackoff(jobId) {
  let delay = 1000; // Start with 1 second
  const maxDelay = 10000; // Max 10 seconds

  while (true) {
    const status = await checkStatus(jobId);

    if (status.status === 'concluido' || status.status === 'erro') {
      return status;
    }

    await new Promise(r => setTimeout(r, delay));
    delay = Math.min(delay * 1.5, maxDelay);
  }
}
```

### 2. Error Handling

Always implement proper error handling:

```javascript
try {
  const response = await fetch('/api/leads/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }

  const data = await response.json();
  return data;

} catch (error) {
  console.error('API Error:', error);
  // Handle error appropriately
}
```

### 3. Resource Cleanup

Always clean up resources after use:

```python
import requests

# Use context managers when possible
with requests.Session() as session:
    response = session.get(f'/api/leads/status/{job_id}')
    data = response.json()
```

---

## 🛠️ Testing the API

### Using the Test Script

```bash
python test_apis.py
```

### Using Postman

Import the following collection:

```json
{
  "info": {
    "name": "Lead Generation Tool API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Generate Leads",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/api/leads/generate",
        "body": {
          "mode": "raw",
          "raw": "{\"tipo_negocio\": \"restaurante\", \"localizacao\": \"São Paulo, SP\"}"
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5000"
    }
  ]
}
```

---

## 📚 Additional Resources

- [Main README](README.md)
- [Contributing Guide](CONTRIBUTING.md)
- [API Configuration Guide](CONFIGURACAO_APIS.md)
- [Supabase Backend Documentation](supabase/README.md)

---

For questions or issues, please open an issue on [GitHub](https://github.com/femydatagent/lead-generation-tool/issues).
