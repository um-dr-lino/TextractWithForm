
import urllib3
import os
from dotenv import load_dotenv
load_dotenv()
print("[DEBUG]: Chamou a função import")
def import_sheet(data):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    http = urllib3.PoolManager()
    url = "https://isc.softexpert.com/apigateway/se/ws/fm_ws.php"
    headers = {
        "Authorization": os.getenv("Authorization"),
        "SOAPAction": 'urn:form#newTableRecord',
        "Content-Type": "text/xml;charset=utf-8"
    }
    payload = f"""<soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:urn="urn:form">
    <soapenv:Header/>
    <soapenv:Body>
        <urn:newTableRecord>
            <urn:UserID>alino</urn:UserID>
            <urn:TableID>notafiscalia</urn:TableID>
            <urn:TableFieldList>
                <urn:TableField>
                    <urn:TableFieldID>texto1</urn:TableFieldID>
                    <urn:TableFieldValue>{data['razao_social']}</urn:TableFieldValue>
                </urn:TableField>
                <urn:TableField>
                    <urn:TableFieldID>texto2</urn:TableFieldID>
                    <urn:TableFieldValue>{data['nf_e']}</urn:TableFieldValue>
                </urn:TableField>
                <urn:TableField>
                    <urn:TableFieldID>texto3</urn:TableFieldID>
                    <urn:TableFieldValue>{data['numero']}</urn:TableFieldValue>
                </urn:TableField>
                <urn:TableField>
                    <urn:TableFieldID>texto4</urn:TableFieldID>
                    <urn:TableFieldValue>{data['serie']}</urn:TableFieldValue>
                </urn:TableField>
                <urn:TableField>
                    <urn:TableFieldID>texto5</urn:TableFieldID>
                    <urn:TableFieldValue>{data['cnpj']}</urn:TableFieldValue>
                </urn:TableField>
                <urn:TableFieldFile>
                    <urn:TableFieldID>{data['filename']}</urn:TableFieldID>
                    <urn:FileName>{data['base64']}</urn:FileName>
                    <urn:FileContent>cid:1365316695114</urn:FileContent>
                </urn:TableFieldFile>
            </urn:TableFieldList>
        </urn:newTableRecord>
    </soapenv:Body>
    """
    req = http.request('POST', url=url, headers=headers, body=payload)
    print("Resposta: ", req.data.decode('utf-8'))