# chatbot_logic.py
import sys
import os
import config


def load_menu_from_file(filename="cardapio.txt"):
    menu_map = {}
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    actual_filepath = os.path.join(base_path, filename)
    print(f"Tentando carregar cardápio de: {actual_filepath}")
    try:
        with open(actual_filepath, "r", encoding="utf-8") as f:
            for line in f:
                item_original = line.strip()
                if item_original:
                    menu_map[item_original.lower()] = item_original
        if not menu_map:
            print(f"AVISO: O arquivo do cardápio '{actual_filepath}' está vazio.")
        else:
            print(f"Cardápio carregado com {len(menu_map)} itens de '{actual_filepath}'.")
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: Arquivo do cardápio '{actual_filepath}' não encontrado.")
    return menu_map


MENU_ITEMS_MAP = load_menu_from_file()
user_sessions = {}


# --- Handlers de Estado Específicos ---

def _handle_state_new_user(session, message_text):
    session["state"] = "AWAITING_INITIAL_CHOICE"
    return {
        "text": (
            f"Olá! 👋 Bem-vindo(a) à {config.NOME_DA_PIZZARIA}! Sou seu assistente virtual! 🍕😋\n\nComo posso te ajudar hoje?"),
        "interactive": {
            "type": "button", "action": {"buttons": [
                {"type": "reply", "reply": {"id": "menu_pedido", "title": "🍕 Fazer Pedido"}},
                {"type": "reply", "reply": {"id": "menu_info", "title": "ℹ️ Informações"}},
                {"type": "reply", "reply": {"id": "falar_atendente", "title": "🗣️ Falar com Atendente"}}
            ]}
        }
    }


def _handle_state_awaiting_initial_choice(session, message_text):
    if message_text == "menu_pedido":
        session["state"] = "AWAITING_ORDER_DESCRIPTION"
        return {
            "text": (
                f"Ótima escolha! 😊 Nosso cardápio online: ➡️ {config.LINK_CARDAPIO_ONLINE}\n\nO que você gostaria de pedir? (Ex: 'Pizza Calabresa Grande')"),
            "interactive": {"type": "button", "action": {
                "buttons": [{"type": "reply", "reply": {"id": "voltar_menu_principal", "title": "↩️ Voltar"}}]}}
        }
    elif message_text == "menu_info":
        session["state"] = "AWAITING_INFO_CHOICE"
        return {
            "text": "Claro! O que você gostaria de saber?",
            "interactive": {"type": "list",
                            "action": {"button": "Ver Opções 📝", "sections": [{"title": "Nossas Informações", "rows": [
                                {"id": "info_horario", "title": "⏰ Horário de Funcionamento"},
                                {"id": "info_endereco", "title": "📍 Nosso Endereço"},
                                {"id": "info_promocoes", "title": "🎉 Promoções Atuais"},
                                {"id": "voltar_menu_principal", "title": "↩️ Voltar"}
                            ]}]}}
        }
    elif message_text == "falar_atendente":
        session["state"] = "HANDED_OFF_TO_HUMAN"
        return "Entendido! Vou te transferir para um de nossos atendentes. Aguarde um momento, por favor. 😊"
    else:
        return "Por favor, clique em uma das opções para continuar."


def _handle_state_awaiting_order_description(session, message_text):
    if message_text.lower() == "finalizar pedido":
        if not session.get("order"):
            return "Seu carrinho está vazio. Por favor, adicione um item antes de finalizar."
        else:
            order_summary = "\n".join([f"- {item['name']}" for item in session["order"]])
            session["state"] = "AWAITING_DELIVERY_OR_PICKUP"
            return {
                "text": f"Perfeito! Vamos revisar seu pedido:\n🍕 Itens:\n{order_summary}\n\nSeu pedido será para:",
                "interactive": {"type": "button", "action": {"buttons": [
                    {"type": "reply", "reply": {"id": "escolha_entrega", "title": "🛵 Entrega (Delivery)"}},
                    {"type": "reply", "reply": {"id": "escolha_retirada", "title": "🚶 Retirada no local"}}
                ]}}
            }
    elif message_text == "voltar_menu_principal":
        return _handle_state_new_user(session, message_text)
    else:
        if not MENU_ITEMS_MAP: return "Desculpe, estou com um problema para acessar nosso cardápio no momento."

        user_request_normalized = message_text.lower().strip()
        found_item_original_name = None
        possible_matches = []
        if user_request_normalized in MENU_ITEMS_MAP:
            found_item_original_name = MENU_ITEMS_MAP[user_request_normalized]
        else:
            for norm_name, orig_name in MENU_ITEMS_MAP.items():
                if user_request_normalized in norm_name: possible_matches.append(orig_name)
            if len(possible_matches) == 1:
                found_item_original_name = possible_matches[0]
            elif len(possible_matches) > 1:
                matches_text = "\n".join([f"- {match}" for match in possible_matches[:5]])
                return f"Encontrei alguns itens parecidos com '{message_text}':\n{matches_text}\nQual deles você gostaria? Por favor, digite o nome completo."

        if found_item_original_name:
            session.setdefault("order", []).append({"name": found_item_original_name})
            order_summary = "\n".join([f"- {item['name']}" for item in session["order"]])
            return (
                f"Adicionado: {found_item_original_name}.\nSeu pedido até agora:\n{order_summary}\n\nAlgo mais? (Digite o item ou 'finalizar pedido')")
        else:
            return f"Desculpe, não encontrei '{message_text}' em nosso cardápio. 🤔\nTente novamente ou confira nosso cardápio online."


def _handle_state_awaiting_info_choice(session, message_text):
    response_text = ""
    if message_text == "info_horario":
        response_text = config.HORARIO_FUNCIONAMENTO
    elif message_text == "info_endereco":
        response_text = config.ENDERECO_PIZZARIA
    elif message_text == "info_promocoes":
        response_text = config.PROMOCOES_DO_DIA
    elif message_text == "voltar_menu_principal":
        return _handle_state_new_user(session, message_text)
    else:
        response_text = "Opção de informação inválida."
    return {"text": response_text + "\n\nPosso ajudar com mais alguma coisa?", "interactive": _get_next_step_buttons()}


def _get_next_step_buttons():  # Função auxiliar para evitar repetição
    return {"type": "button", "action": {"buttons": [
        {"type": "reply", "reply": {"id": "menu_pedido", "title": "🍕 Fazer Pedido"}},
        {"type": "reply", "reply": {"id": "falar_atendente", "title": "🗣️ Falar com Atendente"}}
    ]}}


def _handle_state_awaiting_delivery_or_pickup(session, message_text):
    if message_text == "escolha_entrega":
        session["delivery_type"] = "delivery"
        session["state"] = "AWAITING_ADDRESS"
        return "Entendido! Para entrega, informe seu endereço completo (Rua, N°, Bairro, Complemento, Referência):"
    elif message_text == "escolha_retirada":
        session["delivery_type"] = "pickup"
        session["state"] = "AWAITING_PICKUP_NAME"
        return f"Combinado! Retirada em aprox. {config.TEMPO_MEDIO_PREPARO_RETIRADA} min. Em nome de quem será a retirada?"
    else:
        return "Por favor, escolha uma das opções: Entrega ou Retirada."


def _handle_state_awaiting_address(session, message_text):
    session["address"] = message_text
    session["state"] = "AWAITING_PAYMENT"
    return {"text": f"Endereço anotado: {message_text}.\nComo você gostaria de pagar?",
            "interactive": _get_payment_buttons()}


def _handle_state_awaiting_pickup_name(session, message_text):
    session["pickup_name"] = message_text
    session["state"] = "AWAITING_PAYMENT"
    return {"text": f"Retirada em nome de: {message_text}.\nComo você gostaria de pagar?",
            "interactive": _get_payment_buttons()}


def _get_payment_buttons():  # Função auxiliar para botões de pagamento
    return {"type": "button", "action": {"buttons": [
        {"type": "reply", "reply": {"id": "pagamento_cartao", "title": "💳 Cartão"}},
        {"type": "reply", "reply": {"id": "pagamento_dinheiro", "title": "💰 Dinheiro"}},
        {"type": "reply", "reply": {"id": "pagamento_pix", "title": "📲 PIX"}}
    ]}}


def _handle_state_awaiting_payment(session, message_text):
    previsao = f"Previsão: {config.TEMPO_MEDIO_ENTREGA if session.get('delivery_type') == 'delivery' else config.TEMPO_MEDIO_PREPARO_RETIRADA} min"
    response_text = "Opção de pagamento inválida."
    if message_text == "pagamento_cartao":
        session["payment_method"] = "Cartão";
        session["state"] = "ORDER_COMPLETED";
        response_text = f"Pagamento com Cartão. Pedido quase pronto! {previsao}."
    elif message_text == "pagamento_dinheiro":
        session["payment_method"] = "Dinheiro";
        session["state"] = "ORDER_COMPLETED";
        response_text = f"Pagamento em Dinheiro. Se precisar de troco, nos avise! Pedido quase pronto! {previsao}."
    elif message_text == "pagamento_pix":
        session["payment_method"] = "PIX";
        session["state"] = "AWAITING_PIX_PROOF";
        response_text = f"Pagamento com PIX. Chave: {config.PIX_CHAVE}. Envie o comprovante. Pedido confirmado após comprovante. {previsao} (após confirmação)."

    if session["state"] == "ORDER_COMPLETED": response_text += _get_final_summary(session)
    return response_text


def _get_final_summary(session):
    order_summary_final = "\n".join([f"- {item['name']}" for item in session.get("order", [])])
    delivery_info = ""
    if session.get("delivery_type") == "delivery":
        delivery_info = f"Endereço de Entrega: {session.get('address', 'Não informado')}"
    elif session.get("delivery_type") == "pickup":
        delivery_info = f"Retirada em nome de: {session.get('pickup_name', 'Não informado')}"
    return (
        f"\n\n🎉 PEDIDO CONFIRMADO! 🎉\nResumo:\n{order_summary_final}\nPagamento: {session.get('payment_method', 'Não informado')}\n{delivery_info}\nObrigado pela preferência, {config.NOME_DA_PIZZARIA} agradece!")


def _handle_state_awaiting_pix_proof(session, message_text):
    session["state"] = "ORDER_COMPLETED_AFTER_PIX"
    return "Comprovante recebido (simulação)! Seu pedido está confirmado e já vai para a produção!" + _get_final_summary(
        session)


def _handle_state_handed_off_to_human(session, message_text):
    return "Um de nossos atendentes já foi notificado e responderá em breve."


def _handle_default_state(session, message_text):
    session["state"] = "NEW_USER"
    return _handle_state_new_user(session, message_text)  # Reinicia a conversa com os botões


def handle_message(user_id, user_name, message_text):
    session = user_sessions.get(user_id, {})
    if not session: session = {"state": "NEW_USER"}; user_sessions[user_id] = session
    current_state = session.get("state", "NEW_USER")
    print(f"Sessão: {session} | Mensagem: {message_text}")
    if message_text.lower() in ["menu", "oi", "olá", "ajuda", "cancelar", "sair"]: current_state = "NEW_USER"
    state_handlers = {"NEW_USER": _handle_state_new_user,
                      "AWAITING_INITIAL_CHOICE": _handle_state_awaiting_initial_choice,
                      "AWAITING_ORDER_DESCRIPTION": _handle_state_awaiting_order_description,
                      "AWAITING_INFO_CHOICE": _handle_state_awaiting_info_choice,
                      "AWAITING_DELIVERY_OR_PICKUP": _handle_state_awaiting_delivery_or_pickup,
                      "AWAITING_ADDRESS": _handle_state_awaiting_address,
                      "AWAITING_PICKUP_NAME": _handle_state_awaiting_pickup_name,
                      "AWAITING_PAYMENT": _handle_state_awaiting_payment,
                      "AWAITING_PIX_PROOF": _handle_state_awaiting_pix_proof,
                      "HANDED_OFF_TO_HUMAN": _handle_state_handed_off_to_human}
    handler_function = state_handlers.get(current_state, _handle_default_state)
    response = handler_function(session, message_text)
    user_sessions[user_id] = session
    return response