# app.py
from flask import Flask, request, jsonify
import json
import config
import chatbot_logic
import whatsapp_client

app = Flask(__name__)


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == config.VERIFY_TOKEN:
            return request.args.get('hub.challenge'), 200
        else:
            return 'Verification token mismatch', 403
    if request.method == 'POST':
        data = request.get_json()
        print("Dados recebidos do WhatsApp:", json.dumps(data, indent=2))
        try:
            if data and data.get('object') == 'whatsapp_business_account':
                entry = data.get('entry', [])
                if entry and entry[0].get('changes', []) and entry[0]['changes'][0].get('value', {}).get('messages',
                                                                                                         []):
                    message_data = entry[0]['changes'][0]['value']['messages'][0]
                    user_id = message_data.get('from')
                    user_name = entry[0]['changes'][0]['value'].get('contacts', [{}])[0].get('profile', {}).get('name',
                                                                                                                "Usuário")
                    message_text = ""
                    message_type = message_data.get('type')
                    if message_type == 'text':
                        message_text = message_data.get('text', {}).get('body', "")
                    elif message_type == 'interactive':
                        interactive_data = message_data.get('interactive', {})
                        if interactive_data.get('type') == 'button_reply':
                            message_text = interactive_data.get('button_reply', {}).get('id', "")
                        elif interactive_data.get('type') == 'list_reply':
                            message_text = interactive_data.get('list_reply', {}).get('id', "")
                    else:
                        if user_id: whatsapp_client.send_whatsapp_message(user_id,
                                                                          "Ainda não consigo processar esse tipo de mensagem. Por favor, use texto ou os botões.")
                        return jsonify({'status': 'ok'}), 200

                    if user_id and message_text:
                        bot_response = chatbot_logic.handle_message(user_id, user_name, message_text)

                        if isinstance(bot_response, dict):
                            whatsapp_client.send_whatsapp_message(user_id, bot_response.get("text", ""),
                                                                  bot_response.get("interactive"))
                        elif isinstance(bot_response, str):
                            whatsapp_client.send_whatsapp_message(user_id, bot_response)
        except Exception as e:
            print(f"Erro ao processar webhook: {e}")
        return jsonify({'status': 'ok'}), 200
    return 'Not a valid request', 404


if __name__ == '__main__':
    print("Para rodar o servidor Flask, execute: flask run")
    print("Ou, para testar no terminal, execute diretamente: python terminal_test.py")