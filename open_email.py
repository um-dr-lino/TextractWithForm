import imaplib
import os
import urllib3
import boto3
from dotenv import load_dotenv
import email as email_parser
import base64
from extract_form import analyze_document_textract, word_key


# Carregar variáveis de ambiente
load_dotenv()
host = os.getenv("host")
email = os.getenv("email")
password = os.getenv("password")

textract = boto3.client("textract", region_name="us-east-1", verify=False)
http = urllib3.PoolManager()
download_folder = "/tmp"
os.makedirs(download_folder, exist_ok=True)

def connect_email():
    """Conecta ao servidor de email via IMAP."""
    print("[DEBUG] Iniciando conexão ao servidor de email")
    mail = imaplib.IMAP4_SSL(host)
    print(f"[DEBUG] Tentando login com usuário: {email}")
    mail.login(email, password)
    print("[DEBUG] Login bem-sucedido")
    return mail

def process_new_emails():
    """Processa novos e-mails e extrai apenas as informações essenciais dos anexos."""
    collection_attachment = {'document_file': []}
    extract_emails = []  

    mail = connect_email()
    mail.select("inbox")

    # Buscar e-mails não lidos
    status, email_ids = mail.search(None, '(UNSEEN)')
    email_list = email_ids[0].split()
    
    if not email_list:
        print("Nenhum e-mail não lido encontrado.")
        return None, None  

    latest_email_id = email_list[-1]
    status, email_data = mail.fetch(latest_email_id, "(RFC822)")
    raw_email = email_data[0][1]

    msg = email_parser.message_from_bytes(raw_email)

    print("=" * 50)
    print(f"**De:** {msg['From']}")
    print(f"**Assunto:** {msg['Subject']}")
    print("[DEBUG] Procurando por anexos no email")

    has_attachments = False
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None:
            continue    

        filename = part.get_filename()
        if filename:
            clean_name = filename.strip().lower()
            if clean_name.startswith("outlook-"):
                print(f"({filename}) ignorado: começa com 'Outlook-'")
                continue
            
            has_attachments = True
            print(f"[DEBUG] Anexo encontrado: {filename}")     

            file_path = os.path.join(download_folder, filename)
            with open(file_path, "wb") as f:
                f.write(part.get_payload(decode=True))

            with open(file_path, "rb") as doc_file:
                document_bytes = doc_file.read()
                base64_encoded = base64.b64encode(document_bytes).decode('utf-8')

            textract_response = analyze_document_textract(document_bytes)
            extracted_text = word_key(textract_response) if textract_response else {}
            
            extract_email = {
                'file_name': filename,
                'base64_file': base64_encoded,
                'extracted_text': extracted_text  
            }
            extract_emails.append(extract_email)
            collection_attachment.get('document_file').append({'Name': filename, 'Content': base64_encoded})
    if not has_attachments:
        print("Nenhum anexo encontrado.")

    print("[DEBUG] Processamento de email concluído!")
    print("[DEBUG]: Chamando o extract_emails")
    return extract_emails, collection_attachment



