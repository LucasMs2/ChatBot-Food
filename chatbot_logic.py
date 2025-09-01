# chatbot_logic.py
import sys
import os
import config


# --- Funções de Carregamento e Configuração ---
def load_menu_from_file(filename="cardapio.txt"):
    menu_map = {}
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_path, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                item_original = line.strip()
                if item_original: menu_map[item_original.lower()] = item_original
        print(f"Cardápio carregado com {len(menu_map)} itens de '{filepath}'.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo do cardápio '{filepath}' não encontrado.")
    return menu_map


MENU_ITEMS_MAP = load_menu_from_file()
MENU_ITEMS_LIST = sorted(list(MENU_ITEMS_MAP.values()))  # Ordena para consistência
PAGE_SIZE = 7  # 7 itens + 3 de navegação = 10 (limite do WhatsApp)
user_sessions = {}


# --- Funções Auxiliares de UI (Interface do Usuário) ---
def _build_menu_sections(session, items, page, page_size):
    total = len(items)
    start = page * page_size
    end = min(start + page_size, total)
    page_items = items[start:end]
    rows = [{"id": f"add|{name}", "title": name} for name in page_items]

    nav_rows = []
    if page > 0: nav_rows.append({"id": "prev_items", "title": "⬅️ Página Anterior"})
    if end < total: nav_rows.append({"id": "next_items", "title": "➡️ Próxima Página"})
    if session.get("order"): nav_rows.append({"id": "finish_order", "title": "✅ Finalizar Pedido"})
    nav_rows.append({"id": "cancel_order", "title": "❌ Cancelar e Voltar"})

    sections = []
    order_summary = "\n".join([f"  - {item['name']}" for item in session.get("order", [])])
    if order_summary:
        sections.append({"title": f"Seu Carrinho ({len(session['order'])} itens)", "rows": [
            {"id": "noop", "title": order_summary, "description": "Clique em Finalizar Pedido abaixo"}]})

    if rows: sections.append({"title": f"Cardápio (Página {page + 1})", "rows": rows})
    sections.append({"title": "Ações", "rows": nav_rows})
    return sections


def _list_of_menu(session, body_text="Escolha um item do cardápio:"):
    session.setdefault("menu_page", 0)
    sections = _build_menu_sections(session, MENU_ITEMS_LIST, session["menu_page"], PAGE_SIZE)
    return {"text": body_text, "interactive": {"type": "list", "body": {"text": body_text},
                                               "action": {"button": "🍕 Ver Cardápio", "sections": sections}}}


def _get_next_step_buttons(include_back=False):
    buttons = [
        {"type": "reply", "reply": {"id": "menu_order", "title": "🍕 Fazer Pedido"}},
        {"type": "reply", "reply": {"id": "menu_info", "title": "ℹ️ Informações"}},
        {"type": "reply", "reply": {"id": "handed_off_to_human", "title": "🗣️ Falar com Atendente"}}
    ]
    if include_back: buttons.append({"type": "reply", "reply": {"id": "back", "title": "↩️ Voltar"}})
    return {"type": "button", "action": {"buttons": buttons}}


def _get_payment_buttons():
    return {"type": "button", "action": {"buttons": [
        {"type": "reply", "reply": {"id": "card_payment", "title": "💳 Cartão"}},
        {"type": "reply", "reply": {"id": "cash_payment", "title": "💰 Dinheiro"}},
        {"type": "reply", "reply": {"id": "pix_payment", "title": "📲 PIX"}},
        {"type": "reply", "reply": {"id": "back_to_order_browsing", "title": "↩️ Voltar ao Cardápio"}}
    ]}}


def _get_final_summary(session):
    order_summary_final = "\n".join([f"- {item['name']}" for item in session.get("order", [])])
    delivery_info = ""
    if session.get("delivery_type") == "delivery":
        delivery_info = f"Endereço de Entrega: {session.get('address', 'Não informado')}"
    elif session.get("delivery_type") == "pickup":
        delivery_info = f"Retirada em nome de: {session.get('pickup_name', 'Não informado')}"
    return (
        f"\n\n🎉 PEDIDO CONFIRMADO! 🎉\nResumo:\n{order_summary_final}\nPagamento: {session.get('payment_method', 'Não informado')}\n{delivery_info}\nObrigado pela preferência, {config.NOME_DA_PIZZARIA} agradece!")


# --- Handlers de Estado ---
def _handle_state_new_user(session, _):
    session["state"] = "AWAITING_INITIAL_CHOICE";
    session["order"] = [];
    session["menu_page"] = 0
    return {"text": f"Olá! 👋 Bem-vindo(a) à {config.NOME_DA_PIZZARIA}! Como posso te ajudar?",
            "interactive": _get_next_step_buttons()}


def _handle_state_awaiting_initial_choice(session, message_text):
    if message_text == "menu_order":
        session["state"] = "AWAITING_ORDER_BROWSING";
        return _list_of_menu(session, "Ótima escolha! 😊 Selecione no cardápio:")
    elif message_text == "menu_info":
        session["state"] = "AWAITING_INFO_CHOICE";
        return {"text": "Claro! O que você gostaria de saber?", "interactive":
            {"type": "list",
             "action": {"button": "Ver Opções 📝",
                        "sections": [{
                                         "title": "Nossas Informações",
                                         "rows": [{
                                                      "id": "opening_info",
                                                      "title": "⏰ Horário"},
                                                  {
                                                      "id": "address_info",
                                                      "title": "📍 Endereço"},
                                                  {
                                                      "id": "promo_info",
                                                      "title": "🎉 Promoções"},
                                                  {
                                                      "id": "back",
                                                       "title": "↩️ Voltar"}]}]}}}

    elif message_text == "handed_off_to_human":
        session["state"] = "HANDED_OFF_TO_HUMAN"
        return "Entendido! Vou te transferir para um de nossos atendentes. 😊"
    else:
        return {"text": "Não entendi. Use os botões abaixo 👇", "interactive": _get_next_step_buttons(True)}


def _handle_state_order_browsing(session, message_text):
    if message_text.startswith("add|"):
        item = message_text.split("add|", 1)[1];
        session.setdefault("order", []).append({"name": item});
        return _list_of_menu(session, f"✅ {item} adicionado ao carrinho!")
    if message_text == "next_items":
        session["menu_page"] += 1;
        return _list_of_menu(session, "Próxima página do cardápio:")
    if message_text == "prev_items":
        session["menu_page"] = max(0, session["menu_page"] - 1);
        return _list_of_menu(session, "Página anterior do cardápio:")
    if message_text == "finish_order":
        if not session.get("order"): return _list_of_menu(session, "Seu carrinho está vazio. Adicione algo primeiro.")
        session["state"] = "AWAITING_DELIVERY_OR_PICKUP";
        resumo = "\n".join([f"- {i['name']}" for i in session["order"]])
        return {"text": f"Perfeito! Seu pedido:\n{resumo}\n\nAgora escolha a forma de receber:",
                "interactive": {"type": "button", "action": {
                    "buttons": [{"type": "reply", "reply": {"id": "delivery_option", "title": "🛵 Entrega"}},
                                {"type": "reply", "reply": {"id": "pickup_option", "title": "🚶 Retirada"}},
                                {"type": "reply", "reply": {"id": "back", "title": "↩️ Voltar"}}]}}}
    if message_text == "cancel_order" or message_text == "back": return _handle_state_new_user(session, "cancel")
    return _list_of_menu(session, "Não entendi. Escolha no cardápio:")


def _handle_state_awaiting_info_choice(session, message_text):
    if message_text == "opening_info":
        response_text = config.HORARIO_FUNCIONAMENTO
    elif message_text == "address_info":
        response_text = config.ENDERECO_PIZZARIA
    elif message_text == "promo_info":
        response_text = config.PROMOCOES_DO_DIA
    else:
        return _handle_state_new_user(session, "back")
    return {"text": response_text + "\n\nPosso ajudar com mais algo?", "interactive": _get_next_step_buttons(True)}


def _handle_state_awaiting_delivery_or_pickup(session, message_text):
    if message_text == "delivery_option":
        session["state"] = "AWAITING_ADDRESS"; return "Entendido! Qual o seu endereço completo para entrega?"
    elif message_text == "pickup_option":
        session["state"] = "AWAITING_PICKUP_NAME"; return f"Combinado! Em nome de quem será a retirada?"
    elif message_text == "back":
        session["state"] = "AWAITING_ORDER_BROWSING"; return _list_of_menu(session,
                                                                           "Voltamos ao cardápio. Pode continuar escolhendo.")
    else:
        return {"text": "Opção inválida.",
                "interactive": session.get("last_interactive")}  # Reenvia a última interativa


def _handle_state_awaiting_address(session, message_text):
    session["address"] = message_text;
    session["state"] = "AWAITING_PAYMENT";
    session["delivery_type"] = "delivery"
    return {"text": f"Endereço anotado: {message_text}.\n\nComo gostaria de pagar?",
            "interactive": _get_payment_buttons()}


def _handle_state_awaiting_pickup_name(session, message_text):
    session["pickup_name"] = message_text;
    session["state"] = "AWAITING_PAYMENT";
    session["delivery_type"] = "pickup"
    return {"text": f"Retirada em nome de: {message_text}.\n\nComo gostaria de pagar?",
            "interactive": _get_payment_buttons()}


def _handle_state_awaiting_payment(session, message_text):
    if message_text == "back_to_order_browsing": session["state"] = "AWAITING_ORDER_BROWSING"; return _list_of_menu(
        session, "Sem problemas, voltamos ao cardápio.")

    previsao = f"Previsão de chegada: {config.TEMPO_MEDIO_ENTREGA if session.get('delivery_type') == 'delivery' else config.TEMPO_MEDIO_PREPARO_RETIRADA} min"
    response_text = "Opção de pagamento inválida."
    if message_text == "card_payment":
        session["payment_method"] = "Cartão"; session[
            "state"] = "ORDER_COMPLETED"; response_text = f"Pagamento com Cartão. {previsao}."
    elif message_text == "cash_payment":
        session["payment_method"] = "Dinheiro"; session[
            "state"] = "ORDER_COMPLETED"; response_text = f"Pagamento em Dinheiro. {previsao}."
    elif message_text == "pix_payment":
        session["payment_method"] = "PIX"; session[
            "state"] = "AWAITING_PIX_PROOF"; response_text = f"PIX. Chave: {config.PIX_CHAVE}. {previsao} (após comprovante)."

    if session["state"] == "ORDER_COMPLETED": response_text += _get_final_summary(session)
    return {"text": response_text, "interactive": _get_next_step_buttons()} if session[
                                                                                   "state"] == "ORDER_COMPLETED" else response_text


def _handle_state_awaiting_pix_proof(session, message_text):
    session["state"] = "ORDER_COMPLETED";
    return {"text": "Comprovante recebido (simulação)!" + _get_final_summary(session),
            "interactive": _get_next_step_buttons()}


def _handle_state_handed_off_to_human(session, _):
    return "Um atendente já foi notificado e responderá em breve."


# --- Função Principal (Despachante) ---
def handle_message(user_id, user_name, message_text):
    session = user_sessions.setdefault(user_id, {"state": "NEW_USER"})
    if "name" not in session: session["name"] = user_name

    # Comandos globais que resetam o fluxo
    if message_text in ["back", "cancel_order", "oi", "ola", "olá", "menu"]:
        session["state"] = "NEW_USER"

    state = session.get("state", "NEW_USER")

    state_handlers = {
        "NEW_USER": _handle_state_new_user, "AWAITING_INITIAL_CHOICE": _handle_state_awaiting_initial_choice,
        "AWAITING_ORDER_BROWSING": _handle_state_order_browsing,
        "AWAITING_INFO_CHOICE": _handle_state_awaiting_info_choice,
        "AWAITING_DELIVERY_OR_PICKUP": _handle_state_awaiting_delivery_or_pickup,
        "AWAITING_ADDRESS": _handle_state_awaiting_address,
        "AWAITING_PICKUP_NAME": _handle_state_awaiting_pickup_name, "AWAITING_PAYMENT": _handle_state_awaiting_payment,
        "AWAITING_PIX_PROOF": _handle_state_awaiting_pix_proof, "HANDED_OFF_TO_HUMAN": _handle_state_handed_off_to_human
    }

    handler = state_handlers.get(state, _handle_state_new_user)
    response = handler(session, message_text)

    if isinstance(response, dict) and response.get("interactive"):
        session["last_interactive"] = response["interactive"]  # Salva a última interativa para reenvio em caso de erro

    user_sessions[user_id] = session
    return response