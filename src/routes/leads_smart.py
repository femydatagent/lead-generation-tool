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
import difflib
import unicodedata

leads_bp = Blueprint('leads', __name__)

# Configuração das APIs (em produção, usar variáveis de ambiente)
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
DATASTONE_API_TOKEN = os.getenv("DATASTONE_API_TOKEN", "")

DATASTONE_ENDPOINT = "https://api.datastone.com.br/v1/companies/cnpj/"

# Armazenamento temporário de jobs (em produção, usar Redis ou banco de dados)
jobs = {}

def normalizar_texto(texto):
    """Normaliza texto removendo acentos, convertendo para minúsculo e removendo caracteres especiais"""
    if not texto:
        return ""
    
    # Remove acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
    
    # Converte para minúsculo e remove caracteres especiais
    texto = re.sub(r'[^a-zA-Z0-9\s]', '', texto.lower())
    
    # Remove espaços extras
    texto = ' '.join(texto.split())
    
    return texto

def calcular_similaridade(texto1, texto2):
    """Calcula a similaridade entre dois textos usando SequenceMatcher"""
    texto1_norm = normalizar_texto(texto1)
    texto2_norm = normalizar_texto(texto2)
    
    return difflib.SequenceMatcher(None, texto1_norm, texto2_norm).ratio()

def extrair_palavras_chave(nome_loja):
    """Extrai palavras-chave relevantes do nome da loja"""
    nome_norm = normalizar_texto(nome_loja)
    
    # Remove palavras comuns que não são distintivas
    palavras_comuns = {
        'ltda', 'me', 'eireli', 'sa', 'ss', 'comercio', 'servicos', 'empresa',
        'loja', 'casa', 'centro', 'clinica', 'consultorio', 'instituto',
        'e', 'de', 'da', 'do', 'das', 'dos', 'em', 'na', 'no', 'com', 'para'
    }
    
    palavras = [palavra for palavra in nome_norm.split() 
                if len(palavra) > 2 and palavra not in palavras_comuns]
    
    return palavras

def analisar_relevancia_resultado(nome_loja, cidade, resultado):
    """Analisa a relevância de um resultado de busca para a loja específica"""
    titulo = resultado.get('title', '')
    snippet = resultado.get('snippet', '')
    link = resultado.get('link', '')
    
    # Combina todo o conteúdo do resultado
    conteudo_completo = f"{titulo} {snippet} {link}".lower()
    
    # Calcula similaridade do nome
    similaridade_nome = calcular_similaridade(nome_loja, titulo)
    
    # Verifica se a cidade está mencionada
    cidade_mencionada = normalizar_texto(cidade) in normalizar_texto(conteudo_completo)
    
    # Verifica quantas palavras-chave da loja aparecem no resultado
    palavras_chave = extrair_palavras_chave(nome_loja)
    palavras_encontradas = sum(1 for palavra in palavras_chave 
                              if palavra in normalizar_texto(conteudo_completo))
    
    cobertura_palavras = palavras_encontradas / len(palavras_chave) if palavras_chave else 0
    
    # Calcula score de relevância (0-1)
    score_relevancia = (
        similaridade_nome * 0.4 +  # 40% peso para similaridade do nome
        (1.0 if cidade_mencionada else 0.0) * 0.3 +  # 30% peso para cidade
        cobertura_palavras * 0.3  # 30% peso para cobertura de palavras-chave
    )
    
    return {
        'score': score_relevancia,
        'similaridade_nome': similaridade_nome,
        'cidade_mencionada': cidade_mencionada,
        'cobertura_palavras': cobertura_palavras,
        'palavras_encontradas': palavras_encontradas,
        'total_palavras': len(palavras_chave)
    }

def extrair_instagram_inteligente(nome_loja, cidade, resultados):
    """Extrai URL do Instagram com análise de relevância"""
    candidatos_instagram = []
    
    for resultado in resultados:
        link = resultado.get('link', '')
        
        # Verifica se é um link do Instagram (perfil, não post)
        if 'instagram.com/' in link and not '/p/' in link and not '/reel/' in link:
            # Remove parâmetros da URL
            link_limpo = link.split('?')[0].rstrip('/')
            
            # Analisa relevância
            analise = analisar_relevancia_resultado(nome_loja, cidade, resultado)
            
            candidatos_instagram.append({
                'url': link_limpo,
                'score': analise['score'],
                'analise': analise,
                'titulo': resultado.get('title', ''),
                'snippet': resultado.get('snippet', '')
            })
    
    # Ordena por score de relevância
    candidatos_instagram.sort(key=lambda x: x['score'], reverse=True)
    
    # Retorna o melhor candidato se tiver score mínimo de 0.3
    if candidatos_instagram and candidatos_instagram[0]['score'] >= 0.3:
        return candidatos_instagram[0]['url'], candidatos_instagram[0]['score']
    
    return None, 0

def extrair_cnpj_inteligente(nome_loja, cidade, resultados):
    """Extrai CNPJ com análise de relevância"""
    candidatos_cnpj = []
    
    for resultado in resultados:
        snippet = resultado.get('snippet', '')
        titulo = resultado.get('title', '')
        
        # Procura por padrões de CNPJ
        padroes_cnpj = [
            r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',  # Formato completo: XX.XXX.XXX/XXXX-XX
            r'\d{14}',  # Apenas números
        ]
        
        for padrao in padroes_cnpj:
            matches = re.findall(padrao, snippet + ' ' + titulo)
            
            for match in matches:
                # Normaliza o CNPJ para formato padrão
                cnpj_numeros = re.sub(r'[^0-9]', '', match)
                
                # Verifica se tem 14 dígitos
                if len(cnpj_numeros) == 14:
                    # Formata o CNPJ
                    cnpj_formatado = f"{cnpj_numeros[:2]}.{cnpj_numeros[2:5]}.{cnpj_numeros[5:8]}/{cnpj_numeros[8:12]}-{cnpj_numeros[12:14]}"
                    
                    # Analisa relevância
                    analise = analisar_relevancia_resultado(nome_loja, cidade, resultado)
                    
                    candidatos_cnpj.append({
                        'cnpj': cnpj_formatado,
                        'cnpj_numeros': cnpj_numeros,
                        'score': analise['score'],
                        'analise': analise,
                        'titulo': resultado.get('title', ''),
                        'snippet': snippet
                    })
    
    # Remove duplicatas mantendo o melhor score
    cnpjs_unicos = {}
    for candidato in candidatos_cnpj:
        cnpj_num = candidato['cnpj_numeros']
        if cnpj_num not in cnpjs_unicos or candidato['score'] > cnpjs_unicos[cnpj_num]['score']:
            cnpjs_unicos[cnpj_num] = candidato
    
    # Ordena por score de relevância
    candidatos_finais = sorted(cnpjs_unicos.values(), key=lambda x: x['score'], reverse=True)
    
    # Retorna o melhor candidato se tiver score mínimo de 0.4
    if candidatos_finais and candidatos_finais[0]['score'] >= 0.4:
        return candidatos_finais[0]['cnpj'], candidatos_finais[0]['score']
    
    return None, 0

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

    # Passo 2: Google Search Inteligente
    jobs[job_id]['progress'] = 50
    jobs[job_id]['message'] = f'Analisando dados de {len(dados_maps)} empresas com IA...'
    
    lista_de_leads = []
    cidade_extraida = localizacao.split(',')[0]
    
    for i, local in enumerate(dados_maps):
        nome = local.get("title")
        if not nome:
            continue
        
        # Atualiza progresso para cada empresa
        progresso_atual = 50 + (i / len(dados_maps)) * 25
        jobs[job_id]['progress'] = int(progresso_atual)
        jobs[job_id]['message'] = f'Analisando: {nome[:30]}...'
        
        url_insta, score_insta, num_cnpj, score_cnpj = buscar_instagram_e_cnpj_inteligente(nome, cidade_extraida)
        
        lead = {
            "Nome da Loja": nome,
            "Endereço": local.get("address", ""),
            "Telefone (Maps)": local.get("phone", ""),
            "Website": local.get("website", ""),
            "Avaliação (Maps)": str(local.get("rating", "")),
            "URL Instagram": url_insta or "",
            "Confiança Instagram": f"{score_insta:.2f}" if url_insta else "",
            "CNPJ": num_cnpj or "",
            "Confiança CNPJ": f"{score_cnpj:.2f}" if num_cnpj else ""
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
    jobs[job_id]['message'] = f'Concluído! {len(lista_de_leads)} leads gerados com análise inteligente.'
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

def buscar_instagram_e_cnpj_inteligente(nome_loja, cidade):
    """Busca Instagram e CNPJ no Google Search com análise inteligente"""
    # Monta query mais específica
    query = f'"{nome_loja}" {cidade} instagram cnpj site:instagram.com OR "CNPJ"'
    
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "q": query,
        "hl": "pt-br",
        "gl": "br",
        "num": 20  # Busca mais resultados para melhor análise
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        resultados_organicos = results.get("organic_results", [])
        
        if not resultados_organicos:
            return None, 0, None, 0
        
        # Extrai Instagram com análise inteligente
        url_instagram, score_instagram = extrair_instagram_inteligente(nome_loja, cidade, resultados_organicos)
        
        # Extrai CNPJ com análise inteligente
        cnpj, score_cnpj = extrair_cnpj_inteligente(nome_loja, cidade, resultados_organicos)
        
        return url_instagram, score_instagram, cnpj, score_cnpj
        
    except Exception as e:
        # Se falhar na busca, retorna valores vazios
        return None, 0, None, 0

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
