from open_email import process_new_emails
from import_sheet import import_sheet
data = {}
extract_emails, collection_attachment = process_new_emails()
if extract_emails:
    first_email = extract_emails[0]
    extracted_text = first_email['extracted_text']
    data["Tipo Nota"] = extract_emails[0].get("Tipo Nota", "Nota serviço")
    data['cnpj'] = extracted_text.get("CNPJ")
    data['razao_social'] = extracted_text.get("Razão Social")
    data['nf_e'] = extracted_text.get("NF-e")
    data['numero'] = extracted_text.get("N°")
    data['serie'] = extracted_text.get("Série")
    data['valor_total'] = extracted_text.get("Valor total")
    data['filename'] = collection_attachment["document_file"][0].get("Name")
    data['base64'] = collection_attachment["document_file"][0].get("Content")
    print(f"Tipo de nota fiscal: {data['Tipo Nota']}")
    print(f"Base64: {data['base64'][:20]}")
    print(f"FileName: {data['filename']}")
    print(f"CNPJ: {data['cnpj']}")
    print(f"Razão Social: {data['razao_social']}")
    print(f"NF-e: {data['nf_e']}")
    print(f"N°: {data['numero']}")
    print(f"Série: {data['serie']}")
    print(f"Valor total: {data['valor_total']}")
    print(["[DEBUG] Chamando a função import_sheet"])
    #import_sheet(data)
    
else:
    print("[DEBUG] Veio tudo vazio")
    

