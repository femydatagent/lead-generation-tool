# 🚀 Lead Generation Tool

Uma ferramenta automatizada de geração e enriquecimento de leads com **IA semântica avançada** para maior precisão na extração de dados.

[![Deploy Status](https://img.shields.io/badge/deploy-live-brightgreen)](https://xlhyimcdz5jj.manus.space)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.1+-red.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🌟 Funcionalidades

### 🎯 **Coleta Automatizada de Dados**
- **Google Maps**: Busca empresas por tipo e localização
- **Google Search**: Enriquecimento com Instagram e CNPJ
- **DataStone API**: Dados corporativos detalhados
- **Apify**: Scraping avançado do Instagram (opcional)

### 🧠 **IA Semântica Avançada**
- **Análise de relevância**: Score de confiança para cada resultado
- **Matching inteligente**: Compara nomes e contexto semanticamente
- **Filtros de qualidade**: Elimina falsos positivos
- **Normalização de texto**: Remove acentos e padroniza formato

### 📊 **Interface Web Moderna**
- Design responsivo e profissional
- Progresso em tempo real
- Sistema de jobs assíncronos
- Download automático em CSV

## 🚀 Demo Online

**Acesse a aplicação:** [https://xlhyimcdz5jj.manus.space](https://xlhyimcdz5jj.manus.space)

## 📋 Pré-requisitos

- Python 3.11+
- Chaves de API:
  - **SerpApi** (obrigatória): [serpapi.com](https://serpapi.com)
  - **DataStone** (opcional): [datastone.com.br](https://datastone.com.br)
  - **Apify** (opcional): [apify.com](https://apify.com)

## 🛠️ Instalação Local

### 1. Clone o repositório
```bash
git clone https://github.com/femydatagent/lead-generation-tool.git
cd lead-generation-tool
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
export SERPAPI_API_KEY="sua_chave_serpapi"
export DATASTONE_API_TOKEN="sua_chave_datastone"  # opcional
export APIFY_API_TOKEN="sua_chave_apify"  # opcional
```

### 5. Execute a aplicação
```bash
python src/main.py
```

A aplicação estará disponível em `http://localhost:5000`

## 🔧 Configuração de APIs

### SerpApi (Obrigatória)
1. Acesse [serpapi.com](https://serpapi.com)
2. Crie uma conta gratuita
3. Obtenha sua API key
4. Configure como `SERPAPI_API_KEY`

### DataStone (Opcional)
1. Acesse [datastone.com.br](https://datastone.com.br)
2. Registre-se para obter acesso à API
3. Configure como `DATASTONE_API_TOKEN`

### Apify (Opcional)
1. Acesse [apify.com](https://apify.com)
2. Crie uma conta
3. Obtenha seu token de API
4. Configure como `APIFY_API_TOKEN`

## 📊 Como Usar

### Via Interface Web
1. Acesse a aplicação
2. Insira o **tipo de negócio** (ex: "restaurante", "clínica")
3. Insira a **localização** (ex: "São Paulo, SP")
4. Clique em **"Gerar Leads"**
5. Aguarde o processamento
6. Faça o download do CSV

### Via API
```bash
# Iniciar geração de leads
curl -X POST https://xlhyimcdz5jj.manus.space/api/leads/generate \
  -H "Content-Type: application/json" \
  -d '{"tipo_negocio": "restaurante", "localizacao": "São Paulo, SP"}'

# Verificar status
curl https://xlhyimcdz5jj.manus.space/api/leads/status/{job_id}

# Download dos resultados
curl https://xlhyimcdz5jj.manus.space/api/leads/download/{job_id}
```

## 📈 Dados Coletados

### Google Maps
- Nome da empresa
- Endereço completo
- Telefone
- Website
- Avaliação média
- Número de avaliações

### Enriquecimento Inteligente
- **URL do Instagram** (com score de confiança)
- **CNPJ** (com score de confiança)
- **Dados corporativos** (via DataStone):
  - Status da empresa
  - Nome dos sócios
  - Contatos adicionais

### Scores de Confiança
- **Instagram**: 0.00 a 1.00 (mínimo 0.30 para inclusão)
- **CNPJ**: 0.00 a 1.00 (mínimo 0.40 para inclusão)

## 🏗️ Arquitetura

```
lead-generation-tool/
├── src/
│   ├── main.py                 # Aplicação Flask principal
│   ├── routes/
│   │   ├── leads_smart.py      # API de geração de leads com IA
│   │   └── user.py            # API de usuários (template)
│   ├── models/
│   │   └── user.py            # Modelos de dados
│   ├── static/
│   │   └── index.html         # Interface web
│   └── database/
│       └── app.db             # Banco SQLite
├── requirements.txt           # Dependências Python
└── README.md                 # Documentação
```

## 🤖 Algoritmo de IA Semântica

### 1. Normalização de Texto
- Remove acentos e caracteres especiais
- Converte para minúsculo
- Padroniza espaçamento

### 2. Cálculo de Similaridade
- **40%** similaridade do nome da empresa
- **30%** presença da cidade no contexto
- **30%** cobertura de palavras-chave relevantes

### 3. Filtros de Qualidade
- **Instagram**: Score mínimo 0.30
- **CNPJ**: Score mínimo 0.40
- Remoção de duplicatas
- Validação de formatos

## 🚀 Deploy

### Automático (Recomendado)
O projeto já está configurado para deploy automático. Basta fazer push para o repositório.

### Manual
```bash
# Configure as variáveis de ambiente no servidor
export SERPAPI_API_KEY="sua_chave"
export DATASTONE_API_TOKEN="sua_chave"
export APIFY_API_TOKEN="sua_chave"

# Execute a aplicação
python src/main.py
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Roadmap

- [ ] **Background Jobs**: Implementar processamento assíncrono real
- [ ] **Cache Redis**: Cache de resultados para melhor performance
- [ ] **Autenticação**: Sistema de usuários e API keys
- [ ] **Webhooks**: Notificações de conclusão de jobs
- [ ] **Análise de Sentimento**: Análise de comentários do Instagram
- [ ] **Export Avançado**: Suporte a Excel, JSON, XML
- [ ] **Dashboard Analytics**: Métricas e relatórios detalhados

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/femydatagent/lead-generation-tool/issues)
- **Documentação**: Este README
- **Demo**: [https://xlhyimcdz5jj.manus.space](https://xlhyimcdz5jj.manus.space)

## 🏆 Créditos

Desenvolvido com ❤️ usando:
- [Flask](https://flask.palletsprojects.com) - Framework web
- [SerpApi](https://serpapi.com) - API de busca do Google
- [DataStone](https://datastone.com.br) - Dados de CNPJ
- [Apify](https://apify.com) - Scraping do Instagram

---

⭐ **Se este projeto foi útil, considere dar uma estrela!**
