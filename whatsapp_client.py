import requests
import json
import config

def send_whatsapp_message(recipient_phone_number, message_text, message_type="text"):
    """
    Envia uma mensagem para o usuário via WhatsApp Business API.
    """
    url = f"https://graph.facebook.com/{config.WHATSAPP_API_VERSION}/{config.SENDER_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {config.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_phone_number,
        "type": message_type,
    }
    if message_type == "text":
        payload["text"] = {"preview_url": False, "body": message_text}
    # Futuramente, pode adicionar suporte para botões, listas, etc. aqui

    print(f"Enviando para {recipient_phone_number}: {message_text}") # Log
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Levanta um erro para códigos de status HTTP ruins
        print(f"Resposta da API do WhatsApp: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem: {e}")
        if e.response is not None:
            print(f"Detalhes do erro da API: {e.response.text}")
        return None