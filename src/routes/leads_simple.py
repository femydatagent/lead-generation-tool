import os
import re
import csv
import io
import requests
from flask import Blueprint, request, jsonify, Response
from serpapi.google_search import GoogleSearch
import tempfile
import uuid
from datetime import datetime

leads_bp = Blueprint('leads', __name__)

# Configuração das APIs (em produção, usar variáveis de ambiente)
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
DATASTONE_API_TOKEN = os.getenv("DATASTONE_API_TOKEN", "")

DATASTONE_ENDPOINT = "https://api.datastone.com.br/v1/companies/cnpj/"

# Armazenamento temporário de jobs (em produção, usar Redis ou banco de dados)
jobs = {}

@leads_bp.route('/generate', methods=['POST'])
def generate_leads():
    """Inicia o processo de geração de leads"""
    try:
        data = request.get_json()
        tipo_negocio = data.get('tipo_negocio', '').strip()
        localizacao = data.get('localizacao', '').strip()
        
        if not tipo_negocio or not localizacao:
            return jsonify({'error': 'Tipo de negócio e localização são obrigatórios'}), 400
        
        # Verifica se as chaves de API estão configuradas
        if not SERPAPI_API_KEY:
            return jsonify({'error': 'Chave da SerpApi não configurada. Configure a variável SERPAPI_API_KEY.'}), 500
        
        # Gera um ID único para o job
        job_id = str(uuid.uuid4())
        
        # Inicia o job em background (simulado)
        jobs[job_id] = {
            'status': 'iniciado',
            'progress': 0,
            'message': 'Iniciando busca no Google Maps...',
            'created_at': datetime.now(),
            'tipo_negocio': tipo_negocio,
            'localizacao': localizacao,
            'results': None
        }
        
        # Em uma implementação real, isso seria executado em background
        # Por simplicidade, vamos executar de forma síncrona
        try:
            process_lead_generation(job_id, tipo_negocio, localizacao)
        except Exception as e:
            jobs[job_id]['status'] = 'erro'
            jobs[job_id]['message'] = f'Erro durante o processamento: {str(e)}'
        
        return jsonify({'job_id': job_id, 'status': 'iniciado'}), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Retorna o status de um job de geração de leads"""
    if job_id not in jobs:
        return jsonify({'error': 'Job não encontrado'}), 404
    
    job = jobs[job_id]
    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'progress': job['progress'],
        'message': job['message'],
        'created_at': job['created_at'].isoformat(),
        'results_count': len(job['results']) if job['results'] else 0
    })

@leads_bp.route('/download/<job_id>', methods=['GET'])
def download_results(job_id):
    """Faz download dos resultados em CSV"""
    if job_id not in jobs:
        return jsonify({'error': 'Job não encontrado'}), 404
    
    job = jobs[job_id]
    if job['status'] != 'concluido' or not job['results']:
        return jsonify({'error': 'Resultados não disponíveis'}), 400
    
    try:
        # Criar CSV em memória
        output = io.StringIO()
        
        if job['results']:
            # Obter todas as chaves únicas dos resultados
            fieldnames = set()
            for result in job['results']:
                fieldnames.update(result.keys())
            fieldnames = sorted(list(fieldnames))
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(job['results'])
        
        # Preparar resposta
        csv_content = output.getvalue()
        output.close()
        
        filename = f"leads_{job['tipo_negocio'].replace(' ', '_')}_{job['localizacao'].split(',')[0].lower()}.csv"
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar arquivo: {str(e)}'}), 500

def process_lead_generation(job_id, tipo_negocio, localizacao):
    """Processa a geração de leads (função principal)"""
    
    # Passo 1: Google Maps
    jobs[job_id]['progress'] = 25
    jobs[job_id]['message'] = 'Buscando dados no Google Maps...'
    
    dados_maps = buscar_dados_google_maps(tipo_negocio, f"{localizacao}, Brasil")
    if not dados_maps:
        jobs[job_id]['status'] = 'erro'
        jobs[job_id]['message'] = 'Nenhum resultado encontrado no Google Maps'
        return

    # Passo 2: Google Search
    jobs[job_id]['progress'] = 50
    jobs[job_id]['message'] = f'Enriquecendo dados de {len(dados_maps)} empresas...'
    
    lista_de_leads = []
    cidade_extraida = localizacao.split(',')[0]
    
    for local in dados_maps:
        nome = local.get("title")
        if not nome:
            continue
        
        url_insta, num_cnpj = buscar_instagram_e_cnpj(nome, cidade_extraida)
        lead = {
            "Nome da Loja": nome,
            "Endereço": local.get("address", ""),
            "Telefone (Maps)": local.get("phone", ""),
            "Website": local.get("website", ""),
            "Avaliação (Maps)": str(local.get("rating", "")),
            "URL Instagram": url_insta or "",
            "CNPJ": num_cnpj or ""
        }
        lista_de_leads.append(lead)
    
    # Passo 3: DataStone (opcional, se configurado)
    jobs[job_id]['progress'] = 75
    jobs[job_id]['message'] = 'Consultando dados de CNPJ...'
    
    if DATASTONE_API_TOKEN:
        for lead in lista_de_leads:
            if lead.get('CNPJ'):
                try:
                    status, socios, email, tel = consultar_cnpj_datastone(lead['CNPJ'])
                    lead['Status CNPJ'] = status or ""
                    lead['Nomes dos Sócios'] = socios or ""
                    lead['Email (DataStone)'] = email or ""
                    lead['Telefone (DataStone)'] = tel or ""
                except Exception as e:
                    # Se falhar, continua sem esses dados
                    lead['Status CNPJ'] = ""
                    lead['Nomes dos Sócios'] = ""
                    lead['Email (DataStone)'] = ""
                    lead['Telefone (DataStone)'] = ""
    
    # Finaliza o job
    jobs[job_id]['status'] = 'concluido'
    jobs[job_id]['progress'] = 100
    jobs[job_id]['message'] = f'Concluído! {len(lista_de_leads)} leads gerados.'
    jobs[job_id]['results'] = lista_de_leads

def buscar_dados_google_maps(tipo_negocio, localizacao):
    """Busca dados no Google Maps usando SerpApi"""
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google_maps",
        "q": tipo_negocio,
        "location": localizacao,
        "hl": "pt-br",
        "gl": "br",
        "start": 0
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    if "error" in results:
        raise Exception(f"Erro na busca do Google Maps: {results['error']}")
    
    locais_encontrados = results.get("local_results", [])
    
    # Paginação (limitada para evitar muitos resultados)
    page_count = 0
    while "next" in results.get("serpapi_pagination", {}) and page_count < 2:
        params["start"] += 20
        search = GoogleSearch(params)
        results = search.get_dict()
        locais_encontrados.extend(results.get("local_results", []))
        page_count += 1
    
    return locais_encontrados

def buscar_instagram_e_cnpj(nome_loja, cidade):
    """Busca Instagram e CNPJ no Google Search"""
    query = f'"{nome_loja}" "{cidade}" instagram e cnpj'
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "q": query,
        "hl": "pt-br",
        "gl": "br"
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        instagram_url, cnpj = None, None
        if "organic_results" in results:
            for result in results["organic_results"]:
                link = result.get("link", "")
                if "instagram.com/" in link and not "/p/" in link and not instagram_url:
                    instagram_url = link
                snippet = result.get("snippet", "")
                if "CNPJ" in snippet and not cnpj:
                    match = re.search(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', snippet)
                    if match:
                        cnpj = match.group(0)
        
        return instagram_url, cnpj
    except Exception as e:
        # Se falhar na busca, retorna valores vazios
        return None, None

def consultar_cnpj_datastone(cnpj):
    """Consulta CNPJ na API da DataStone"""
    if not isinstance(cnpj, str):
        return None, None, None, None
    
    cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj_limpo) != 14:
        return None, None, None, None
    
    headers = {"Authorization": f"Bearer {DATASTONE_API_TOKEN}"}
    try:
        response = requests.get(f"{DATASTONE_ENDPOINT}{cnpj_limpo}", headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        status = data.get("situacao_cadastral", "Não informado")
        socios = data.get("qsa", [])
        nomes_socios = ", ".join([s.get("nome_socio") for s in socios if s.get("nome_socio")])
        email = data.get("email")
        telefone = data.get("telefone")
        
        return status, nomes_socios, email, telefone
    except Exception as e:
        return None, None, None, None
