import boto3
import json
import os
import email as email_parser
import re
import unicodedata
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
host = os.getenv("host")
email = os.getenv("email")
password = os.getenv("password")

# Configurar Textract
textract = boto3.client("textract", region_name="us-east-1", verify=False)
def analyze_document_textract(document_bytes: bytes):
    """Analisa um documento com Textract e retorna os dados extraídos."""
    try:
        response = textract.analyze_document(
            Document={'Bytes': document_bytes},
            FeatureTypes=["FORMS"]
        )
        print("[DEBUG] Resposta do Textract recebida!")
        return response
    except Exception as e:
        print(f"[ERRO] Falha ao chamar Textract: {str(e)}")
        return None


def extract_all_key_values(response):
    """Extrai todas as chaves e valores do Textract."""
    key_map = {}
    value_map = {}
    results = {}

    if "Blocks" not in response:
        print("[ERRO] Nenhum bloco retornado pelo Textract!")
        return results

    print("[DEBUG] Total de blocos recebidos:", len(response["Blocks"]))

    for block in response["Blocks"]:
        if block["BlockType"] == "KEY_VALUE_SET" and "EntityTypes" in block:
            if "KEY" in block["EntityTypes"]:
                key_map[block["Id"]] = block
            elif "VALUE" in block["EntityTypes"]:
                value_map[block["Id"]] = block

    for key_id, key_block in key_map.items():
        key_text = extract_text_from_block(response, key_block)
        if key_text:
            value_text = ""
            for rel in key_block.get("Relationships", []):
                if rel["Type"] == "VALUE":
                    value_block = value_map.get(rel["Ids"][0])
                    if value_block:
                        value_text = extract_text_from_block(response, value_block)
            
            results[key_text] = value_text

    print("[DEBUG] Pares chave-valor extraídos:", json.dumps(results, indent=4, ensure_ascii=False))
    return results


def extract_text_from_block(response, block):
    """Extrai o texto de um bloco do Textract."""
    if "Relationships" not in block:
        return ""

    text = []
    for rel in block["Relationships"]:
        if rel["Type"] == "CHILD":
            for word in response["Blocks"]:
                if word["Id"] in rel["Ids"] and "Text" in word:
                    text.append(word["Text"])
    return " ".join(text)

def clean_text(texto):
    """Remove acentos e coloca o texto em minúsculas."""
    return ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if unicodedata.category(c) != 'Mn')

def word_key(response):
    """Extrai e retorna apenas as informações essenciais do documento processado pelo Textract."""
    
    # Extrai todos os pares chave-valor do Textract
    extracted_data_all = extract_all_key_values(response)
    
    # Normaliza as chaves e valores extraídos
    extracted_data = {clean_text(key): clean_text(value) if isinstance(value, str) else value
                      for key, value in extracted_data_all.items()}

    print("[DEBUG] Chaves extraídas e normalizadas do Textract:", list(extracted_data.keys()))

    # Mapeamento de chaves esperadas para variações encontradas no Textract
    # Para buscar uma informação da nota fiscal, basta seguir o padrão disposto a baixo com letras sem acento e letras minúsculas
    key_map = {
    "Razão Social": ['razao social', 'nome/razao social', 'razao social da empresa', 'razao social da empresa:'],
    "NF-e": ['numero da nota fiscal', 'numero', 'nota fiscal', 'nf-e', 'nf-e:'],
    "CNPJ": ['cnpj', 'cnpj/cpf:', 'cnpjcpf', 'cnpj/cpf'],
    "N°": ['numero', 'numero do rps','n°', 'numero do rps:'],
    "Série": ['serie do documento', 'serie do rps'],
    "Valor total": [r'.*valor total.*', r'.*vi\. liquido da nota fiscal.*', r'.*liquido da nota fiscal.*'],
    "CFOP": ["cfop"]
    }

    
    print("cfop", key_map["CFOP"])

    # Criar dicionário estruturado apenas com os campos desejados
    data = {}

    for key, possible_keys in key_map.items():
        for possible_key in possible_keys:
            possible_key_clean = clean_text(possible_key)  # Normaliza os nomes das chaves do key_map
            for extracted_key in extracted_data.keys():
                if possible_key_clean in extracted_key or re.search(rf'{possible_key_clean}', extracted_key):  
                    data[key] = extracted_data[extracted_key]
                    print(f"[MATCH] Encontrado: {possible_key_clean} → {extracted_key}: {extracted_data[extracted_key]}")
                    break  # Para no primeiro match encontrado
            if key in data:
                break  # Se encontrou um match, para de procurar mais


    data["Tipo Nota"] = "Nota de venda" if data.get("CFOP") else "Nota serviço"
                
    # Remover chaves com valores vazios
    filtered_data = {k: v for k, v in data.items() if v}

    print("[DEBUG] Dados extraídos estruturados:")
    print(json.dumps(filtered_data, indent=4, ensure_ascii=False))

    return filtered_data


