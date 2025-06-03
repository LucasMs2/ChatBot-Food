from flask import Flask, request, jsonify
import json
import os
import config
import chatbot_logic
import whatsapp_client


app = Flask(__name__)


# Definição e verificação do Webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':

        if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == config.VERIFY_TOKEN:
            return request.args.get('hub.challenge'), 200
        else:
            print("Falha na verificação do Webhook. Token esperado:", config.VERIFY_TOKEN, "Recebido:",
                  request.args.get('hub.verify_token'))
            return 'Verification token mismatch', 403

    if request.method == 'POST':
        data = request.get_json()
        print("Dados recebidos do WhatsApp:", json.dumps(data, indent=2))

        if data and data.get('object') == 'whatsapp_business_account':
            try:
                entry = data.get('entry', [])
                if not entry:
                    print("Payload sem 'entry'.")
                    return jsonify({'status': 'ok'}), 200

                changes = entry[0].get('changes', [])
                if not changes:
                    print("Payload sem 'changes'.")
                    return jsonify({'status': 'ok'}), 200

                value = changes[0].get('value', {})
                if not value:
                    print("Payload sem 'value'.")
                    return jsonify({'status': 'ok'}), 200

                if changes[0].get('field') == 'messages':
                    messages = value.get('messages', [])
                    if not messages:
                        print("Campo 'messages' vazio ou ausente.")
                        return jsonify({'status': 'ok'}), 200

                    message_data = messages[0]
                    user_id = message_data.get('from')

                    contacts = value.get('contacts', [])
                    user_name = "Usuário"
                    if contacts:
                        user_name = contacts[0].get('profile', {}).get('name', "Usuário")

                    message_text = ""
                    message_type = message_data.get('type')

                    if message_type == 'text':
                        message_text = message_data.get('text', {}).get('body', "")
                    elif message_type == 'interactive':
                        interactive_data = message_data.get('interactive', {})
                        interactive_type = interactive_data.get('type')
                        if interactive_type == 'button_reply':
                            message_text = interactive_data.get('button_reply', {}).get('id', "")
                        elif interactive_type == 'list_reply':
                            message_text = interactive_data.get('list_reply', {}).get('id', "")
                        else:
                            print(f"Tipo interativo não tratado: {interactive_type}")
                            return jsonify({'status': 'ok'}), 200
                    else:
                        print(f"Tipo de mensagem não tratado: {message_type}")
                        if user_id:
                            whatsapp_client.send_whatsapp_message(user_id,
                                                                  "Ainda não consigo processar esse tipo de mensagem. Por favor, envie texto ou use os botões.")
                        return jsonify({'status': 'ok'}), 200

                    if user_id and message_text:
                        bot_response = chatbot_logic.handle_message(user_id, user_name, message_text)
                        whatsapp_client.send_whatsapp_message(user_id, bot_response)
                    elif not user_id:
                        print("Não foi possível extrair user_id da mensagem.")
                    elif not message_text:
                        print("Mensagem sem texto útil para processar.")


            except (IndexError, KeyError, TypeError) as e:
                print(f"Erro ao processar dados do webhook: {e}. Payload: {data}")

            return jsonify({'status': 'ok'}), 200
        else:
            return 'Not a WhatsApp event or invalid payload structure', 404


#if __name__ == '__main__':