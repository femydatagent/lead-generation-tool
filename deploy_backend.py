#!/usr/bin/env python3
"""
Script para aplicar o schema do Supabase via API REST
"""

import requests
import json
import os
import time

# Configurações
PROJECT_REF = "zhlhstsnsovvtkqwubha"
ACCESS_TOKEN = "sbp_1f97cef6e9097dede1502bc52e388fd0d317a8f5"

# URLs da API do Supabase
BASE_URL = f"https://api.supabase.com/v1/projects/{PROJECT_REF}"
MANAGEMENT_API_URL = "https://api.supabase.com/v1"

# Headers para autenticação
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def get_project_info():
    """Obtém informações do projeto"""
    print("🔍 Obtendo informações do projeto...")
    
    url = f"{MANAGEMENT_API_URL}/projects/{PROJECT_REF}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        project = response.json()
        print(f"✅ Projeto encontrado: {project['name']}")
        print(f"   Status: {project['status']}")
        print(f"   Região: {project['region']}")
        return project
    else:
        print(f"❌ Erro ao obter projeto: {response.status_code}")
        print(response.text)
        return None

def apply_migration():
    """Aplica o schema como uma migração"""
    print("📄 Lendo schema SQL...")
    
    try:
        with open('/home/ubuntu/lead-generator/supabase/schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
    except FileNotFoundError:
        print("❌ Arquivo schema.sql não encontrado!")
        return False
    
    print("🚀 Aplicando schema como migração...")
    
    # Divide o schema em partes menores para evitar timeouts
    sql_statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
    
    migration_name = f"initial_schema_{int(time.time())}"
    
    # Monta o SQL da migração
    migration_sql = ";\n".join(sql_statements) + ";"
    
    url = f"{MANAGEMENT_API_URL}/projects/{PROJECT_REF}/database/migrations"
    
    payload = {
        "name": migration_name,
        "statements": [{"sql": migration_sql}]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        print("✅ Schema aplicado com sucesso!")
        return True
    else:
        print(f"❌ Erro ao aplicar schema: {response.status_code}")
        print(response.text)
        return False

def get_project_url():
    """Obtém a URL da API do projeto"""
    print("🔗 Obtendo URL da API...")
    
    url = f"{MANAGEMENT_API_URL}/projects/{PROJECT_REF}/api-keys"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        api_url = f"https://{PROJECT_REF}.supabase.co"
        anon_key = None
        
        for key in data:
            if key['name'] == 'anon':
                anon_key = key['api_key']
                break
        
        print(f"✅ URL da API: {api_url}")
        print(f"✅ Chave anônima: {anon_key[:20]}...")
        
        return api_url, anon_key
    else:
        print(f"❌ Erro ao obter chaves: {response.status_code}")
        return None, None

def deploy_edge_functions():
    """Deploy das Edge Functions"""
    print("⚡ Fazendo deploy das Edge Functions...")
    
    functions = [
        {
            "name": "process-leads",
            "path": "/home/ubuntu/lead-generator/supabase/functions/process-leads/index.ts"
        },
        {
            "name": "job-status", 
            "path": "/home/ubuntu/lead-generator/supabase/functions/job-status/index.ts"
        },
        {
            "name": "export-leads",
            "path": "/home/ubuntu/lead-generator/supabase/functions/export-leads/index.ts"
        }
    ]
    
    for func in functions:
        print(f"📦 Deploying {func['name']}...")
        
        try:
            with open(func['path'], 'r', encoding='utf-8') as f:
                function_code = f.read()
        except FileNotFoundError:
            print(f"❌ Arquivo {func['path']} não encontrado!")
            continue
        
        url = f"{MANAGEMENT_API_URL}/projects/{PROJECT_REF}/functions"
        
        payload = {
            "slug": func['name'],
            "name": func['name'],
            "source_code": function_code,
            "entrypoint": "index.ts",
            "verify_jwt": True
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            print(f"✅ {func['name']} deployed com sucesso!")
        else:
            print(f"❌ Erro no deploy de {func['name']}: {response.status_code}")
            print(response.text)

def create_env_file():
    """Cria arquivo .env com as configurações"""
    print("📝 Criando arquivo de configuração...")
    
    api_url, anon_key = get_project_url()
    
    if api_url and anon_key:
        env_content = f"""# Configurações do Supabase
SUPABASE_URL={api_url}
SUPABASE_ANON_KEY={anon_key}
SUPABASE_PROJECT_REF={PROJECT_REF}

# Chaves de API (configure com suas chaves)
SERPAPI_API_KEY=your_serpapi_key_here
DATASTONE_API_TOKEN=your_datastone_token_here
APIFY_API_TOKEN=your_apify_token_here
"""
        
        with open('/home/ubuntu/lead-generator/.env.example', 'w') as f:
            f.write(env_content)
        
        print("✅ Arquivo .env.example criado!")
        print("📋 Configure suas chaves de API no arquivo .env")

def main():
    """Função principal"""
    print("🚀 Iniciando deploy do backend Supabase...")
    print("=" * 50)
    
    # 1. Verificar projeto
    project = get_project_info()
    if not project:
        return
    
    # 2. Aplicar schema
    if not apply_migration():
        print("❌ Falha ao aplicar schema. Continuando...")
    
    # 3. Deploy das Edge Functions
    deploy_edge_functions()
    
    # 4. Criar arquivo de configuração
    create_env_file()
    
    print("=" * 50)
    print("🎉 Deploy concluído!")
    print(f"🌐 Projeto: https://supabase.com/dashboard/project/{PROJECT_REF}")
    print("📋 Próximos passos:")
    print("   1. Configure as variáveis de ambiente no dashboard")
    print("   2. Teste as Edge Functions")
    print("   3. Configure as chaves de API")

if __name__ == "__main__":
    main()
