# 🔑 Configuração das Variáveis de Ambiente - APIs

Este guia mostra como configurar as chaves de API necessárias para a ferramenta de geração de leads.

## 🌐 **Método 1: Dashboard do Supabase (Recomendado)**

### **Passo 1: Acessar o Dashboard**
1. Acesse: https://supabase.com/dashboard/project/zhlhstsnsovvtkqwubha
2. Faça login na sua conta Supabase
3. Vá para **Settings** → **Environment Variables**

### **Passo 2: Adicionar Variáveis**
Clique em **Add Variable** e adicione cada uma:

#### **🔍 SerpApi (OBRIGATÓRIA)**
- **Name**: `SERPAPI_API_KEY`
- **Value**: `sua_chave_serpapi_aqui`
- **Environment**: `Production`

#### **🏢 DataStone (Opcional)**
- **Name**: `DATASTONE_API_TOKEN`
- **Value**: `sua_chave_datastone_aqui`
- **Environment**: `Production`

#### **📱 Apify (Opcional)**
- **Name**: `APIFY_API_TOKEN`
- **Value**: `sua_chave_apify_aqui`
- **Environment**: `Production`

### **Passo 3: Salvar**
Clique em **Save** após adicionar cada variável.

---

## 🔧 **Método 2: Via CLI do Supabase**

Se preferir usar linha de comando:

```bash
# SerpApi (obrigatória)
supabase secrets set SERPAPI_API_KEY=sua_chave_serpapi_aqui

# DataStone (opcional)
supabase secrets set DATASTONE_API_TOKEN=sua_chave_datastone_aqui

# Apify (opcional)
supabase secrets set APIFY_API_TOKEN=sua_chave_apify_aqui
```

---

## 📋 **Como Obter Cada Chave de API**

### **1. 🔍 SerpApi (OBRIGATÓRIA)**

**O que faz**: Busca dados no Google Maps e Google Search

**Como obter**:
1. Acesse: https://serpapi.com
2. Clique em **"Get Started Free"**
3. Crie uma conta gratuita
4. Vá para **Dashboard** → **API Key**
5. Copie sua chave (formato: `abc123def456...`)

**Plano gratuito**: 100 buscas/mês
**Custo**: $50/mês para 5.000 buscas

---

### **2. 🏢 DataStone (Opcional)**

**O que faz**: Consulta dados de CNPJ (sócios, status, contatos)

**Como obter**:
1. Acesse: https://datastone.com.br
2. Registre-se para uma conta
3. Vá para **API** → **Tokens**
4. Gere um novo token
5. Copie o token (formato: `dst_abc123...`)

**Plano gratuito**: 100 consultas/mês
**Custo**: Varia conforme uso

---

### **3. 📱 Apify (Opcional)**

**O que faz**: Scraping avançado do Instagram (bio, posts, seguidores)

**Como obter**:
1. Acesse: https://apify.com
2. Crie uma conta gratuita
3. Vá para **Settings** → **Integrations**
4. Copie seu **API Token**
5. Token formato: `apify_api_abc123...`

**Plano gratuito**: $5 em créditos/mês
**Custo**: Pay-as-you-go

---

## ⚙️ **Configuração Local (Para Desenvolvimento)**

Se quiser testar localmente, crie um arquivo `.env`:

```bash
# Copie o arquivo exemplo
cp .env.example .env

# Edite com suas chaves
nano .env
```

Conteúdo do `.env`:
```env
# Supabase
SUPABASE_URL=https://zhlhstsnsovvtkqwubha.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# APIs Externas
SERPAPI_API_KEY=sua_chave_serpapi_real
DATASTONE_API_TOKEN=sua_chave_datastone_real
APIFY_API_TOKEN=sua_chave_apify_real
```

---

## 🧪 **Testando as Configurações**

### **Teste via Dashboard Supabase**
1. Vá para **Edge Functions**
2. Teste a função `process-leads`
3. Verifique os logs para erros de API

### **Teste via Aplicação Web**
1. Acesse: https://xlhyimcdz5jj.manus.space
2. Tente gerar leads de teste
3. Monitore o progresso e resultados

---

## 🚨 **Problemas Comuns**

### **❌ "SerpApi key not configured"**
- **Causa**: Variável `SERPAPI_API_KEY` não configurada
- **Solução**: Adicione a chave no dashboard do Supabase

### **❌ "Unauthorized" na SerpApi**
- **Causa**: Chave inválida ou sem créditos
- **Solução**: Verifique a chave em https://serpapi.com/dashboard

### **❌ "DataStone API error"**
- **Causa**: Token inválido ou sem créditos
- **Solução**: Verifique em https://datastone.com.br/dashboard

### **❌ "Apify actor failed"**
- **Causa**: Token inválido ou sem créditos
- **Solução**: Verifique em https://apify.com/account

---

## 💡 **Dicas de Economia**

### **SerpApi**
- Use filtros específicos para reduzir consultas
- Monitore uso no dashboard
- Considere cache de resultados

### **DataStone**
- Só consulte CNPJs com alta confiança
- Implemente cache para CNPJs já consultados
- Use batch requests quando disponível

### **Apify**
- Configure timeouts menores
- Use apenas para leads de alta qualidade
- Monitore créditos regularmente

---

## 🔒 **Segurança**

### **✅ Boas Práticas**
- ✅ Nunca commite chaves no Git
- ✅ Use variáveis de ambiente
- ✅ Rotacione chaves periodicamente
- ✅ Monitore uso das APIs
- ✅ Configure alertas de limite

### **❌ Evite**
- ❌ Chaves hardcoded no código
- ❌ Compartilhar chaves por email/chat
- ❌ Usar chaves de produção em desenvolvimento
- ❌ Deixar chaves em logs

---

## 📊 **Monitoramento**

### **Dashboard Supabase**
- Logs das Edge Functions
- Métricas de uso
- Erros de API

### **Dashboards das APIs**
- **SerpApi**: https://serpapi.com/dashboard
- **DataStone**: https://datastone.com.br/dashboard  
- **Apify**: https://apify.com/account

---

## 🎯 **Próximos Passos**

1. **Configure pelo menos a SerpApi** (obrigatória)
2. **Teste a aplicação** com dados reais
3. **Monitore o uso** das APIs
4. **Configure alertas** de limite
5. **Otimize consultas** conforme necessário

---

**🚀 Após configurar as variáveis, sua ferramenta estará 100% funcional!**
