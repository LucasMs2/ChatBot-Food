import chatbot_logic # Importa a lógica e as sessões

def terminal_test_chat():
    """
    Permite testar a lógica do chatbot interagindo via terminal.
    """
    print("--- Iniciando Teste do Chatbot no Terminal ---")
    print("Você pode começar digitando 'oi', 'menu' ou uma saudação.")
    print("Digite 'sair' a qualquer momento para encerrar o teste.")
    print("----------------------------------------------")

    test_user_id = "terminal_user_001"
    test_user_name = "Cliente Terminal"

    # Garante que a sessão de teste comece limpa
    if test_user_id in chatbot_logic.user_sessions:
        del chatbot_logic.user_sessions[test_user_id]

    while True:
        user_input = input(f"\n[{test_user_name}]: ")

        if user_input.lower() == 'sair':
            print("\n--- Teste encerrado pelo usuário ---")
            if test_user_id in chatbot_logic.user_sessions:
                del chatbot_logic.user_sessions[test_user_id] # Limpa a sessão ao sair
            break

        bot_response = chatbot_logic.handle_message(test_user_id, test_user_name, user_input)
        print(f"[BOT]: {bot_response}")

if __name__ == '__main__':
    # Esta parte permite rodar o testador diretamente
    terminal_test_chat()