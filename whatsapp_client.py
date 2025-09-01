# whatsapp_client.py
import requests
import json
import config


def send_whatsapp_message(recipient_phone_number, message_body, interactive_payload=None):
    """
    Envia uma mensagem para o usuário, que pode ser de texto simples ou interativa.
    """
    url = f"https://graph.facebook.com/{config.WHATSAPP_API_VERSION}/{config.SENDER_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {config.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone_number,
    }

    if interactive_payload:
        payload["type"] = "interactive"
        payload["interactive"] = interactive_payload
        # O corpo do texto da mensagem interativa fica dentro do payload dela
        if "body" not in payload["interactive"]:
            payload["interactive"]["body"] = {"text": message_body}
    else:
        payload["type"] = "text"
        payload["text"] = {"preview_url": False, "body": message_body}

    print(f"Enviando para {recipient_phone_number}: {json.dumps(payload, indent=2)}")  # Log
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        print(f"Resposta da API do WhatsApp: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem: {e}")
        if e.response is not None:
            print(f"Detalhes do erro da API: {e.response.text}")
        return None