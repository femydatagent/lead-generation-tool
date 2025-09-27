#!/usr/bin/env python3
"""
Script para testar a configuração das APIs
"""

import os
import requests
import json
from datetime import datetime

def test_serpapi():
    """Testa a configuração da SerpApi"""
    print("🔍 Testando SerpApi...")
    
    api_key = os.getenv('SERPAPI_API_KEY')
    if not api_key:
        print("❌ SERPAPI_API_KEY não configurada")
        return False
    
    # Teste simples de busca
    params = {
        'api_key': api_key,
        'engine': 'google',
        'q': 'test',
        'num': 1
    }
    
    try:
        response = requests.get('https://serpapi.com/search', params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"❌ Erro SerpApi: {data['error']}")
                return False
            else:
                print("✅ SerpApi funcionando!")
                print(f"   Créditos restantes: {data.get('search_metadata', {}).get('total_time_taken', 'N/A')}")
                return True
        else:
            print(f"❌ SerpApi erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar SerpApi: {e}")
        return False

def test_datastone():
    """Testa a configuração da DataStone"""
    print("🏢 Testando DataStone...")
    
    api_token = os.getenv('DATASTONE_API_TOKEN')
    if not api_token:
        print("⚠️  DATASTONE_API_TOKEN não configurada (opcional)")
        return True
    
    # Teste com CNPJ da Petrobras (público)
    cnpj_teste = "33000167000101"
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(
            f'https://api.datastone.com.br/v1/companies/cnpj/{cnpj_teste}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ DataStone funcionando!")
            data = response.json()
            print(f"   Empresa teste: {data.get('razao_social', 'N/A')}")
            return True
        elif response.status_code == 401:
            print("❌ DataStone: Token inválido")
            return False
        elif response.status_code == 429:
            print("⚠️  DataStone: Limite de rate excedido")
            return True
        else:
            print(f"❌ DataStone erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar DataStone: {e}")
        return False

def test_apify():
    """Testa a configuração do Apify"""
    print("📱 Testando Apify...")
    
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        print("⚠️  APIFY_API_TOKEN não configurada (opcional)")
        return True
    
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Testa listando actors disponíveis
        response = requests.get(
            'https://api.apify.com/v2/acts',
            headers=headers,
            params={'limit': 1},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Apify funcionando!")
            data = response.json()
            print(f"   Actors disponíveis: {data.get('total', 'N/A')}")
            return True
        elif response.status_code == 401:
            print("❌ Apify: Token inválido")
            return False
        else:
            print(f"❌ Apify erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Apify: {e}")
        return False

def test_supabase():
    """Testa a configuração do Supabase"""
    print("🗄️  Testando Supabase...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Configurações do Supabase não encontradas")
        return False
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Testa conexão com a API
        response = requests.get(
            f'{supabase_url}/rest/v1/',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Supabase funcionando!")
            return True
        else:
            print(f"❌ Supabase erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Supabase: {e}")
        return False

def load_env_file():
    """Carrega variáveis do arquivo .env se existir"""
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"📄 Carregando {env_file}...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Arquivo .env carregado!")
    else:
        print("⚠️  Arquivo .env não encontrado, usando variáveis do sistema")

def main():
    """Função principal"""
    print("🧪 Teste de Configuração das APIs")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Carrega arquivo .env se existir
    load_env_file()
    print()
    
    # Testa cada API
    results = {
        'SerpApi': test_serpapi(),
        'DataStone': test_datastone(),
        'Apify': test_apify(),
        'Supabase': test_supabase()
    }
    
    print()
    print("=" * 50)
    print("📊 Resumo dos Testes:")
    
    for api, status in results.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {api}")
    
    # Verifica se pelo menos a SerpApi está funcionando
    if results['SerpApi']:
        print()
        print("🎉 Configuração mínima OK! A ferramenta pode funcionar.")
        if not results['DataStone']:
            print("💡 Configure DataStone para dados de CNPJ")
        if not results['Apify']:
            print("💡 Configure Apify para dados do Instagram")
    else:
        print()
        print("⚠️  SerpApi é obrigatória! Configure antes de usar a ferramenta.")
    
    print()
    print("📋 Para configurar as APIs:")
    print("   1. Leia o arquivo CONFIGURACAO_APIS.md")
    print("   2. Configure no dashboard do Supabase")
    print("   3. Execute este teste novamente")

if __name__ == "__main__":
    main()
