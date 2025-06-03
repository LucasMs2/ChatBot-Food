import sys
import os
import config


#Carregar Itens do Cardápio na Inicialização
def load_menu_from_file(filename="cardapio.txt"):
    """
    Carrega os itens do cardápio de um arquivo TXT.
    Procura o arquivo na pasta do executável (se congelado) ou na pasta do script.
    Retorna um dicionário mapeando o nome normalizado (minúsculo) para o nome original.
    """
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
            print(f"AVISO: O arquivo do cardápio '{actual_filepath}' está vazio ou não contém itens válidos.")
        else:
            print(f"Cardápio carregado com {len(menu_map)} itens de '{actual_filepath}'.")
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: Arquivo do cardápio '{actual_filepath}' não encontrado. "
              "Certifique-se de que 'cardapio.txt' está na mesma pasta que o executável ou o script.")
    return menu_map


MENU_ITEMS_MAP = load_menu_from_file()


#Gerenciamento de Estado da Conversa
user_sessions = {}


#Funções Auxiliares de Mensagem
def get_initial_greeting():
    return (
        f"Olá! 👋 Bem-vindo(a) à {config.NOME_DA_PIZZARIA}! Sou seu assistente virtual! 🍕😋\n\n"
        "Como posso te ajudar hoje?\n"
        "Digite o número da opção desejada:\n"
        "1. 🍕 Ver Cardápio e Fazer Pedido\n"
        "2. ℹ️ Informações\n"
        "3. 🗣️ Falar com um Atendente"
    )


def get_first_menu_options(message_text_str):
    if message_text_str == "1":
        return (
            "Ótima escolha! 😊 Nosso cardápio online: "
            f"➡️ CARDAPIO.PDF\n\n"
            "Ou pode voltar ao menu anterior digitando 5"
        )
    elif message_text_str == "2":
        return (
            "Claro! O que você gostaria de saber?\n"
            "1. ⏰ Nosso Horário de Funcionamento\n"
            "2. 📍 Nosso Endereço (para retirada)\n"
            "3. 🎉 Promoções Atuais\n"
            "4. ↩️ Voltar ao menu anterior"
        )
    elif message_text_str == "3":
        return ("Entendido! Vou te transferir para um de nossos atendentes. "
                "Aguarde um momento, por favor. 😊")
    return "Opção inválida. Por favor, tente novamente."



def _handle_state_new_user(session, message_text):
    session["state"] = "AWAITING_INITIAL_CHOICE"
    return get_initial_greeting()

#Aguardando pedido
def _handle_state_awaiting_initial_choice(session, message_text):
    response_text = get_first_menu_options(message_text)  # message_text é "1", "2", ou "3"
    if message_text == "1":
        session["state"] = "AWAITING_ORDER_DESCRIPTION"
    elif message_text == "2":
        session["state"] = "AWAITING_INFO_CHOICE"
    elif message_text == "3":
        session["state"] = "HANDED_OFF_TO_HUMAN"
    else:
        response_text = "Opção inválida. Por favor, digite 1, 2 ou 3.\n\n" + get_initial_greeting()
    return response_text

#Fazendo pedido
def _handle_state_awaiting_order_description(session, message_text):
    response_text = "Desculpe, não entendi o item do pedido."
    if message_text.lower() == "finalizar pedido":
        if not session.get("order"):
            response_text = ("Seu carrinho está vazio. Gostaria de adicionar algo?\n\n" + get_first_menu_options("1"))
        else:
            order_summary = "\n".join([f"- {item['name']} ({item.get('details', '')})" for item in session["order"]])
            response_text = (
                f"Perfeito! Vamos revisar seu pedido:\n🍕 Itens:\n{order_summary}\n\n"
                "Seu pedido será para:\n"
                "1. 🛵 Entrega (Delivery)\n"
                "2. 🚶 Retirada no local"
            )
            session["state"] = "AWAITING_DELIVERY_OR_PICKUP"
    elif message_text.lower() == "5":
        response_text = get_initial_greeting()
        session["state"] = "AWAITING_INITIAL_CHOICE"
    else:
        if not MENU_ITEMS_MAP:
            response_text = "Desculpe, estou com um problema para acessar nosso cardápio no momento."
        else:
            user_request_normalized = message_text.lower().strip()
            found_item_original_name = None
            possible_matches = []

            if user_request_normalized in MENU_ITEMS_MAP:
                found_item_original_name = MENU_ITEMS_MAP[user_request_normalized]
            else:
                for norm_name, orig_name in MENU_ITEMS_MAP.items():
                    if user_request_normalized in norm_name:
                        possible_matches.append(orig_name)

                if len(possible_matches) == 1:
                    found_item_original_name = possible_matches[0]
                elif len(possible_matches) > 1:
                    matches_text = "\n".join([f"- {match}" for match in possible_matches[:5]])
                    response_text = (
                        f"Encontrei alguns itens parecidos com '{message_text}':\n{matches_text}\n"
                        "Qual deles você gostaria? Por favor, digite o nome completo de um dos itens."
                    )
                    session["previous_response_was_clarification"] = True
                    return response_text

            if found_item_original_name:
                session["order"].append({"name": found_item_original_name, "details": "Item do cardápio"})
                order_summary = "\n".join(
                    [f"- {item['name']} ({item.get('details', 'detalhes pendentes')})" for item in session["order"]])
                response_text = (
                    f"Adicionado: {found_item_original_name}.\n"
                    f"Seu pedido até agora:\n{order_summary}\n\n"
                    "Algo mais? (Digite o item ou 'FINALIZAR PEDIDO')"
                )
            elif not possible_matches:
                response_text = (
                        f"Desculpe, não encontrei '{message_text}' em nosso cardápio. 🤔\n"
                        "Tente novamente ou confira nosso cardápio online.\n\n" +
                        get_first_menu_options("1")
                )
    session["previous_response_was_clarification"] = False
    return response_text

#Buscando informações
def _handle_state_awaiting_info_choice(session, message_text):
    if message_text == "1":
        response_text = config.HORARIO_FUNCIONAMENTO
    elif message_text == "2":
        response_text = config.ENDERECO_PIZZARIA
    elif message_text == "3":
        response_text = config.PROMOCOES_DO_DIA
    elif message_text == "4":  # Voltar
        response_text = get_initial_greeting()
        session["state"] = "AWAITING_INITIAL_CHOICE"
    else:
        response_text = "Opção inválida para Informações. Por favor, digite de 1 a 4."
    return response_text

#Delivery ou retirada
def _handle_state_awaiting_delivery_or_pickup(session, message_text):
    if message_text == "1":
        response_text = "Entendido! Para entrega, informe seu endereço completo (Rua, N°, Bairro, Complemento, Referência):"
        session["delivery_type"] = "delivery"
        session["state"] = "AWAITING_ADDRESS"
    elif message_text == "2":
        response_text = (
            f"Combinado! Retirada em aprox. {config.TEMPO_MEDIO_PREPARO_RETIRADA} min. "
            f"Endereço: {config.ENDERECO_PIZZARIA}. Em nome de quem será a retirada?"
        )
        session["delivery_type"] = "pickup"
        session["state"] = "AWAITING_PICKUP_NAME"
    else:
        response_text = "Opção inválida. Digite 1 para Entrega ou 2 para Retirada."
    return response_text

#Endereço do cliente
def _handle_state_awaiting_address(session, message_text):
    session["address"] = message_text
    session["state"] = "AWAITING_PAYMENT"
    return (
        f"Endereço anotado: {message_text}.\n"
        "Como você gostaria de pagar?\n"
        "1. 💳 Cartão (levamos a maquininha)\n"
        "2. 💰 Dinheiro (Precisa de troco? Para quanto?)\n"
        f"3. 📲 PIX (Chave: {config.PIX_CHAVE}. Envie o comprovante após pagar.)"
    )

#Pagamento
def _handle_state_awaiting_pickup_name(session, message_text):
    session["pickup_name"] = message_text
    session["state"] = "AWAITING_PAYMENT"
    return (
        f"Retirada em nome de: {message_text}.\n"
        "Como você gostaria de pagar?\n"
        "1. 💳 Cartão na retirada\n"
        "2. 💰 Dinheiro na retirada (Precisa de troco? Para quanto?)\n"
        f"3. 📲 PIX (Chave: {config.PIX_CHAVE}. Envie o comprovante após pagar.)"
    )


def _handle_state_awaiting_payment(session, message_text):
    previsao = f"Previsão: {config.TEMPO_MEDIO_ENTREGA if session.get('delivery_type') == 'delivery' else config.TEMPO_MEDIO_PREPARO_RETIRADA} min"
    response_text = "Opção de pagamento inválida. Por favor, escolha 1, 2 ou 3."
    if message_text == "1":
        session["payment_method"] = "Cartão"
        response_text = f"Pagamento com Cartão. Pedido quase pronto! {previsao}."
        session["state"] = "ORDER_COMPLETED"
    elif message_text == "2":
        session["payment_method"] = "Dinheiro"
        response_text = f"Pagamento em Dinheiro. Se precisar de troco, nos avise! Pedido quase pronto! {previsao}."
        session["state"] = "ORDER_COMPLETED"
    elif message_text == "3":
        session["payment_method"] = "PIX"
        response_text = f"Pagamento com PIX. Chave: {config.PIX_CHAVE}. Envie o comprovante. Pedido confirmado após comprovante. {previsao} (após confirmação)."
        session["state"] = "AWAITING_PIX_PROOF"

    if session["state"] == "ORDER_COMPLETED":
        order_summary_final = "\n".join(
            [f"- {item['name']} ({item.get('details', 'sem detalhes')})" for item in session.get("order", [])])
        delivery_info = ""
        if session.get("delivery_type") == "delivery":
            delivery_info = f"Endereço de Entrega: {session.get('address', 'Não informado')}"
        elif session.get("delivery_type") == "pickup":
            delivery_info = f"Retirada em nome de: {session.get('pickup_name', 'Não informado')}"
        response_text += (
            f"\n\n🎉 PEDIDO CONFIRMADO! 🎉\n"
            f"Resumo:\n{order_summary_final}\n"
            f"Pagamento: {session.get('payment_method', 'Não informado')}\n"
            f"{delivery_info}\n"
            f"Obrigado pela preferência, {config.NOME_DA_PIZZARIA} agradece!"
        )
    return response_text

  ###Assume que qualquer mensagem é o comprovante, tratar depois
def _handle_state_awaiting_pix_proof(session, message_text):
    session["state"] = "ORDER_COMPLETED_AFTER_PIX"
    order_summary_final = "\n".join(
        [f"- {item['name']} ({item.get('details', 'sem detalhes')})" for item in session.get("order", [])])
    delivery_info = ""
    if session.get("delivery_type") == "delivery":
        delivery_info = f"Endereço de Entrega: {session.get('address', 'Não informado')}"
    elif session.get("delivery_type") == "pickup":
        delivery_info = f"Retirada em nome de: {session.get('pickup_name', 'Não informado')}"

    return (
        "Comprovante recebido (simulação)! Seu pedido está confirmado e já vai para a produção! Obrigado!\n\n"
        f"🎉 PEDIDO CONFIRMADO! 🎉\n"
        f"Resumo:\n{order_summary_final}\n"
        f"Pagamento: {session.get('payment_method', 'PIX')}\n"
        f"{delivery_info}\n"
        f"Obrigado pela preferência, {config.NOME_DA_PIZZARIA} agradece!"
    )


def _handle_state_handed_off_to_human(session, message_text):
    # O bot geralmente não responde mais aqui, mas pode ter uma mensagem final se necessário
    # ou se o usuário continuar mandando msg antes do humano responder.
    return "Um de nossos atendentes já foi notificado e responderá em breve. Se precisar de mais alguma coisa enquanto espera, pode me dizer."


def _handle_default_state(session, message_text):  # Fallback para estados não mapeados
    print(f"AVISO: Estado não tratado '{session.get('state')}' ou lógica de fallback atingida.")
    session["state"] = "NEW_USER"  # Resetar o estado
    return get_initial_greeting() + "\nParece que nos perdemos um pouco. Vamos recomeçar?"


# --- Função Principal de Lógica do Chatbot (Despachante) ---
def handle_message(user_id, user_name, message_text):
    session = user_sessions.get(user_id, {"state": "NEW_USER", "order": [], "name": user_name,
                                          "previous_response_was_clarification": False})
    current_state = session.get("state", "NEW_USER")

    #print(f"Sessão INICIAL para {user_id} ({user_name}): {session}")
    #print(f"Mensagem recebida: {message_text}, Estado ATUAL: {current_state}")

    # Comandos globais para resetar/ajudar
    if message_text.lower() in ["menu", "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "início", "inicio",
                                "ajuda", "cancelar", "sair"]:
        if current_state not in ["NEW_USER", "AWAITING_INITIAL_CHOICE"]:  # Evita loop de saudação
            print(f"Comando global '{message_text}' detectado. Resetando para o início.")
        current_state = "NEW_USER"  # Força o reset para o handler _handle_state_new_user
        session["state"] = "NEW_USER"  # Atualiza a sessão imediatamente

    # Mapeamento de estados para funções de tratamento
    state_handlers = {
        "NEW_USER": _handle_state_new_user,
        "AWAITING_INITIAL_CHOICE": _handle_state_awaiting_initial_choice,
        "AWAITING_ORDER_DESCRIPTION": _handle_state_awaiting_order_description,
        "AWAITING_INFO_CHOICE": _handle_state_awaiting_info_choice,
        "AWAITING_DELIVERY_OR_PICKUP": _handle_state_awaiting_delivery_or_pickup,
        "AWAITING_ADDRESS": _handle_state_awaiting_address,
        "AWAITING_PICKUP_NAME": _handle_state_awaiting_pickup_name,
        "AWAITING_PAYMENT": _handle_state_awaiting_payment,
        "AWAITING_PIX_PROOF": _handle_state_awaiting_pix_proof,
        "HANDED_OFF_TO_HUMAN": _handle_state_handed_off_to_human,
        # Estados finais como ORDER_COMPLETED geralmente não precisam de handler se o bot não interage mais.
        # Se o usuário mandar msg após ORDER_COMPLETED, ele cairá no _handle_default_state (ou pode criar um handler específico).
    }

    handler_function = state_handlers.get(current_state, _handle_default_state)
    response_text = handler_function(session, message_text)

    user_sessions[user_id] = session
    #print(f"Sessão FINAL para {user_id} ({user_name}): {session}")
    return response_text