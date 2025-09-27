# 🚀 Lead Generation Tool - Supabase Backend

Este diretório contém toda a configuração e código do backend Supabase para a ferramenta de geração de leads.

## 📁 Estrutura do Backend

```
supabase/
├── schema.sql              # Schema completo do banco de dados
├── config.toml            # Configuração do projeto Supabase
├── functions/             # Edge Functions
│   ├── process-leads/     # Processamento de leads
│   ├── job-status/        # Status de jobs
│   └── export-leads/      # Exportação CSV
└── README.md             # Esta documentação
```

## 🗄️ Schema do Banco de Dados

### Tabelas Principais

#### `profiles`
Estende `auth.users` com informações adicionais do usuário:
- `id` - UUID (FK para auth.users)
- `email` - Email único
- `full_name` - Nome completo
- `plan` - Plano (free, pro, enterprise)
- `api_credits` - Créditos disponíveis

#### `api_keys`
Armazena chaves de API criptografadas dos usuários:
- `user_id` - Referência ao usuário
- `service_name` - Serviço (serpapi, datastone, apify)
- `api_key_encrypted` - Chave criptografada
- `is_active` - Status ativo/inativo

#### `lead_jobs`
Controla jobs de geração de leads:
- `user_id` - Proprietário do job
- `business_type` - Tipo de negócio
- `location` - Localização da busca
- `status` - Status (pending, running, completed, failed)
- `progress` - Progresso (0-100)
- `total_leads_found` - Total de leads encontrados

#### `leads`
Armazena os leads individuais:
- `job_id` - Referência ao job
- `business_name` - Nome da empresa
- `address`, `phone_maps`, `website` - Dados básicos
- `instagram_url`, `instagram_confidence` - Instagram com score
- `cnpj`, `cnpj_confidence` - CNPJ com score
- `extraction_quality_score` - Score geral de qualidade

#### `usage_logs`
Log de uso de APIs para billing:
- `user_id` - Usuário
- `service_name` - Serviço utilizado
- `api_calls_count` - Número de chamadas
- `credits_used` - Créditos consumidos

### Views Analíticas

#### `user_dashboard_stats`
Estatísticas do dashboard do usuário:
- Total de jobs, leads, créditos usados
- Leads com Instagram/CNPJ
- Jobs completados

#### `recent_activity`
Atividade recente do usuário:
- Criação de jobs
- Conclusão de jobs
- Ordenado por data

## 🔐 Segurança (RLS)

### Row Level Security
Todas as tabelas têm RLS habilitado com políticas que garantem:
- Usuários só acessam seus próprios dados
- Isolamento completo entre usuários
- Proteção contra acesso não autorizado

### Políticas Principais
- **Profiles**: Usuários podem ver/editar apenas seu perfil
- **API Keys**: Usuários gerenciam apenas suas chaves
- **Jobs/Leads**: Acesso apenas aos próprios jobs e leads
- **Usage Logs**: Visualização apenas do próprio uso

## ⚡ Edge Functions

### 1. `process-leads`
**Endpoint**: `/functions/v1/process-leads`
**Método**: POST
**Autenticação**: JWT obrigatório

Processa geração de leads de forma assíncrona:

```typescript
// Request
{
  "business_type": "restaurante",
  "location": "São Paulo, SP",
  "job_name": "Restaurantes SP" // opcional
}

// Response
{
  "success": true,
  "job_id": "uuid",
  "message": "Lead generation started"
}
```

**Fluxo de Processamento**:
1. Cria job no banco
2. Busca no Google Maps via SerpApi
3. Enriquece dados com Instagram/CNPJ
4. Calcula scores de confiança
5. Salva leads no banco
6. Atualiza status do job

### 2. `job-status`
**Endpoint**: `/functions/v1/job-status/{job_id}`
**Método**: GET
**Autenticação**: JWT obrigatório

Retorna status detalhado do job:

```typescript
// Response
{
  "success": true,
  "job": {
    "id": "uuid",
    "status": "completed",
    "progress": 100,
    "message": "Completed! Found 25 leads",
    "total_leads_found": 25,
    "leads_with_instagram": 18,
    "leads_with_cnpj": 12,
    "stats": {
      "total_leads": 25,
      "high_quality_leads": 15,
      "avg_quality_score": 0.72,
      "quality_percentage": 60
    }
  }
}
```

### 3. `export-leads`
**Endpoint**: `/functions/v1/export-leads/{job_id}`
**Método**: GET
**Autenticação**: JWT obrigatório

Exporta leads em formato CSV:
- Verifica propriedade do job
- Gera CSV com todos os dados
- Retorna arquivo para download
- Nome do arquivo inclui tipo de negócio e data

## 🔧 Funções do Banco

### Utilitárias
- `update_updated_at_column()` - Atualiza timestamp automaticamente
- `handle_new_user()` - Cria perfil ao registrar usuário
- `encrypt_api_key()` - Criptografa chaves de API
- `decrypt_api_key()` - Descriptografa chaves (uso interno)

### Analíticas
- `calculate_job_stats()` - Calcula estatísticas de um job
- `update_job_progress()` - Atualiza progresso de job

## 🚀 Deploy no Supabase

### 1. Criar Projeto
```bash
# Via interface web ou CLI
supabase projects create lead-generation-tool
```

### 2. Aplicar Schema
```bash
# Aplicar schema.sql
supabase db push
```

### 3. Deploy Edge Functions
```bash
# Deploy todas as functions
supabase functions deploy process-leads
supabase functions deploy job-status
supabase functions deploy export-leads
```

### 4. Configurar Variáveis de Ambiente
No dashboard do Supabase, configurar:
- `SERPAPI_API_KEY` - Chave da SerpApi
- `DATASTONE_API_TOKEN` - Token da DataStone (opcional)
- `APIFY_API_TOKEN` - Token do Apify (opcional)

## 🔗 Integração com Frontend

### Configuração do Cliente
```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://your-project.supabase.co'
const supabaseKey = 'your-anon-key'

export const supabase = createClient(supabaseUrl, supabaseKey)
```

### Autenticação
```typescript
// Login
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password'
})

// Logout
await supabase.auth.signOut()
```

### Chamadas de API
```typescript
// Iniciar processamento
const { data } = await supabase.functions.invoke('process-leads', {
  body: {
    business_type: 'restaurante',
    location: 'São Paulo, SP'
  }
})

// Verificar status
const { data } = await supabase.functions.invoke('job-status', {
  body: { job_id: 'uuid' }
})

// Exportar CSV
const { data } = await supabase.functions.invoke('export-leads', {
  body: { job_id: 'uuid' }
})
```

## 📊 Monitoramento

### Logs
- Edge Functions logs no dashboard Supabase
- Logs de erro capturados automaticamente
- Métricas de performance disponíveis

### Advisors
Use `get_advisors` para verificar:
- Políticas RLS faltantes
- Vulnerabilidades de segurança
- Otimizações de performance

### Métricas
- Uso de API por usuário
- Performance de jobs
- Taxa de sucesso de extração
- Qualidade média dos leads

## 🔄 Backup e Manutenção

### Backup Automático
- Supabase faz backup automático diário
- Retenção de 7 dias no plano gratuito
- Point-in-time recovery disponível

### Migrações
- Todas as mudanças via migrations
- Versionamento automático
- Rollback disponível

### Monitoramento de Saúde
- Uptime monitoring integrado
- Alertas de performance
- Métricas de uso em tempo real

## 🎯 Próximos Passos

1. **Implementar Rate Limiting** nas Edge Functions
2. **Adicionar Cache Redis** para melhor performance
3. **Webhooks** para notificações de conclusão
4. **Analytics Avançadas** com dashboards personalizados
5. **Integração com Stripe** para billing automático
6. **API de Webhooks** para integrações externas

---

Este backend fornece uma base sólida, escalável e segura para a ferramenta de geração de leads, com todas as funcionalidades necessárias para produção.
